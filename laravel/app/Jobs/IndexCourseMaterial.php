<?php

namespace App\Jobs;

use App\Models\CourseMaterial;
use App\Models\CourseMaterialChunk;
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

    public int $courseMaterialId;

    public function __construct(int $courseMaterialId)
    {
        $this->courseMaterialId = $courseMaterialId;
    }

    public function handle(): void
    {
        $material = CourseMaterial::find($this->courseMaterialId);

        if (!$material) {
            Log::error("IndexCourseMaterial: material {$this->courseMaterialId} not found, cancelling.");
            return;
        }

        $material->update(['status' => CourseMaterial::STATUS_INDEXING, 'error_message' => null]);

        try {
            $startTime = microtime(true);
            if ($material->ocr_enabled) {
                if ($material->extraction_engine === 'textract') {
                    $this->indexWithAWSTextractOCR($material);
                } elseif ($material->extraction_engine === 'tesseract') {
                    $this->indexWithTesseractOCR($material);
                }
            } else {
                $this->indexWithoutOCR($material);
            }
            $processingTime = (int) round(microtime(true) - $startTime);
            $material->update(['processing_time_seconds' => $processingTime]);
        } catch (Throwable $exception) {
            Log::error("IndexCourseMaterial failed for material {$material->id}: " . $exception->getMessage());
            $material->update([
                'status' => CourseMaterial::STATUS_FAILED,
                'error_message' => mb_substr($exception->getMessage(), 0, 1000),
            ]);
            throw $exception;
        }
    }

    private function indexWithoutOCR(CourseMaterial $material): void
    {
        $rows = [];
        $pageNumber = 0;
        foreach ($this->parsePages($material) as $page) {
            $pageNumber++;
            $text = trim($page->getText());

            if ($text !== '') {
                $rows[] = $this->courseMaterialChunkDBRow($material, $pageNumber, $text);
            }
        }

        $this->saveTextChunks($material, $rows);
    }

    private function indexWithTesseractOCR(CourseMaterial $material): void
    {
        $this->assertEnglishOCRDataAvailable();

        $absolutePath = Storage::disk('local')->path($material->file_path);

        $rows = [];
        $pageNumber = 0;
        foreach ($this->parsePages($material) as $page) {
            $pageNumber++;
            $text = trim($page->getText());

            if (mb_strlen($text) <= $material->ocr_threshold) {
                // High DPI needed for OCR, otherwise smaller characters get mixed up
                $pngPath = PdfPageRenderer::pdfToImage($absolutePath, $pageNumber, dpi: 300);
                try {
                    $text = trim((new TesseractOCR($pngPath))->run());
                } finally {
                    @unlink($pngPath);
                }
            }

            if ($text !== '') {
                $rows[] = $this->courseMaterialChunkDBRow($material, $pageNumber, $text);
            }
        }

        $this->saveTextChunks($material, $rows);
    }

    private function parsePages(CourseMaterial $material): array
    {
        ini_set('memory_limit', '1024M');
        set_time_limit(0);

        $config = new PdfParserConfig();
        $config->setRetainImageContent(false);

        $pages = (new Parser([], $config))
            ->parseFile(Storage::disk('local')->path($material->file_path))
            ->getPages();

        $material->update(['page_count' => count($pages)]);

        return $pages;
    }

    private function courseMaterialChunkDBRow(CourseMaterial $material, int $pageNumber, string $text): array
    {
        return [
            'course_material_id' => $material->id,
            'page_number' => $pageNumber,
            'chunk_index' => 0,
            'content' => $text,
            'created_at' => now(),
            'updated_at' => now(),
        ];
    }

    private function saveTextChunks(CourseMaterial $material, array $rows): void
    {
        foreach (array_chunk($rows, 100) as $batch) {
            CourseMaterialChunk::insert($batch);
        }

        $material->update(['status' => CourseMaterial::STATUS_INDEXED]);
    }

    private function indexWithAWSTextractOCR(CourseMaterial $material): void
    {
        $absolutePath = Storage::disk('local')->path($material->file_path);
        $fileBytes = file_get_contents($absolutePath);

        $response = Http::timeout(300)->post(config('services.text_extraction.base_url') . '/extract', [
            'file' => base64_encode($fileBytes),
        ]);

        $response->throw();
        $data = $response->json();
        $pages = $data['pages'] ?? [];

        $material->update(['page_count' => count($pages)]);

        $rows = [];
        foreach ($pages as $page) {
            if (!empty($page['content'])) {
                $rows[] = $this->courseMaterialChunkDBRow($material, $page['page_number'], $page['content']);
            }
        }

        $this->saveTextChunks($material, $rows);
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
