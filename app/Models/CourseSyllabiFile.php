<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CourseSyllabiFile extends Model
{
    use HasFactory;

    protected $table = 'course_syllabi_file';

    protected $primary = 'id';

    protected $guarded = ['course_id'];

    protected $fillable = ['file_name', 'file_path'];

    public $incrementing = false;

    public function course(){
        return $this->belongsTo(Course::class);
    }

}
