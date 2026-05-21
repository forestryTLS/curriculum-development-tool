<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class CourseMaterial extends Model
{
    use HasFactory;

    protected $table = 'course_materials';

    protected $fillable = [
        'course_id',
        'uploaded_by',
        'file_name',
        'file_path',
        'mime_type',
        'file_size',
        'status',
        'error_message',
        'page_count',
    ];

    public const STATUS_PENDING = 'PENDING';
    public const STATUS_INDEXING = 'INDEXING';
    public const STATUS_INDEXED = 'INDEXED';
    public const STATUS_FAILED = 'FAILED';

    public function course()
    {
        return $this->belongsTo(Course::class, 'course_id', 'course_id');
    }

    public function uploader()
    {
        return $this->belongsTo(User::class, 'uploaded_by');
    }

    public function chunks()
    {
        return $this->hasMany(CourseMaterialChunk::class, 'course_material_id');
    }
}
