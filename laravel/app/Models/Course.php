<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class Course extends Model
{
    use HasFactory;

    protected $table = 'courses';

    protected $primaryKey = 'course_id';

    protected $fillable = ['course_code', 'course_num', 'course_title', 'status', 'assigned', 'type', 'year', 'semester', 'section', 'delivery_modality', 'standard_category_id', 'scale_category_id', 'campus', 'faculty', 'department'];

    protected $guarded = ['course_id'];

    public function users()
    {
        return $this->belongsToMany(User::class, 'course_users', 'course_id', 'user_id')->withPivot('permission');
    }

    public function usersWithElevatedRoles()
    {
        return $this->belongsToMany(User::class, 'course_user_role', 'course_id', 'user_id')->withPivot('role_id', 'program_id', 'department_id');
    }

    public function collaborators()
    {
        return $this->users
            ->merge($this->usersWithElevatedRoles)
            ->unique('id')
            ->values();
    }

    public function owners()
    {
        return $this->belongsToMany(User::class, 'course_users', 'course_id', 'user_id')->wherePivot('permission', 1);
    }

    public function editors()
    {
        return $this->belongsToMany(User::class, 'course_users', 'course_id', 'user_id')->wherePivot('permission', 2);
    }

    public function viewers()
    {
        return $this->belongsToMany(User::class, 'course_users', 'course_id', 'user_id')->wherePivot('permission', 3);
    }

    public function learningActivities()
    {
        return $this->hasMany(LearningActivity::class, 'course_id', 'course_id');
    }

    public function assessmentMethods()
    {
        return $this->hasMany(AssessmentMethod::class, 'course_id', 'course_id');
    }

    public function learningOutcomes()
    {
        return $this->hasMany(LearningOutcome::class, 'course_id', 'course_id');
    }

    public function programs()
    {
        return $this->belongsToMany(Program::class, 'course_programs', 'course_id', 'program_id')->withPivot('manual_map_status', 'ai_suggestion_status');
    }

    public function standards()
    {
        return $this->hasMany(Standard::class, 'standard_category_id', 'standard_category_id');
    }

    public function standardScalesCategory()
    {
        return $this->belongsTo(StandardsScaleCategory::class, 'scale_category_id', 'scale_category_id');
    }

    public function standardCategory()
    {
        return $this->belongsTo(StandardCategory::class, 'standard_category_id', 'standard_category_id');
    }

    public function standardOutcomes()
    {
        return $this->hasMany(Standard::class, 'standard_category_id', 'standard_category_id');
    }

    public function courseStandardOutcomes()
    {
        //return $this->hasMany(Standard::class, 'standard_category_id', 'standard_category_id');
        return $this->hasManyThrough(StandardScale::class, StandardsScaleCategory::class);
    }

    public function optionalPriorities()
    {
        return $this->belongsToMany(OptionalPriorities::class, 'course_optional_priorities', 'course_id', 'op_id');
    }

    public function syllabusFile()
    {
        return $this->hasOne(CourseSyllabiFile::class, 'course_id', 'course_id');
    }

    public function courseDescription()
    {
        return $this->hasOne(CourseDescription::class, 'course_id', 'course_id');
    }

}
