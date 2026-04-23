<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\Pivot;

class OutcomeMapAiSuggestion extends Pivot
{
    use HasFactory;

    protected $primaryKey = ['l_outcome_id', 'pl_outcome_id', 'map_scale_id'];

    protected $table = 'outcome_map_ai_suggestions';

    public $incrementing = false;
}
