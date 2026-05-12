<?php

namespace App\Http\Controllers;

use App\Models\Course;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Models\CourseTopic;
use Throwable;

class CourseTopicController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
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
     *
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
        // try update course topics
        try {
            $courseId = $request->input('course_id');
            $currentTopics = $request->input('current_topics');
            $newTopics = $request->input('new_topics');
            // get the course
            $course = Course::find($courseId);
            // case: delete all Course Topics
            if (!$currentTopics && ! $newTopics) {
                $course->courseTopics()->delete();
            }
            // get the saved course topics for this course
            $courseTopics = $course->courseTopics;
            // update current topics
            foreach ($courseTopics as $courseTopic) {
                if ($currentTopics && array_key_exists($courseTopic->course_topic_id, $currentTopics)) {
                    // save Topic
                    $courseTopic->topic = $currentTopics[$courseTopic->course_topic_id];
                    $courseTopic->save();
                } else {
                    // remove Topic from course
                    $courseTopic->delete();
                }
            }
            // add new Topics
            if ($newTopics) {
                foreach ($newTopics as $index => $newTopic) {
                    if (trim($newTopic) === '') {
                        continue;
                    }

                    $newCourseTopic = new CourseTopic;
                    $newCourseTopic->topic = $newTopic;
                    $newCourseTopic->course_id = $courseId;
                    $newCourseTopic->position = $index + 1;
                    $newCourseTopic->save();
                }
            }

            // update courses 'updated_at' field
            $course = Course::find($request->input('course_id'));
            $course->touch();

            // get users name for last_modified_user
            $user = User::find(Auth::id());
            $course->last_modified_user = $user->name;
            $course->save();

            $request->session()->flash('success', 'Your course topics were updated successfully!');

        } catch (Throwable $exception) {
            // flash error message if something goes wrong
            $request->session()->flash('error', 'There was an error updating your course topics');

        } finally {
            // return back to course topics step
            return redirect()->route('courseWizard.step9', $request->input('course_id'));
        }
    }

    /**
     * Display the specified resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function show(CourseTopic $courseTopic)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function edit(CourseTopic $courseTopic)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request, CourseTopic $courseTopic)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  \App\Models\CourseTopic  $courseTopic
     */
    public function destroy(Request $request, $course_topic_id): RedirectResponse
    {
        //
        $courseTopic = CourseTopic::where('course_topic_id', $course_topic_id)->first();
        $course_id = $request->input('course_id');

        if ($courseTopic && $courseTopic->delete()) {
            // update courses 'updated_at' field
            $course = Course::find($course_id);
            $course->touch();

            // get users name for last_modified_user
            $user = User::find(Auth::id());
            $course->last_modified_user = $user->name;
            $course->save();

            $request->session()->flash('success', 'Course topic has been deleted');
        } else {
            $request->session()->flash('error', 'There was an error deleting the course topic');
        }

        return redirect()->route('courseWizard.step9', $request->input('course_id'));
    }
}
