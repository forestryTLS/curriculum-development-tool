<?php

namespace App\Support;

use Illuminate\Support\Facades\Process;

class PdfPageRenderer
{
    /* The code here is inspired by the approach in this article:
        https://medium.com/@boisdecerf/pdftoppm-this-underrated-linux-tool-506f13d4b953
        it's a system CLI tool, which PHP calls.

        The jamesyapkm/poppler-php package does the same thing but, is quite old and uses exec().
        This could be a security risk.
        Here, the same thing is done with Laravel's Process facade, which is safer.
    */

    public static function pdfToImage(string $pdfPath, int $page, int $dpi = 96): string
    {
        // Basically creates a temporary file for the output image,
        // in the format systempdir/pdf_page_someuniqueid
        $tmpBase = sys_get_temp_dir() . DIRECTORY_SEPARATOR . uniqid('pdf_page_', true);

        // This then appends the page number and extension,
        // so the final output is something like systemtempdir/pdf_page_someuniqueid-1.png
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
