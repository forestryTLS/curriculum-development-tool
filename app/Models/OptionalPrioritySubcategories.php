<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class OptionalPrioritySubcategories extends Model
{
    use \Backpack\CRUD\app\Models\Traits\CrudTrait;
    use \Backpack\CRUD\app\Models\Traits\HasIdentifiableAttribute;
    use HasFactory;

    protected $primaryKey = 'subcat_id';

    protected $table = 'optional_priority_subcategories';

    protected $fillable = [
        'subcat_id',
        'subcat_name',
        'subcat_desc',
        'cat_id',
        'subcat_postamble',
        //'input_status',
    ];

    public function optionalPriorities()
    {
        return $this->hasMany(OptionalPriorities::class, 'subcat_id', 'subcat_id');
    }

    public function optionalPriorityCategory()
    {
        return $this->belongsTo(OptionalPriorityCategories::class, 'cat_id', 'cat_id');
    }
}
