<?php

namespace App\Helpers;

use App\Models\Campus;
use App\Models\Course;
use App\Models\CourseUserRole;
use App\Models\Department;
use App\Models\Faculty;
use App\Models\FacultyCourseCodes;
use App\Models\Program;
use App\Models\ProgramUserRole;
use App\Models\Role;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;

class RoleAssignmentHelpers
{

    /**
     * Helper function to add all admins to given course/program.
     */
    public function addAllAdminsToEntity($entity){
        $errorMessages = Collection::make();

        $adminRoleId = Role::where('role', 'administrator')->first()->id;

        $adminUsers = User::whereHas('roles', function ($query){
            $query->where('role', 'administrator');
        })->get();

        foreach ($adminUsers as $adminUser) {
            if (!$entity->usersWithElevatedRoles()->wherePivot('role_id', $adminRoleId)
                ->wherePivot('user_id', $adminUser->id)->exists()) {
                try {
                    $entity->usersWithElevatedRoles()->attach($adminUser->id, ['role_id' => $adminRoleId]);
                } catch (\Illuminate\Database\QueryException $e) {
                    $errorMessages->add('There was an error adding '.'<b>'.$adminUser->email.'</b>'.' as administrator');
                }
            }
        }
        return $errorMessages;
    }


    /**
     * Helper function to get department for given course/program
     */
    public function getDepartmentFromEntity($entity){
        $campus = Campus::where('campus', $entity->campus)->first();
        if($campus != null){
            $faculty = Faculty::where(['faculty'=> $entity->faculty,
                'campus_id' => $campus->campus_id])->first();
            if($faculty != null) {
                $department = Department::where(['department' => $entity->department,
                    'faculty_id' => $faculty->faculty_id])->first();
                return $department;
            }
        }
        return null;
    }

    /**
     * @param User $user
     * @param Role $role
     * @param Course $course
     * @param int $programId
     * @param int $departmentId
     * Helper function to assign given elevated role to user for given course
     */
    public function addElevatedRoleUserToCourse($user, $role, $course, $programId, $departmentId){
        if(!$course->usersWithElevatedRoles()->wherePivot('role_id', $role->id)
            ->wherePivot('user_id', $user->id)->wherePivot('program_id', $programId)
            ->wherePivot('department_id', $departmentId)->exists()){
            $courseUserRole = CourseUserRole::create([
                'course_id' => $course->course_id,
                'user_id' => $user->id,
                'program_id' => $programId,
                'department_id' => $departmentId,
                'role_id' => $role->id,
            ]);
            if($courseUserRole->save()){
            }else{
                return 'There was an error adding '.'<b>'.$user->email.'</b>'.' as ' . $role->role . ' to course ' .$course->course_code.' '.$course->course_num;
            }
        }
        return null;
    }

    /**
     * @param User $user
     * @param Role $role
     * @param Program $program
     * @param int $departmentId
     * @param boolean $has_access_to_all_courses_in_faculty
     * Helper function to assign given elevated role to user for given program
     */
    public function addElevatedRoleUserToProgram($user, $role, $program, $departmentId, $has_access_to_all_courses_in_faculty){
        if(!$program->usersWithElevatedRoles()->wherePivot('role_id', $role->id)
            ->wherePivot('user_id', $user->id)->wherePivot('department_id', $departmentId)
            ->wherePivot('has_access_to_all_courses_in_faculty', $has_access_to_all_courses_in_faculty)->exists()){
            $programUserRole = ProgramUserRole::create([
                'program_id' => $program->program_id,
                'user_id' => $user->id,
                'department_id' => $departmentId,
                'role_id' => $role->id,
                'has_access_to_all_courses_in_faculty' => $has_access_to_all_courses_in_faculty,
            ]);
            if($programUserRole->save()){
            }else{
                return 'There was an error adding '.'<b>'.$user->email.'</b>'.' as ' . $role->role . ' to program '. $program->program;
            }
        }
        return null;
    }

    /**
     * @param $campusName string
     * @param $facultyName string
     * Helper function to get all courses in faculty by stored faculty information and by identified faculty
     * through course codes
     */
    private function getAllCoursesInFaculty($campusName, $facultyName){
        $coursesInFacultyByName = Course::where(['campus' => $campusName, 'faculty' => $facultyName])->get();

        $campus = Campus::where('campus', $campusName)->first();
        $faculty = $campus?->faculties()->where('faculty', $facultyName)->first();

        if(!$campus || !$faculty){
            return $coursesInFacultyByName;
        }

        $courseCodes = FacultyCourseCodes::where('faculty_id', $faculty->faculty_id)->get()->pluck('course_code')->toArray();

        if (count($courseCodes) === 0) {
            return $coursesInFacultyByName;
        }

        $coursesInFacultyByCode = Course::whereIn('course_code', $courseCodes)->where(
            function ($query) use ($campusName, $facultyName) {
                $query->where(function ($q) {
                    $q->whereNull('campus')->whereNull('faculty');
                })->orWhere(function ($q) use ($campusName, $facultyName) {
                    $q->where('campus', $campusName)
                        ->where('faculty', $facultyName);
                })->orWhere(function ($q) use ($campusName, $facultyName) {
                    $q->where('campus', 'Other')->whereNull('faculty')->whereNull('department');
                });
            })->get();

        return $coursesInFacultyByName->merge($coursesInFacultyByCode)->unique('course_id');


    }

    /**
     * @param $user User
     * @param $campusName string
     * @param $facultyName string
     * @param $role Role
     * @param $program Program
     * @param $department Department
     * Helper function to add the requested new user with given elevated role to all courses in faculty.
     */

    public function assignOwnershipOfAllCoursesInFaculty($user, $campusName, $facultyName, $role, $program, $department){
        $errorMessages = Collection::make();

        $allCoursesInFaculty = $this->getAllCoursesInFaculty($campusName, $facultyName);

        foreach($allCoursesInFaculty as $course){
            if($program){
                $errorMessage = $this->addElevatedRoleUserToCourse($user, $role, $course, $program->program_id, null);
                if($errorMessage != null){
                    $errorMessages->add($errorMessage);
                }
            } else if($department) {
                $errorMessage = $this->addElevatedRoleUserToCourse($user, $role, $course, null, $department->department_id);
                if($errorMessage != null){
                    $errorMessages->add($errorMessage);
                }
            }
        }

        return $errorMessages;
    }

    /**
     * Helper function to add all department heads with access to all faculty courses to the given course.
     */
    public function  addFacultyDepartmentHeadsToCourse($course, $facultyId)
    {
        $errorMessages = Collection::make();
        $departmentsInFaculty = Department::where('faculty_id', $facultyId)->get();
        $departmentHeadRole = Role::where('role', 'department head')->first();
        foreach ($departmentsInFaculty as $department) {
            $departmentHeads = $department->heads()->where('has_access_to_all_courses_in_faculty', true)->get();
            foreach ($departmentHeads as $head) {
                $errorMessage = $this->addElevatedRoleUserToCourse($head,$departmentHeadRole,
                    $course, null, $department->department_id);
                if($errorMessage != null) {
                    $errorMessages->add($errorMessage);
                }
            }
        }
        return $errorMessages;
    }

    /**
     * Helper function to add all program directors with all faculty course access to given course.
     */
    public function addFacultyProgramDirectorsToCourse($course, $facultyId){
        $errorMessages = Collection::make();
        $faculty = Faculty::where('faculty_id', $facultyId)->first();
        if(!$faculty){
            $errorMessages->add("Course Faculty doesn't exist");
            return $errorMessages;
        }
        $programs = Program::where(['campus' => $faculty->campus->campus,
            'faculty' => $faculty->faculty])->get();
        $programDirectorRole = Role::where('role', 'program director')->first();

        foreach ($programs as $program) {
            $programDirectors = $program->directors()->wherePivot('has_access_to_all_courses_in_faculty', true)->get();
            foreach ($programDirectors as $director) {
                $errorMessage =$this->addElevatedRoleUserToCourse($director,$programDirectorRole,
                    $course, $program->program_id, null);
                if($errorMessage != null) {
                    $errorMessages->add($errorMessage);
                }
            }
        }
        return $errorMessages;
    }
}
