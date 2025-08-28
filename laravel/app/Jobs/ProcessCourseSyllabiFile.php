<?php

namespace App\Jobs;

use App\Helpers\RoleAssignmentHelpers;
use App\Models\AssessmentMethod;
use App\Models\Course;
use App\Models\CourseDescription;
use App\Models\CourseSyllabiFile;
use App\Models\CourseUser;
use App\Models\FacultyCourseCodes;
use App\Models\LearningOutcome;
use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Bus\Batchable;

class ProcessCourseSyllabiFile implements ShouldQueue
{
    use Batchable, Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    protected $courseFileId;
    protected $userId;
    private $roleAssignmentHelper;

    /**
     * Create a new job instance.
     */
    public function __construct($courseFile, $userId)
    {
        $this->courseFileId = $courseFile;
        $this->userId = $userId;
        $this->roleAssignmentHelper = new RoleAssignmentHelpers();

    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        $baseUrl = config('services.python_api.base_url');

        $courseFile = CourseSyllabiFile::where('id', $this->courseFileId)->first();


        try{
            $response = HTTP::post($baseUrl . '/create_course_from_syllabi', [
                'file_path' => storage_path('app') . "/" . $courseFile->file_path,
                'client_original_filename' => $courseFile->file_name
            ]);
        } catch (\Exception $e) {
            // handle any other exception
            Log::error('Error in parsing file ' . $e->getMessage());
            return;

        }

        if($response->failed()){
            Log::error('Error in creating course from ' . $courseFile->file_name . ': ' . $response->body());
            return;
        }

        // Decode the response to get the course object
        $courseObject = json_decode($response->body());

        if($courseObject->status !='success'){
            Log::error('Error in creating course from ' . $courseFile->file_name . ': ' . $courseObject->message);
            return;
        }
        // TO DO: CHANGE AFTER API CALL
        $course = new Course();
        $course->course_code = $courseObject->code;
        $course->course_num = $courseObject->number;
        $course->delivery_modality = 'O';
        $course->year = $courseObject->year;
        $course->semester = $courseObject->term;
        $course->course_title = $courseObject->title;
        $course->assigned = 1;
        $course->type = 'unassigned';
        $course->save();

        $courseDescription = new CourseDescription();
        $courseDescription->course_id = $course->course_id;
        $courseDescription->description = $courseObject->description;
        $courseDescription->save();

        $courseFile = CourseSyllabiFile::where(['file_name'=> $courseFile->file_name,
            'file_path'=> $courseFile->file_path])->first();
        $courseFile->course_id = $course->course_id;
        $courseFile->save();

        $learningOutcomes = $courseObject->goals;

        foreach($learningOutcomes as $lo){
            $learningOutcome = new LearningOutcome();
            $learningOutcome->l_outcome = $lo;
            $learningOutcome->course_id = $course->course_id;
            $learningOutcome->save();
        }

        $assessmentMethods = $courseObject->assessments;

        foreach($assessmentMethods as $am){
            $assessmentMethod = new AssessmentMethod();
            $assessmentMethod->a_method = $am[0];
            $assessmentMethod->weight = $am[1];
            $assessmentMethod->course_id = $course->course_id;
            $assessmentMethod->save();
        }

        $user = User::where('id', $this->userId)->first();
        $adminAddErrorMessages = $this->roleAssignmentHelper->addAllAdminsToEntity($course);

        //Add department heads and program directors of Faculty of Forestry owners of all courses in the faculty
        if(FacultyCourseCodes::where('course_code', $course->course_code)->exists()){
            $facultyId = FacultyCourseCodes::where('course_code', $course->course_code)->first()->faculty_id;
            $this->roleAssignmentHelper->addFacultyDepartmentHeadsToCourse($course, $facultyId);
            $this->roleAssignmentHelper->addFacultyProgramDirectorsToCourse($course, $facultyId);
        }

        $courseUser = new CourseUser;
        $courseUser->course_id = $course->course_id;
        $courseUser->user_id = $user->id;
        // assign the creator of the course the owner permission
        $courseUser->permission = 1;
        if ($courseUser->save()) {

        } else {
            Log::error('Error in creating course from ' . $courseFile->file_name);
        }
    }
}
