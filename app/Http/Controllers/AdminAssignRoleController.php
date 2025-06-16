<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Gate;
use App\Models\Campus;
use App\Models\Course;
use App\Models\CourseUser;
use App\Models\Department;
use App\Models\Faculty;
use App\Models\Program;
use App\Models\ProgramUser;
use App\Models\User;
use App\Models\Role;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

use Illuminate\Database\Eloquent\Collection;


class AdminAssignRoleController extends Controller{

    public function __construct()
    {
        $this->middleware(['auth', 'verified']);
    }


    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        if (Gate::denies('admin-privilege')) { // This Gate checks if user is an admin
            return redirect(route('home'));  //   and redirects to home if they are not (security)
        }

        $campuses = Campus::all();
        $faculties = Faculty::orderBy('faculty')->get();
        $departments = Department::orderBy('department')->get();
        $programs = Program::orderBy('program')->get();

        return view('pages.assignRole')->with('campuses', $campuses)->with('faculties', $faculties)->with('departments', $departments)->with('programs', $programs);
    }

    public function store(Request $request): RedirectResponse
    {
        //
        $this->validate($request, [
            'email' => 'required',
            'role' => 'required',
            'campus' => 'required_if:role,department-head',
            'faculty' => 'required_if:role,department-head',
            'department' => 'required_if:role,department-head',
            'program' => 'required_if:role,program-director'
        ]);

        $user = User::where('email', $request->input('email'))->first();

        if(!$user){
            return back()->with('error', 'User not found');
        }

        if($request->input('role')=='admin'){
            $role = Role::where('role', 'administrator')->first();
            $user->roles()->syncWithoutDetaching([$role->id]);
            $errorMessages = $this->assignOwenershipOfAllCoursesNPrograms($request->input('email'));

        } elseif ($request->input('role')=='department-head') {
            $role = Role::where('role', 'department head')->first();
            $user->roles()->syncWithoutDetaching([$role->id]);

            $campusName = $request->input('campus');
            $departmentName = $request->input('department');
            $facultyName = $request->input('faculty');

            $department = Department::where('department', $departmentName)
                ->whereHas('faculty', function ($query) use ($campusName, $facultyName) {
                    $query->where('faculty', $facultyName)
                        ->whereHas('campus', function ($query) use ($campusName) {
                            $query->where('campus', $campusName);
                        });
                })->first();

            if(!$department){
                return back()->with('error', 'Department not found');
            } else{
                $department->heads()->syncWithoutDetaching([$user->id]);

            }

        } elseif ($request->input('role')=='program-director') {
            $role = Role::where('role', 'program director')->first();
            $user->roles()->syncWithoutDetaching([$role->id]);
        }

        return redirect()->back()->with('success', 'User successfully assigned role');

    }

    private function assignOwenershipOfAllCoursesNPrograms($userEmail) 
    {
        $courses = Course::all();
        $programs = Program::all();
        $userAdmin = User::where('email', $userEmail)->first();


        $errorMessages = Collection::make();

        foreach($courses as $course){
            $courseUser = CourseUser::updateOrCreate(
                    ['course_id' => $course->course_id, 'user_id' => $userAdmin->id],
            );
            $courseUser = CourseUser::where([['course_id', '=', $courseUser->course_id], ['user_id', '=', $courseUser->user_id]])->first();
            $courseUser->permission = 1;
            if($courseUser->save()){
            } else{
                $errorMessages->add('There was an error adding '.'<b>'.$userAdmin->email.'</b>'.' to course '.$course->course_code.' '.$course->course_num);
            }
        }

        foreach($programs as $program){
            $programUser = ProgramUser::updateOrCreate(
                    ['program_id' => $program->program_id, 'user_id' => $userAdmin->id],
            );
            $programUser = ProgramUser::where([['program_id', '=', $programUser->program_id], ['user_id', '=', $programUser->user_id]])->first();
            $programUser->permission = 1;
            if($programUser->save()){
            } else{
                $errorMessages->add('There was an error adding '.'<b>'.$userAdmin->email.'</b>'.' to program '.$program->program);
            }
        }

        return $errorMessages;

    }
}
