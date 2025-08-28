<?php

namespace App\Http\Controllers;

use App\Models\CourseDescription;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class CourseDescriptionController extends Controller
{
    //

    public function __construct()
    {
        $this->middleware(['auth', 'verified']);
    }

    public function index(): RedirectResponse
    {
        //
        return redirect()->back();
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request): RedirectResponse
    {
        // try to update Course Description
        try {
            $courseId = $request->input('course_id');
            $description = $request->input('current_courseDescription');
            if(CourseDescription::where('course_id', $courseId)->exists()) {
                $courseDescription = CourseDescription::where('course_id', $courseId)->first();
                $courseDescription->description = $description;
                $courseDescription->save();
            } else{
                $courseDescription = new CourseDescription();
                $courseDescription->course_id = $courseId;
                $courseDescription->description = $description;
                $courseDescription->save();
            }
        } finally{
            return redirect()->route('courseWizard.step8', $request->input('course_id'));
        }
    }


}
