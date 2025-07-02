<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ProgramUserRole extends Model
{
    use HasFactory;

    protected $table = 'program_user_role';

    protected $primary = 'id';

    protected $fillable = ['user_id', 'program_id', 'role_id'];

    public $incrementing = false;
}
