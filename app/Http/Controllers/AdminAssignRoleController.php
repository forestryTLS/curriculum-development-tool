<?php

namespace App\Http\Controllers;

use App\Models\CourseUserRole;
use App\Models\FacultyCourseCodes;
use App\Models\ProgramUserRole;
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
    public function index(Request $request)
    {
        if (Gate::denies('admin-privilege')) { // This Gate checks if user is an admin
            return redirect(route('home'));  //   and redirects to home if they are not (security)
        }

        $campuses = Campus::all();
        $faculties = Faculty::orderBy('faculty')->get();
        $departments = Department::orderBy('department')->get();
        $programs = Program::orderBy('program')->get();

        $activeTab = $request->query('tab', 'assign-role');


        return view('pages.assignRole', compact('activeTab'))->with('campuses', $campuses)->with('faculties', $faculties)->with('departments', $departments)->with('programs', $programs);
    }

    /**
     * Store a newly created resource in storage.
     */

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
            if ($user->roles()->where('role_id', $role->id)->exists()) {
                return back()->with('warning', 'User already assigned admin role');
            }
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
                if ($department->heads()->where('user_id', $user->id)->exists()) {
                    return back()->with('warning', 'User already assigned head role for this department');
                }
                $department->heads()->syncWithoutDetaching([$user->id]);
                $errorMessages = $this->addUserToAllProgramInDepertment($user,$department, $campusName, $facultyName);
                if($department->faculty->faculty == "Faculty of Forestry" and $department->faculty->campus->campus == "Vancouver"){
                    $errors = $this->assignOwnershipOfAllCoursesInFaculty($user, $department->faculty->campus->campus,
                        $department->faculty->faculty, $role, null);
                }
            }

        } elseif ($request->input('role')=='program-director') {
            $role = Role::where('role', 'program director')->first();
            $user->roles()->syncWithoutDetaching([$role->id]);

            $programName = $request->input('program');
            $program = Program::where('program', $programName)->first();

            if(!$program){
                return back()->with('error', 'Program not found');
            } else {
                if ($program->directors()->where('user_id', $user->id)->where('role_id', $role->id)->exists()) {
                    return back()->with('warning', 'User already assigned director for this program');
                }
                $user = User::where('email', $request->input('email'))->first();
                $programDirectorRoleId = Role::where('role', 'program director')->first()->id;
                $programUserRole = ProgramUserRole::create(
                    ['program_id' => $program->program_id, 'user_id' => $user->id,
                        'role_id' => $programDirectorRoleId],
                );
                $programUserRole->save();
                $errorMessages = $this->assignOwnershipOfAllCoursesInProgram($request);
                if($program->campus == "Vancouver" and $program->faculty == "Faculty of Forestry"){
                    $errors = $this->assignOwnershipOfAllCoursesInFaculty($user, "Vancouver",
                        "Faculty of Forestry"  , $role, $program);
                }
            }
        }

        return redirect()->route('admin.assignRole.index', ['tab' => 'assign-role'])->with('success', 'User successfully assigned role');

    }

     /**
     * Helper function to add the requested new administrator to all courses and programs.
     */

    private function assignOwenershipOfAllCoursesNPrograms($userEmail)
    {
        $courses = Course::all();
        $programs = Program::all();
        $userAdmin = User::where('email', $userEmail)->first();
        $adminRoleId = Role::where('role', 'administrator')->first()->id;


        $errorMessages = Collection::make();

        foreach($courses as $course){
            $courseUserRole = CourseUserRole::create(
                ['course_id' => $course->course_id, 'user_id' => $userAdmin->id,
                    'role_id' => $adminRoleId]
            );
            if($courseUserRole->save()){
            } else{
                $errorMessages->add('There was an error adding '.'<b>'.$userAdmin->email.'</b>'.' to course '.$course->course_code.' '.$course->course_num);
            }
        }

        foreach($programs as $program){
            $programUserRole = ProgramUserRole::create(
                    ['program_id' => $program->program_id, 'user_id' => $userAdmin->id,
                        'role_id' => $adminRoleId],
            );
            if($programUserRole->save()){
            } else{
                $errorMessages->add('There was an error adding '.'<b>'.$userAdmin->email.'</b>'.' to program '.$program->program);
            }
        }

        return $errorMessages;

    }

    private function addUserToAllProgramInDepertment($user, $department, $campusName, $facultyName){
        $errorMessages = Collection::make();

        $programsInDepartment = Program::where(['campus' => $campusName, 'faculty' => $facultyName,
            'department' => $department->department])->get();

        $departmentHeadRoleId = Role::where('role', 'department head')->first()->id;

        foreach($programsInDepartment as $program){
            $programUserRole = ProgramUserRole::create(
                ['program_id' => $program->program_id, 'user_id' => $user->id,
                    'role_id' => $departmentHeadRoleId]);
            if($programUserRole->save()){
                $coursesInProgram = $program->courses()->get();
                foreach($coursesInProgram as $course){
                    $courseUserRole = CourseUserRole::create(
                        ['course_id' => $course->course_id, 'user_id' => $user->id,
                            'role_id' => $departmentHeadRoleId,
                            'program_id' => $program->program_id],
                    );
                    if($courseUserRole->save()){
                    } else{
                        $errorMessages->add('There was an error adding '.'<b>'.$user->email.'</b>'.' to course '.$course->course_code.' '.$course->course_num);
                    }
                }

            }else{
                $errorMessages->add('There was an error adding '.'<b>'.$user->email.'</b>'.' to course '.$program->program);
            }
        }
        return $errorMessages;
    }

    /**
     * Helper function to add the requested new program director to all the courses of the program.
     */

    private function assignOwnershipOfAllCoursesInProgram($request){

        $program = Program::where('program', $request->input('program'))->first();

        $coursesInProgram = $program->courses()->get();
        $programDirectorRoleId = Role::where('role', 'program director')->first()->id;

        $errorMessages = Collection::make();

        foreach($coursesInProgram as $course){
            $user = User::where('email', $request->input('email'))->first();
            $courseUserRole = CourseUserRole::create(
                    ['course_id' => $course->course_id, 'user_id' => $user->id,
                        'role_id' => $programDirectorRoleId,
                        'program_id' => $program->program_id],
            );
            if($courseUserRole->save()){
            } else{
                $errorMessages->add('There was an error adding '.'<b>'.$user->email.'</b>'.' to course '.$course->course_code.' '.$course->course_num);
            }
        }

        return $errorMessages;
    }

    private function assignOwnershipOfAllCoursesInFaculty($user, $campusName, $facultyName, $role, $program){
        $errorMessages = Collection::make();

        $campus = Campus::where('campus', $campusName)->first();
        $faculty = Faculty::where('faculty', $facultyName)->where('campus_id', $campus->campus_id)->first();

        $courseCodes = FacultyCourseCodes::where('faculty_id', $faculty->faculty_id)->get();

        foreach($courseCodes as $courseCode){
            $courses = Course::where('course_code', $courseCode->course_code)->get();
            foreach($courses as $course){
                if($program){
                    if(!CourseUserRole::where(['course_id' => $course->course_id, 'user_id' => $user->id,
                        'role_id' => $role->id, 'program_id' => $program->program_id])->exists()){
                        $courseUserRole = CourseUserRole::create(['course_id' => $course->course_id, 'user_id' => $user->id,
                            'role_id' => $role->id, 'program_id' => $program->program_id]);
                        if($courseUserRole->save()){

                        } else{
                            $errorMessages->add('There was an error adding '.'<b>'.$user->email.'</b>'.' to course '.$course->course_code.' '.$course->course_num);
                        }
                    }
                } else {
                    if(!CourseUserRole::where(['course_id' => $course->course_id, 'user_id' => $user->id,
                        'role_id' => $role->id, 'program_id' => null])->exists()){

                        $courseUserRole = CourseUserRole::create(['course_id' => $course->course_id, 'user_id' => $user->id,
                            'role_id' => $role->id]);

                        if($courseUserRole->save()){

                        } else{
                            $errorMessages->add('There was an error adding '.'<b>'.$user->email.'</b>'.' to course '.$course->course_code.' '.$course->course_num);
                        }
                    }
               }
            }
        }

        return $errorMessages;
    }

    /**
     * Get all roles for the given resource
     */
    public function getUserRoles(Request $request){
        $email = $request->input('userEmail');
        $user = User::where('email', $email)->first();

        if ($user) {
            $roles = $user->roles()->get();
            $departmentsHeaded = $user->headedDepartments()->get();
            $directedPrograms = $user->directedPrograms()->get();
            return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('user', $user)
                ->with('roles', $roles)->with('departmentsHeaded', $departmentsHeaded)->with('directedPrograms', $directedPrograms);
        } else {
            return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('error', 'User not found.')->with('activeTab', 'manage-roles');
        }

    }

    /**
     * Remove administrator role for user
     * @param int $user
     * @param int $role
     */
    public function deleteAdminRole(Request $request, $user, $role){
        $user = User::where(['id' => $user])->first();
        $role = Role::where(['id' => $role])->first();
        CourseUserRole::where([ 'user_id' => $user->id, 'role_id' => $role->id])->delete();
        ProgramUserRole::where(['user_id' => $user->id, 'role_id' => $role->id])->delete();
        $user->roles()->detach($role->id);
        return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('success', 'Administrator role removed for '. $user->name);
    }

    /**
     * Remove program director role for user
     * @param int $user
     * @param int $role
     * @param int $program
     */

    public function deleteProgramDirectorRole(Request $request, $user, $role, $program){
        $user = User::where(['id' => $user])->first();
        $role = Role::where(['id' => $role])->first();
        $program = Program::where(['program_id' => $program])->first();
        CourseUserRole::where([ 'user_id' => $user->id, 'role_id' => $role->id,
            'program_id' => $program->program_id])->delete();
        ProgramUserRole::where(['user_id' => $user->id, 'role_id' => $role->id,
            'program_id' => $program->program_id])->delete();

        $user->directedPrograms()->wherePivot('program_id', $program->program_id)->detach($role->id);

        $programsDirected = $user->directedPrograms()->get();

        $hasDirectedProgramsInForestry = $programsDirected->contains(function ($program) {
            return $program->campus == 'Vancouver' && $program->faculty == 'Faculty of Forestry';
        });

        if($programsDirected->isEmpty()){
            $user->roles()->detach($role->id);
        } else if($hasDirectedProgramsInForestry){

            $forestryProgram = $programsDirected->first(function ($program) {
                return $program->campus == 'Vancouver' && $program->faculty == 'Faculty of Forestry';
            });

            // This ensures that the user still has ownership of all courses in the faculty of forestry
            $this->assignOwnershipOfAllCoursesInFaculty($user, "Vancouver",
                "Faculty of Forestry"  , $role, $forestryProgram);


        }

        return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('success', 'Program Director role removed for '.$user->name.' for '.$program->program);
    }

    /**
     * Remove department head role for user
     * @param int $user
     * @param int $role
     * @param int $department
     */
    public function deleteDepartmentHeadRole(Request $request, $user, $role, $department){
        $user = User::where(['id' => $user])->first();
        $role = Role::where(['id' => $role])->first();
        $department = Department::where(['department_id' => $department])->first();
        $faculty = $department->faculty;
        $campus = $faculty->campus;
        $programsInDepartment = Program::where(['campus' => $campus->campus, 'faculty'=>$faculty->faculty,
            'department' => $department->department])->get();

        $vancouverCampusId = Campus::where('campus', 'Vancouver')->first()->campus_id;
        $forestryFacultyId = Faculty::where(['faculty' => 'Faculty of Forestry',
            'campus_id' => $vancouverCampusId])->first()->faculty_id;

        foreach($programsInDepartment as $program){
            CourseUserRole::where([ 'user_id' => $user->id, 'role_id' => $role->id,
                'program_id' => $program->program_id])->delete();
            ProgramUserRole::where(['user_id' => $user->id, 'role_id' => $role->id,
                'program_id' => $program->program_id])->delete();
        }

        $user->headedDepartments()->wherePivot('department_id', $department->department_id)->detach();;

        $departmentHeaded = $user->headedDepartments()->get();

        if ($departmentHeaded->isEmpty()) {
            $user->roles()->detach($role->id);
        } else {
            // Department heads in Faculty of Forestry are assigned access to all courses in the faculty
            $hasDepartmentInForestry = $departmentHeaded->contains(function ($department) use ($forestryFacultyId) {
                return optional($department->faculty)->faculty_id === $forestryFacultyId;
            });
            if (!$hasDepartmentInForestry) {
                $forestryCourseCodes = FacultyCourseCodes::where('faculty_id', $forestryFacultyId)->get();
                foreach ($forestryCourseCodes as $forestryCourseCode) {
                    $coursesWithCode = Course::where(['course_code' => $forestryCourseCode->course_code])->get();
                    foreach ($coursesWithCode as $course) {
                        CourseUserRole::where([ 'user_id' => $user->id, 'role_id' => $role->id,
                            'course_id' => $course->course_id])->delete();
                    }
                }
            } else {
                // This ensures that the user still has ownership of all courses in the faculty of forestry
                $this->assignOwnershipOfAllCoursesInFaculty($user, "Vancouver",
                    "Faculty of Forestry"  , $role, null);
            }
        }

        return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('success', 'Department Head role removed '. $user->name . ' for ' . $department->department);
    }

}
