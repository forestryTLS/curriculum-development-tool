<?php

namespace App\Http\Controllers;

use App\Helpers\RoleAssignmentHelpers;
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

    private $roleAssignmentHelper;

    public function __construct()
    {
        $this->middleware(['auth', 'verified']);
        $this->roleAssignmentHelper = new RoleAssignmentHelpers();
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

        $warningMessage = Collection::make();

        if($request->input('role')=='admin'){
            $role = Role::where('role', 'administrator')->first();
            if ($user->roles()->where('role_id', $role->id)->exists()) {
                return back()->with('warning', 'User already assigned admin role');
            }
            $user->roles()->syncWithoutDetaching([$role->id]);
            $errorMessages = $this->assignOwnershipOfAllCoursesNPrograms($request->input('email'));
            if($errorMessages->count() > 0){
                $warningMessage->add('Admin Role assigned. User could not be added to all courses/programs.');
            }

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
                if($errorMessages->count() > 0){
                    $warningMessage->add('Department Head Role assigned. User could not be added to all programs in department.');
                }
                if($request->input('accessToAllCoursesInFaculty') == "1"){
                    $department->heads()->updateExistingPivot($user->id, ['has_access_to_all_courses_in_faculty' => true]);
                    $errors = $this->roleAssignmentHelper->assignOwnershipOfAllCoursesInFaculty($user, $department->faculty->campus->campus,
                        $department->faculty->faculty, $role, null, $department);
                    if($errors->count() > 0){
                        $warningMessage->add('User could not be assigned to all courses in faculty');
                    }
                } else {
                    $errors = $this->assignOwnershipOfAllCoursesInDepartment($user, $department->faculty->campus->campus,
                        $department->faculty->faculty, $role, $department);
                    if($errors->count() > 0){
                        $warningMessage->add('User could not be assigned to all courses in department');
                    }
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
                        'role_id' => $programDirectorRoleId,
                        'has_access_to_all_courses_in_faculty' => $request->input('accessToAllCoursesInFaculty') == "1"],

                );
                $errorMessages = $this->assignOwnershipOfAllCoursesInProgram($request);
                if($errorMessages->count() > 0){
                    $warningMessage->add('Program Director role assigned to user. User could not be assigned to all courses in the program.');
                }
                if($request->input('accessToAllCoursesInFaculty') == "1"){
                    $errors = $this->roleAssignmentHelper->assignOwnershipOfAllCoursesInFaculty($user, $program->campus,
                        $program->faculty, $role, $program, null);
                    if($errors->count() > 0){
                        $warningMessage->add('User could not be assigned to all courses in faculty');
                    }
                }
            }
        }

        if($warningMessage->count() > 0){
            return redirect()->route('admin.assignRole.index', ['tab' => 'assign-role'])->with('warningMessages', $warningMessage);
        }

        return redirect()->route('admin.assignRole.index', ['tab' => 'assign-role'])->with('success', 'User successfully assigned role');

    }

     /**
     * Helper function to add the requested new administrator to all courses and programs.
     */

    private function assignOwnershipOfAllCoursesNPrograms($userEmail)
    {
        $courses = Course::all();
        $programs = Program::all();
        $adminRoleId = Role::where('role', 'administrator')->first()->id;
        $userAdmin = User::where('email', $userEmail)->whereRelation('roles', 'id', $adminRoleId)->first();

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

        $departmentHeadRole = Role::where('role', 'department head')->first();

        foreach($programsInDepartment as $program){
            $errorMessage = $this->roleAssignmentHelper->addElevatedRoleUserToProgram($user, $departmentHeadRole, $program, $department->department_id, false);
            if($errorMessage == null){
                $coursesInProgram = $program->courses()->get();
                foreach($coursesInProgram as $course){
                    $error = $this->roleAssignmentHelper->addElevatedRoleUserToCourse($user, $departmentHeadRole, $course, $program->program_id, $department->department_id);
                    if($error != null){
                        $errorMessages->add($error);
                    }
                }
            }else{
                $errorMessages->add($errorMessage);
            }
        }
        return $errorMessages;
    }

    /**
     * Helper function to add the requested new program director to all the courses of the program.
     */

    private function assignOwnershipOfAllCoursesInProgram($request){

        $program = Program::where('program', $request->input('program'))->first();
        $user = User::where('email', $request->input('email'))->first();

        $coursesInProgram = $program->courses()->get();
        $programDirectorRole = Role::where('role', 'program director')->first();

        $errorMessages = Collection::make();

        foreach($coursesInProgram as $course){
            $errorMessage = $this->roleAssignmentHelper->addElevatedRoleUserToCourse($user, $programDirectorRole, $course, $program->program_id, null);
            if($errorMessage != null){
                $errorMessages->add($errorMessage);
            }
        }

        return $errorMessages;
    }

    /**
     * Helper function to add the requested new department head to all courses in department.
     */
    private function assignOwnershipOfAllCoursesInDepartment($user, $campusName, $facultyName, $role, $department){
        $errorMessages = Collection::make();
        $coursesInDepartement = Course::where('campus', $campusName)->where('faculty', $facultyName)
            ->where('department', $department->department)->get();
        foreach($coursesInDepartement as $course){
            $errorMessage = $this->roleAssignmentHelper->addElevatedRoleUserToCourse($user,$role, $course, null, $department->department_id);
            if($errorMessage != null){
                $errorMessages->add($errorMessage);
            }
        }
        return $errorMessages;
    }

    /**
     * Get all roles for the given resource
     */
    public function getUserRoles(Request $request){
        $email = $request->input('userEmail');

        $user = User::where('email', $email)->with('roles', 'headedDepartments', 'directedPrograms')->first();
        if($user) {
            return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('user', $user)
                ->with('roles', $user->roles)->with('departmentsHeaded', $user->headedDepartments)->with('directedPrograms', $user->directedPrograms);
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

    public function deleteProgramDirectorRole(Request $request, $user, $role, $program = null){
        $user = User::where(['id' => $user])->first();
        $role = Role::where(['id' => $role])->first();
        if(!$program){
            if($role->role == 'program director'){
                $user->roles()->detach($role->id);
                return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('success', 'Program Director role removed for '.$user->name);
            }
        }
        $program = Program::where(['program_id' => $program])->first();
        CourseUserRole::where([ 'user_id' => $user->id, 'role_id' => $role->id,
            'program_id' => $program->program_id])->delete();
        ProgramUserRole::where(['user_id' => $user->id, 'role_id' => $role->id,
            'program_id' => $program->program_id])->delete();

        $user->directedPrograms()->wherePivot('program_id', $program->program_id)->detach($role->id);

        $programsDirected = $user->directedPrograms()->get();

        if($programsDirected->isEmpty()){
            $user->roles()->detach($role->id);
        }

        return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('success', 'Program Director role removed for '.$user->name.' for '.$program->program);
    }

    /**
     * Remove department head role for user
     * @param int $user
     * @param int $role
     * @param int $department
     */
    public function deleteDepartmentHeadRole(Request $request, $user, $role, $department=null){
        $user = User::where(['id' => $user])->first();
        $role = Role::where(['id' => $role])->first();
        if(!$department){
            if($role->role == 'department head'){
                $user->roles()->detach($role->id);
                return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('success', 'Department Head role removed '. $user->name);
            }
        }

        CourseUserRole::where([ 'user_id' => $user->id, 'role_id' => $role->id,
            'department_id' => $department])->delete();
        ProgramUserRole::where(['user_id' => $user->id, 'role_id' => $role->id,
            'department_id' => $department])->delete();

        $user->headedDepartments()->wherePivot('department_id', $department)->detach();;

        $departmentHeaded = $user->headedDepartments()->get();

        if ($departmentHeaded->isEmpty()) {
            $user->roles()->detach($role->id);
        }

        return redirect()->route('admin.assignRole.index', ['tab' => 'manage-roles'])->with('success', 'Department Head role removed '. $user->name);
    }

}
