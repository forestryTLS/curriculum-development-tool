<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CourseUserRole extends Model
{
    use HasFactory;

    protected $table = 'course_user_role';

    protected $primary = 'id';

    protected $fillable = ['user_id', 'course_id', 'role_id', 'program_id', 'department_id'];

    public $incrementing = false;
}
