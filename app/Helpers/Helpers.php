<?php

use Illuminate\Database\Eloquent\Collection;
use App\Models\User;
use App\Models\CourseUser;


if(!function_exists('addAllAminsToCourse')) {
    function addAllAminsToCourse($course) {
        
        $errorMessages = Collection::make();

        $adminUsers = User::whereHas('roles', function ($query){
            $query->where('role', 'administrator');
            })->get();

        foreach ($adminUsers as $adminUser) {
                // find the newCollab by their email
            $userAdmin = User::where('email', $adminUser->email)->first();
            $courseUser = CourseUser::updateOrCreate(
                    ['course_id' => $course->course_id, 'user_id' => $userAdmin->id],
            );
            $courseUser = CourseUser::where([['course_id', '=', $courseUser->course_id], ['user_id', '=', $courseUser->user_id]])->first();
            $courseUser->permission = 1;
            if($courseUser->save()){
            } else{
                $errorMessages->add('There was an error adding '.'<b>'.$user->email.'</b>'.' to course '.$course->course_code.' '.$course->course_num);
            }
        }

        return $errorMessages;

    }
}
