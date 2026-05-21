<?php

namespace App\Http\Controllers;

use App\Models\Course;
use App\Models\CourseMaterial;
use App\Models\Program;
use App\Models\User;
use Illuminate\Contracts\View\View;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

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

    public function courseStatus(Request $request, $course_id): JsonResponse
    {
        $statuses = CourseMaterial::where('course_id', $course_id)
            ->select(['id', 'status', 'page_count', 'pages_processed'])
            ->get();

        return response()->json($statuses);
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
}
