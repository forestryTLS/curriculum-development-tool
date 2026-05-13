<?php

namespace App\Http\Controllers;

use App\Models\Course;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Models\CourseMaterial;
use Throwable;

class CourseMaterialController extends Controller
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
    public function store(Request $request){
        //try update course material

        try {
            $courseId = $request->input('course_id');
            $currentMaterial = $request->input('current_material');
            $newMaterial = $request->input('new_material');

            //get course
            $course = Course::find($courseId);

            //case: delete all Course Topics
            if(!$currentMaterial && !$newMaterial){
                $course->courseMaterials()->delete();
            }

            //get saved material
            $courseMaterial = $course->courseMaterials;

            //update current material
            foreach($courseMaterial as $material){
                if($currentMaterial && array_key_exists($material->course_material_id, $currentMaterial)){

                    $materialData = $currentMaterial[$material->course_material_id];

                    $material->name = $materialData['name'];
                    $material->type = $materialData['type'];
                    $material->description = $materialData['description'];
                    $material->is_required = isset($materialData['is_required']);
                    $material->url = $materialData["url"];
                    
                    $material->save();

                } else{
                    //remove material from course
                    $material->delete();
                }
            }

            //add new topics

            if($newMaterial){
                foreach($newMaterial as $index => $newmat){
                    if (empty(trim($newmat['name'] ?? ''))) {
                        continue;
                    }


                    $newCourseMaterial = new CourseMaterial;
                    $newCourseMaterial->name = $newmat['name'];
                    $newCourseMaterial->type = $newmat['type'];
                    $newCourseMaterial->description = $newmat['description'];
                    $newCourseMaterial->is_required = isset($newmat['is_required']);
                    $newCourseMaterial->url = $newmat['url'];
                    $newCourseMaterial->course_id = $courseId;
                    $newCourseMaterial->position = $index + 1;
                    $newCourseMaterial->save();
                }
            }

            // update courses 'updated_at' field
            $course = Course::find($request->input('course_id'));
            $course->touch();

            // get users name for last_modified_user
            $user = User::find(Auth::id());
            $course->last_modified_user = $user->name;
            $course->save();

            $request->session()->flash('success', 'Your course material was updated successfully!');
        } catch (Throwable $exception) {
            // flash error message if something goes wrong
            $request->session()->flash('error', 'There was an error updating your course material');

        } finally {
            // return back to course topics step
            return redirect()->route('courseWizard.step10', $request->input('course_id'));
        }

    }

    /**
     * Display the specified resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function show(CourseMaterial $courseMaterial)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function edit(CourseMaterial $courseMaterial)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request, CourseMaterial $courseMaterial)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  \App\Models\CourseTopic  $courseTopic
     */
    public function destroy(Request $request, $course_material_id): RedirectResponse
    {
        //
        $courseMaterial = CourseMaterial::where('course_material_id', $course_material_id)->first();
        $course_id = $request->input('course_id');

        if ($courseMaterial && $courseMaterial->delete()) {
            // update courses 'updated_at' field
            $course = Course::find($course_id);
            $course->touch();

            // get users name for last_modified_user
            $user = User::find(Auth::id());
            $course->last_modified_user = $user->name;
            $course->save();

            $request->session()->flash('success', 'Course material has been deleted');
        } else {
            $request->session()->flash('error', 'There was an error deleting the course material');
        }

        return redirect()->route('courseWizard.step10', $request->input('course_id'));
    }
}
