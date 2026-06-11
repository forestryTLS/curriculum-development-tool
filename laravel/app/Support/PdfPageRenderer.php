<?php

namespace App\Support;

use Illuminate\Support\Facades\Process;

class PdfPageRenderer
{
    public static function pdfToImage(string $pdfPath, int $page, int $dpi = 96): string
    {
        $tmpBase = sys_get_temp_dir() . DIRECTORY_SEPARATOR . uniqid('pdf_page_', true);

        $result = Process::run([
            'pdftoppm', '-png',
            '-f', (string) $page,
            '-l', (string) $page,
            '-r', (string) $dpi,
            $pdfPath,
            $tmpBase,
        ]);

        if ($result->failed()) {
            throw new \RuntimeException("pdftoppm failed for page {$page}: " . $result->errorOutput());
        }

        $files = glob($tmpBase . '*.png');
        if (empty($files)) {
            throw new \RuntimeException("pdftoppm produced no output for page {$page}.");
        }

        return $files[0];
    }
}
