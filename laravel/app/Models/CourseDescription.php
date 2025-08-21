<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CourseDescription extends Model
{
    use HasFactory;

    protected $table = 'course_description';

    protected $fillable = ['course_id', 'description'];

    protected $primaryKey = 'id';
    
    public function course()
    {
        return $this->belongsTo(Course::class, 'course_id', 'course_id');
    }
}