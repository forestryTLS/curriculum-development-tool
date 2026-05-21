<?php

namespace App\Http\Controllers;

use App\Jobs\IndexCourseMaterial;
use App\Models\CourseMaterial;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
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
        $this->assertEditor((int) $course_id);

        $request->validate([
            'file' => ['required', 'file', 'mimes:pdf', 'max:51200'],
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
        ]);

        IndexCourseMaterial::dispatch($material->id);

        return redirect()
            ->route('course.coverageAnalysis', ['course' => $course_id])
            ->with('success', 'Material uploaded. Indexing in the background.');
    }

    public function destroy($course_id, $material_id): RedirectResponse
    {
        $this->assertEditor((int) $course_id);

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

    private function assertEditor(int $course_id): void
    {
        $permission = User::find(Auth::id())?->effectivePermissionForCourse($course_id) ?? 0;
        abort_unless(in_array($permission, [1, 2], true), 403, 'Editor access required.');
    }
}
