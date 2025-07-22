<?php

namespace App\Helpers;

use App\Models\Campus;
use App\Models\Course;
use App\Models\CourseUserRole;
use App\Models\Department;
use App\Models\Faculty;
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
                return 'There was an error adding '.'<b>'.$user->email.'</b>'.' as ' . $role->role . ' to course';
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
                return 'There was an error adding '.'<b>'.$user->email.'</b>'.' as ' . $role->role . ' to program';
            }
        }
        return null;
    }
}
