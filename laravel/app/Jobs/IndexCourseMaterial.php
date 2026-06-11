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
use Smalot\PdfParser\Config as PdfParserConfig;
use Smalot\PdfParser\Parser;
use App\Support\PdfPageRenderer;
use thiagoalessio\TesseractOCR\TesseractOCR;

class IndexCourseMaterial implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $timeout = 1800;
    public int $tries = 1;

    public function __construct(public int $courseMaterialId)
    {
    }

    public function handle(): void
    {
        $material = CourseMaterial::find($this->courseMaterialId);

        if (!$material) {
            Log::warning("IndexCourseMaterial: material {$this->courseMaterialId} not found, skipping.");
            return;
        }

        $material->update(['status' => CourseMaterial::STATUS_INDEXING, 'error_message' => null]);

        try {
            $startTime = microtime(true);
            if ($material->extraction_engine === 'textract') {
                $this->indexWithTextract($material);
            } else {
                $this->indexWithLocalPipeline($material);
            }
            $processingTime = (int) round(microtime(true) - $startTime);
            $material->update(['processing_time_seconds' => $processingTime]);
        } catch (\Throwable $e) {
            Log::error("IndexCourseMaterial failed for material {$material->id}: " . $e->getMessage());
            $material->update([
                'status' => CourseMaterial::STATUS_FAILED,
                'error_message' => mb_substr($e->getMessage(), 0, 1000),
            ]);
            throw $e;
        }
    }

    private function indexWithLocalPipeline(CourseMaterial $material): void
    {
        ini_set('memory_limit', '1024M');
        set_time_limit(0);

        if ($material->ocr_enabled) {
            $this->assertOcrBinariesAvailable();
        }

        $absolutePath = Storage::disk('local')->path($material->file_path);

        $config = new PdfParserConfig();
        $config->setRetainImageContent(false);

        $parser = new Parser([], $config);
        $pdf = $parser->parseFile($absolutePath);
        $pages = $pdf->getPages();

        $material->update([
            'page_count' => count($pages),
            'pages_processed' => 0,
        ]);

        $rows = [];
        $pageNumber = 0;
        foreach ($pages as $page) {
            $pageNumber++;
            $text = trim($page->getText());

            if ($material->ocr_enabled && mb_strlen($text) <= $material->ocr_threshold) {
                $text = trim($this->ocrPage($absolutePath, $pageNumber));
            }

            if ($text !== '') {
                $rows[] = [
                    'course_material_id' => $material->id,
                    'page_number' => $pageNumber,
                    'chunk_index' => 0,
                    'content' => $text,
                    'created_at' => now(),
                    'updated_at' => now(),
                ];
            }
        }

        if (!empty($rows)) {
            foreach (array_chunk($rows, 100) as $batch) {
                CourseMaterialChunk::insert($batch);
            }
        }

        $material->update([
            'status' => CourseMaterial::STATUS_INDEXED,
            'page_count' => $pageNumber,
        ]);
    }

    private function indexWithTextract(CourseMaterial $material): void
    {
        $absolutePath = Storage::disk('local')->path($material->file_path);
        $fileBytes = file_get_contents($absolutePath);

        $response = Http::timeout(300)->post(config('services.text_extraction.url') . '/extract', [
            'file' => base64_encode($fileBytes),
        ]);

        $response->throw();
        $data = $response->json();
        $pages = $data['pages'] ?? [];

        $rows = [];
        foreach ($pages as $page) {
            if (!empty($page['content'])) {
                $rows[] = [
                    'course_material_id' => $material->id,
                    'page_number' => $page['page_number'],
                    'chunk_index' => 0,
                    'content' => $page['content'],
                    'created_at' => now(),
                    'updated_at' => now(),
                ];
            }
        }

        if (!empty($rows)) {
            foreach (array_chunk($rows, 100) as $batch) {
                CourseMaterialChunk::insert($batch);
            }
        }

        $material->update([
            'status' => CourseMaterial::STATUS_INDEXED,
            'page_count' => count($pages),
        ]);
    }

    private function ocrPage(string $pdfPath, int $pageNumber): string
    {
        // For OCR, we want a high DPI, otherwise Tesseract tends to mix up characters.
        $pngPath = PdfPageRenderer::pdfToImage($pdfPath, $pageNumber, dpi: 300);
        try {
            return (new TesseractOCR($pngPath))->run();
        } finally {
            @unlink($pngPath);
        }
    }

    private function assertOcrBinariesAvailable(): void
    {
        $check = function (string $command, string $name, string $installHint): void {
            exec($command . ' 2>&1', $output, $code);
            if ($code !== 0) {
                throw new \RuntimeException(
                    "OCR is enabled but the '{$name}' binary is not available on PATH. "
                    . "Install it and restart the queue worker. {$installHint} "
                    . "See docs/Setup.md for full instructions."
                );
            }
        };

        $check('pdftoppm -v', 'pdftoppm', 'Make sure `poppler-utils` is installed.');
        $check('tesseract --version', 'tesseract', 'Make sure `tesseract` is installed');

        exec('tesseract --list-langs 2>&1', $langOutput, $langCode);
        $langs = $langCode === 0 ? array_map('trim', $langOutput) : [];
        if (!in_array('eng', $langs, true)) {
            throw new \RuntimeException(
                "OCR is enabled but Tesseract's English language data (eng.traineddata) is not installed. "
                . "Download it into your Tesseract installation's tessdata directory. "
                . "See docs/Setup.md for instructions."
            );
        }
    }
}
