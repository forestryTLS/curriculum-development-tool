<?php

namespace App\Http\Controllers;

use App\Jobs\IndexCourseMaterial;
use App\Models\CourseMaterial;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Illuminate\View\View;
use App\Support\PdfPageRenderer;
use Symfony\Component\HttpFoundation\StreamedResponse;

class CourseMaterialController extends Controller
{
    public function __construct()
    {
        $this->middleware(['auth', 'verified']);
        $this->middleware('hasAccess');
    }

    public function store(Request $request, $course_id): RedirectResponse
    {
        $this->assertIsEditor((int) $course_id);

        $request->validate([
            'file' => ['required', 'file', 'mimes:pdf', 'max:51200'],
            'ocr_enabled' => ['sometimes', 'boolean'],
            'extraction_engine' => ['required_if:ocr_enabled,1', 'in:tesseract,textract'],
            'ocr_threshold' => ['sometimes', 'integer', 'min:0', 'max:10000'],
        ]);

        $uploaded = $request->file('file');
        $diskPath = 'course-materials/' . $course_id . '/' . Str::uuid()->toString() . '.pdf';

        Storage::disk('local')->put($diskPath, file_get_contents($uploaded->getRealPath()));

        $material = CourseMaterial::create([
            'course_id' => $course_id,
            'uploaded_by' => Auth::id(),
            'file_name' => $uploaded->getClientOriginalName(),
            'file_path' => $diskPath,
            'mime_type' => $uploaded->getClientMimeType() ?: 'application/pdf',
            'file_size' => $uploaded->getSize(),
            'status' => CourseMaterial::STATUS_PENDING,
            'extraction_engine' => $request->input('extraction_engine', 'tesseract'),
            'ocr_enabled' => $request->boolean('ocr_enabled'),
            'ocr_threshold' => $request->boolean('ocr_enabled') ? (int) $request->input('ocr_threshold', 0) : 0,
        ]);

        IndexCourseMaterial::dispatch($material->id);

        return redirect()
            ->route('course.coverageAnalysis', ['course' => $course_id])
            ->with('success', 'Material uploaded. Indexing in the background.');
    }

    public function searchCourse(Request $request, $course_id): View|RedirectResponse
    {
        $limit = 5; // TODO: Make this dynamic

        $this->assertIsEditor((int) $course_id);

        $searchTerm = trim($request->input('query', ''));

        if ($searchTerm === '') {
            return redirect()->route('course.coverageAnalysis', ['course' => $course_id]);
        }

        $results = DB::table('course_material_chunks as c')
            ->join('course_materials as m', 'm.id', '=', 'c.course_material_id')
            ->where('m.course_id', $course_id)
            ->whereRaw("c.content_tsv @@ plainto_tsquery('english', ?)", [$searchTerm])
            ->selectRaw("
                m.id as material_id,
                m.file_name,
                c.page_number,
                ts_rank(c.content_tsv, plainto_tsquery('english', ?)) as rank,
                ts_headline('english', c.content, plainto_tsquery('english', ?),
                    'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=5, MaxWords=25') as snippet
            ", [$searchTerm, $searchTerm])
            ->orderByDesc('rank')
            ->limit($limit)
            ->get();

        return redirect()
            ->route('course.coverageAnalysis', ['course' => $course_id])
            ->with('search_results', $results)
            ->with('search_query', $searchTerm);
    }

    public function searchProgram(Request $request, $program_id): RedirectResponse
    {
        $searchTerm = trim($request->input('query', ''));

        if ($searchTerm === '') {
            return redirect()->route('program.coverageAnalysis', ['program' => $program_id]);
        }

        $courseIds = DB::table('course_programs')
            ->where('program_id', $program_id)
            ->pluck('course_id');

        $results = DB::table('course_material_chunks as c')
            ->join('course_materials as m', 'm.id', '=', 'c.course_material_id')
            ->whereIn('m.course_id', $courseIds)
            ->whereRaw("c.content_tsv @@ plainto_tsquery('english', ?)", [$searchTerm])
            ->selectRaw("
                m.id as material_id,
                m.file_name,
                m.course_id,
                c.page_number,
                ts_rank(c.content_tsv, plainto_tsquery('english', ?)) as rank,
                ts_headline('english', c.content, plainto_tsquery('english', ?),
                    'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=5, MaxWords=25') as snippet
            ", [$searchTerm, $searchTerm])
            ->orderByDesc('rank')
            ->limit(5)
            ->get();

        return redirect()
            ->route('program.coverageAnalysis', ['program' => $program_id])
            ->with('search_results', $results)
            ->with('search_query', $searchTerm);
    }

    public function destroy($course_id, $material_id): RedirectResponse
    {
        $this->assertIsEditor((int) $course_id);

        $material = CourseMaterial::where('id', $material_id)
            ->where('course_id', $course_id)
            ->firstOrFail();

        if (Storage::disk('local')->exists($material->file_path)) {
            Storage::disk('local')->delete($material->file_path);
        }
        $material->delete();

        return redirect()
            ->route('course.coverageAnalysis', ['course' => $course_id])
            ->with('success', 'Material deleted.');
    }

    public function download($course_id, $material_id): StreamedResponse
    {
        $material = CourseMaterial::where('id', $material_id)
            ->where('course_id', $course_id)
            ->firstOrFail();

        abort_unless(Storage::disk('local')->exists($material->file_path), 404);

        return Storage::disk('local')->download($material->file_path, $material->file_name);
    }

    public function view($course_id, $material_id): StreamedResponse
    {
        $material = CourseMaterial::where('id', $material_id)
            ->where('course_id', $course_id)
            ->firstOrFail();

        abort_unless(Storage::disk('local')->exists($material->file_path), 404);

        return Storage::disk('local')->response($material->file_path, $material->file_name);
    }

    public function thumbnail(Request $request, $course_id, $material_id): Response
    {
        // If no page number is given in $request, just outputs first page

        $material = CourseMaterial::where('id', $material_id)
            ->where('course_id', $course_id)
            ->firstOrFail();

        $absolutePath = Storage::disk('local')->path($material->file_path);
        abort_unless(file_exists($absolutePath), 404);

        $page = $request->validate(['page' => ['sometimes', 'integer', 'min:1', 'max:' . $material->page_count]])['page'] ?? 1;

        $pngPath = PdfPageRenderer::pdfToImage($absolutePath, $page, 96);
        try {
            return response(file_get_contents($pngPath), 200)
                ->header('Content-Type', 'image/png');
        } finally {
            @unlink($pngPath);
        }
    }

    private function assertIsEditor(int $course_id): void
    {
        $permission = User::find(Auth::id())?->effectivePermissionForCourse($course_id) ?? 0;
        abort_unless(in_array($permission, [1, 2], true), 403, 'Editor access required.');
    }
}
