<?php

namespace Database\Seeders;

use App\Models\Campus;
use App\Models\Faculty;
use App\Models\FacultyCourseCodes;
use Illuminate\Database\Seeder;

class FacultyCourseCodeSeeder extends Seeder
{
    public function run()
    {
        $campus = Campus::where('campus', 'Vancouver')->first();

        $forestryFacultyId = Faculty::where('faculty', 'Faculty of Forestry')->where('campus_id', $campus->campus_id)
            ->first()->faculty_id;

        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'BEST']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'FOPR']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'FRST']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'FCOR']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'FOPE']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'GEM']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'HGSE']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'ILS']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'NRES']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'CONS']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'UFOR']);
        FacultyCourseCodes::create(['faculty_id' => $forestryFacultyId, 'course_code' => 'WOOD']);

    }
}
