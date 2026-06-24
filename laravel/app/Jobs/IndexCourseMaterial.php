<?php

namespace App\Jobs;

use App\Models\CourseMaterialChunk;
use App\Models\CourseMaterialFile;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Throwable;
use Smalot\PdfParser\Config as PdfParserConfig;
use Smalot\PdfParser\Parser;
use App\Support\PdfPageRenderer;
use thiagoalessio\TesseractOCR\TesseractOCR;


class IndexCourseMaterial implements ShouldQueue
{
    // 'Chunk' here currently means a whole page, but we can more finely index later

    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $timeout = 1800;
    public int $tries = 1;

    public int $courseMaterialFileId;

    public function __construct(int $courseMaterialFileId)
    {
        $this->courseMaterialFileId = $courseMaterialFileId;
    }

    public function handle(): void
    {
        $file = CourseMaterialFile::find($this->courseMaterialFileId);

        if (!$file) {
            Log::error("IndexCourseMaterial: file {$this->courseMaterialFileId} not found, cancelling.");
            return;
        }

        $file->update(['status' => CourseMaterialFile::STATUS_INDEXING, 'error_message' => null]);

        try {
            $startTime = microtime(true);
            if ($file->ocr_enabled) {
                if ($file->extraction_engine === 'textract') {
                    $this->indexWithAWSTextractOCR($file);
                } elseif ($file->extraction_engine === 'tesseract') {
                    $this->indexWithTesseractOCR($file);
                }
            } else {
                $this->indexWithoutOCR($file);
            }
            $processingTime = (int) round(microtime(true) - $startTime);
            $file->update(['processing_time_seconds' => $processingTime]);
        } catch (Throwable $exception) {
            Log::error("IndexCourseMaterial failed for file {$file->course_material_file_id}: " . $exception->getMessage());
            $file->update([
                'status' => CourseMaterialFile::STATUS_FAILED,
                'error_message' => mb_substr($exception->getMessage(), 0, 1000),
            ]);
            throw $exception;
        }
    }

    private function indexWithoutOCR(CourseMaterialFile $file): void
    {
        $rows = [];
        $pageNumber = 0;
        foreach ($this->parsePages($file) as $page) {
            $pageNumber++;
            $text = trim($page->getText());

            if ($text !== '') {
                $rows[] = $this->chunkDBRow($file, $pageNumber, $text);
            }
        }

        $this->saveTextChunks($file, $rows);
    }

    private function indexWithTesseractOCR(CourseMaterialFile $file): void
    {
        $this->assertEnglishOCRDataAvailable();

        $absolutePath = Storage::disk('local')->path($file->file_path);

        $rows = [];
        $pageNumber = 0;
        foreach ($this->parsePages($file) as $page) {
            $pageNumber++;
            $text = trim($page->getText());

            if (mb_strlen($text) <= $file->ocr_threshold) {
                // High DPI needed for OCR, otherwise smaller characters get mixed up
                $pngPath = PdfPageRenderer::pdfToImage($absolutePath, $pageNumber, dpi: 300);
                try {
                    $text = trim((new TesseractOCR($pngPath))->run());
                } finally {
                    @unlink($pngPath);
                }
            }

            if ($text !== '') {
                $rows[] = $this->chunkDBRow($file, $pageNumber, $text);
            }
        }

        $this->saveTextChunks($file, $rows);
    }

    private function parsePages(CourseMaterialFile $file): array
    {
        ini_set('memory_limit', '1024M');
        set_time_limit(0);

        $config = new PdfParserConfig();
        $config->setRetainImageContent(false);

        $pages = (new Parser([], $config))
            ->parseFile(Storage::disk('local')->path($file->file_path))
            ->getPages();

        $file->update(['page_count' => count($pages)]);

        return $pages;
    }

    private function chunkDBRow(CourseMaterialFile $file, int $pageNumber, string $text): array
    {
        return [
            'course_material_file_id' => $file->course_material_file_id,
            'page_number' => $pageNumber,
            'chunk_index' => 0,
            'content' => $text,
            'created_at' => now(),
            'updated_at' => now(),
        ];
    }

    private function saveTextChunks(CourseMaterialFile $file, array $rows): void
    {
        foreach (array_chunk($rows, 100) as $batch) {
            CourseMaterialChunk::insert($batch);
        }

        $file->update(['status' => CourseMaterialFile::STATUS_INDEXED]);
    }

    private function indexWithAWSTextractOCR(CourseMaterialFile $file): void
    {
        $absolutePath = Storage::disk('local')->path($file->file_path);
        $fileBytes = file_get_contents($absolutePath);

        $response = Http::timeout(300)->post(config('services.text_extraction.base_url') . '/extract', [
            'file' => base64_encode($fileBytes),
        ]);

        $response->throw();
        $data = $response->json();
        $pages = $data['pages'] ?? [];

        $file->update(['page_count' => count($pages)]);

        $rows = [];
        foreach ($pages as $page) {
            if (!empty($page['content'])) {
                $rows[] = $this->chunkDBRow($file, $page['page_number'], $page['content']);
            }
        }

        $this->saveTextChunks($file, $rows);
    }

    private function assertEnglishOCRDataAvailable(): void
    {
        exec('tesseract --list-langs 2>&1', $langOutput, $langCode);
        $langs = $langCode === 0 ? array_map('trim', $langOutput) : [];
        if (!in_array('eng', $langs, true)) {
            throw new \RuntimeException(
                "Tesseract OCR is installed but English language data for it isn't. "
                . "See docs/Setup.md for instructions."
            );
        }
    }
}
