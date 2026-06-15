<?php

namespace App\Http\Controllers;

use App\Models\Course;
use App\Models\CourseMaterial;
use App\Models\Program;
use App\Models\User;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class CoverageAnalysisController extends Controller
{
    public function __construct()
    {
        $this->middleware(['auth', 'verified']);
        $this->middleware('hasAccess');
    }

    public function course(Request $request, $course_id): View
    {
        $course = Course::where('course_id', $course_id)->firstOrFail();

        $permission = User::find(Auth::id())?->effectivePermissionForCourse((int) $course_id) ?? 0;
        $canEdit = in_array($permission, [1, 2], true);

        $materials = CourseMaterial::where('course_id', $course_id)
            ->with([
                'uploader:id,name',
                'chunks' => fn ($q) => $q->orderBy('page_number')->orderBy('chunk_index'),
            ])
            ->orderByDesc('created_at')
            ->get();

        return view('courses.coverageAnalysis', compact('course', 'materials', 'canEdit'));
    }

    public function program(Request $request, $program_id): View
    {
        $program = Program::where('program_id', $program_id)->firstOrFail();

        $courses = $program->courses()->orderBy('course_code')->orderBy('course_num')->get();
        $courseIds = $courses->pluck('course_id')->all();

        $materials = CourseMaterial::whereIn('course_id', $courseIds)
            ->with([
                'uploader:id,name',
                'chunks' => fn ($q) => $q->orderBy('page_number')->orderBy('chunk_index'),
            ])
            ->orderByDesc('created_at')
            ->get();

        $materialsByCourse = $materials->groupBy('course_id');

        return view('programs.coverageAnalysis', compact(
            'program', 'courses', 'materialsByCourse'
        ));
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

    private function assertIsEditor(int $course_id): void
    {
        $permission = User::find(Auth::id())?->effectivePermissionForCourse($course_id) ?? 0;
        abort_unless(in_array($permission, [1, 2], true), 403, 'Editor access required.');
    }
}
