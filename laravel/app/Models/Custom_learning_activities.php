<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Custom_learning_activities extends Model
{
    use HasFactory;

    protected $primaryKey = 'custom_activity_id';

    protected $fillable = ['custom_activities'];
}
