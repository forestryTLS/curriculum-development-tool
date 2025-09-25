<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class FacultyCourseCodes extends Model
{
    use HasFactory;

    protected $primaryKey = ['faculty_id', 'course_code'];
    public $incrementing = false;
    protected $fillable = ['faculty_id', 'course_code'];


    public function faculty()
    {
        return $this->belongsTo(Faculty::class, 'faculty_id', 'faculty_id');
    }
}
