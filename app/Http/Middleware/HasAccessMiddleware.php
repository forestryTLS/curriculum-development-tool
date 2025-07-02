<?php

namespace App\Http\Middleware;

use App\Models\Course;
use App\Models\Program;
use App\Models\syllabus\Syllabus;
use App\Models\User;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Symfony\Component\HttpFoundation\Response;

class HasAccessMiddleware
{
    /**
     * Handle an incoming request.
     */
    public function handle(Request $request, Closure $next): Response
    {
        $course_id = $request->route()->parameter('course');
        $program_id = $request->route()->parameter('program');
        $syllabus_id = $request->route()->parameter('syllabusId');
        // get current user
        $user = User::where('id', Auth::id())->first();

        if ($course_id != null) {
            // get all users for the course
            $courseUsers = Course::find($course_id)->users;

            //get all admins, directors and heads for course
            $courseElevatedAccessUsers = Course::find($course_id)->usersWithElevatedRoles;
            // check if the current user belongs to this course
            if (! in_array($user->id, $courseUsers->pluck('id')->toArray()) and
                ! in_array($user->id, $courseElevatedAccessUsers->pluck('id')->toArray())) {
                // user does not belong to this course
                $request->session()->flash('error', 'You do not have access to this course');

                return redirect()->route('home');
            } else {
                // get users permission level for this syllabus
//                $userPermission = $courseUsers->where('id', Auth::id())->first()->pivot->permission;
                $userPermission = User::where('id', Auth::id())->first()->effectivePermissionForCourse($course_id);
                switch ($userPermission) {
                    case 1:
                        // Owner
                        break;
                    case 2:
                        // Editor
                        $request['isEditor'] = true;
                        break;
                    case 3:
                        // Viewer
                        $request['isViewer'] = true;
                        break;
                    default:
                        // default
                }
            }
        } elseif ($program_id != null) {
            // get all users for the program
            $programUsers = Program::find($program_id)->users;
            //get all admins, directors and heads for course
            $programElevatedAccessUsers = Program::find($program_id)->usersWithElevatedRoles;
            // check if the current user belongs to this program
            if (! in_array($user->id, $programUsers->pluck('id')->toArray()) and
                ! in_array($user->id, $programElevatedAccessUsers->pluck('id')->toArray())) {
                // user does not belong to this program
                $request->session()->flash('error', 'You do not have access to this program');

                return redirect()->route('home');
            } else {
                // get users permission level for this syllabus
//                $userPermission = $programUsers->where('id', Auth::id())->first()->pivot->permission;
                $userPermission = User::where('id', Auth::id())->first()->effectivePermissionForProgram($program_id);
                switch ($userPermission) {
                    case 1:
                        // Owner
                        break;
                    case 2:
                        // Editor
                        $request['isEditor'] = true;
                        break;
                    case 3:
                        // Viewer
                        $request['isViewer'] = true;
                        break;
                    default:
                        // default
                }
            }

        } elseif ($syllabus_id != null) {
            $syllabus = Syllabus::find($syllabus_id);
            // get all users for the syllabus
            $syllabusUsers = Syllabus::find($syllabus_id)->users;
            // check if the current user belongs to this syllabus
            if (! in_array($user->id, $syllabusUsers->pluck('id')->toArray())) {
                // user does not belong to this syllabus
                $request->session()->flash('error', 'You do not have access to this syllabus');

                return redirect()->route('home');
            }
        }

        return $next($request);
    }
}
