<?php

namespace App\Jobs;

use App\Models\CourseMaterial;
use App\Models\CourseMaterialChunk;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Smalot\PdfParser\Config as PdfParserConfig;
use Smalot\PdfParser\Parser;

class IndexCourseMaterial implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $timeout = 600;
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

        ini_set('memory_limit', '1024M');

        $material->update(['status' => CourseMaterial::STATUS_INDEXING, 'error_message' => null]);

        try {
            $absolutePath = Storage::disk('local')->path($material->file_path);

            $config = new PdfParserConfig();
            $config->setRetainImageContent(false);

            $parser = new Parser([], $config);
            $pdf = $parser->parseFile($absolutePath);
            $pages = $pdf->getPages();

            $rows = [];
            $pageNumber = 0;
            foreach ($pages as $page) {
                $pageNumber++;
                $text = trim($page->getText());
                if ($text === '') {
                    continue;
                }

                $rows[] = [
                    'course_material_id' => $material->id,
                    'page_number' => $pageNumber,
                    'chunk_index' => 0,
                    'content' => $text,
                    'created_at' => now(),
                    'updated_at' => now(),
                ];
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
        } catch (\Throwable $e) {
            Log::error("IndexCourseMaterial failed for material {$material->id}: " . $e->getMessage());
            $material->update([
                'status' => CourseMaterial::STATUS_FAILED,
                'error_message' => mb_substr($e->getMessage(), 0, 1000),
            ]);
            throw $e;
        }
    }
}
