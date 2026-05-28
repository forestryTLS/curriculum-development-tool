<?php

use App\Models\Course;
use App\Models\LearningOutcome;
use App\Models\Program;
use App\Models\ProgramLearningOutcome;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

function makeTestUser(string $email): User
{
    DB::table('users')->insert([
        'name' => 'Fixture User',
        'email' => $email,
        'email_verified_at' => Carbon::now(),
        'password' => '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
    ]);

    return User::where('email', $email)->first();
}

function makeTestCourse(string $title = 'E2E Fixture Course'): Course
{
    return Course::create([
        'course_code' => 'E2E',
        'course_num' => 101,
        'course_title' => $title,
        'delivery_modality' => 'O',
        'year' => 2026,
        'semester' => 'W1',
        'assigned' => 1,
        'type' => 'unassigned',
        'created_at' => Carbon::now(),
        'updated_at' => Carbon::now(),
    ]);
}

function makeTestProgram(string $name = 'E2E Fixture Program'): Program
{
    return Program::create([
        'program' => $name,
        'faculty' => 'Irving K. Barber Faculty of Science',
        'department' => 'Computer Science',
        'level' => 'Bachelors',
        'status' => 1,
        'created_at' => Carbon::now(),
        'updated_at' => Carbon::now(),
    ]);
}

function linkUserToCourse(User $user, Course $course, int $permission = 1): void
{
    DB::table('course_users')->insert([
        'course_id' => $course->course_id,
        'user_id' => $user->id,
        'permission' => $permission,
    ]);
}

function linkCourseToProgram(Course $course, Program $program): void
{
    DB::table('course_programs')->insert([
        'course_id' => $course->course_id,
        'program_id' => $program->program_id,
        'created_at' => Carbon::now(),
        'updated_at' => Carbon::now(),
    ]);
}

function addCloToCourse(Course $course, string $text, string $shortphrase = 'Test CLO'): LearningOutcome
{
    return LearningOutcome::create([
        'course_id' => $course->course_id,
        'l_outcome' => $text,
        'clo_shortphrase' => $shortphrase,
    ]);
}

function addPloToProgram(Program $program, string $text, string $shortphrase = 'Test PLO'): ProgramLearningOutcome
{
    DB::table('program_learning_outcomes')->insert([
        'program_id' => $program->program_id,
        'pl_outcome' => $text,
        'plo_shortphrase' => $shortphrase,
        'created_at' => Carbon::now(),
        'updated_at' => Carbon::now(),
    ]);

    return ProgramLearningOutcome::where('program_id', $program->program_id)
        ->where('pl_outcome', $text)
        ->first();
}

function attachMappingScalesToProgram(Program $program, array $mapScaleIds = [1, 2, 3]): void
{
    foreach ($mapScaleIds as $id) {
        DB::table('mapping_scale_programs')->insert([
            'map_scale_id' => $id,
            'program_id' => $program->program_id,
            'created_at' => Carbon::now(),
            'updated_at' => Carbon::now(),
        ]);
    }
}
