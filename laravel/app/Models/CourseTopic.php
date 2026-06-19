<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CourseTopic extends Model
{
    use HasFactory;

    protected $table = 'course_topics';

    protected $primaryKey = 'course_topic_id';
    protected $fillable = ['course_id', 'topic', 'description', 'position'];

    public function course(){
        return $this->belongsTo(Course::class, 'course_id', 'course_id');
    }



}
