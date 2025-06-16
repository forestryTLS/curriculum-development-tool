<?php

namespace App\Models;

use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable implements MustVerifyEmail
{
    use \Backpack\CRUD\app\Models\Traits\CrudTrait;
    use HasFactory, Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    /**
     * The attributes that should be hidden for arrays.
     *
     * @var array
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    /**
     * The attributes that should be cast to native types.
     *
     * @var array
     */
    protected $casts = [
        'email_verified_at' => 'datetime',
    ];

    public function roles()
    {
        return $this->belongsToMany(\App\Models\Role::class);
    }

    public function courses()
    {
        return $this->belongsToMany(\App\Models\Course::class, 'course_users', 'user_id', 'course_id')->withPivot('permission');
    }

    public function programs()
    {
        return $this->belongsToMany(\App\Models\Program::class, 'program_users', 'user_id', 'program_id')->withPivot('permission','role_id');
    }

    public function syllabi()
    {
        return $this->belongsToMany(\App\Models\syllabus\Syllabus::class, 'syllabi_users', 'user_id', 'syllabus_id')->withPivot('permission');
    }

    public function headedDepartments()
    {
        return $this->belongsToMany(\App\Models\Department::class, 'department_head');
    }

    public function directedProducts()
    {
        $directorRoleId = Role::where('role', 'program director')->first()->id;

        return $this->programs()
                    ->withPivot('permission','role_id')
                    ->wherePivot('role_id', $directorRoleId);
    }

    public function hasAnyRoles($roles)
    {
        if ($this->roles()->whereIn('role', $roles)->first()) {
            return true;
        }

        return false;
    }

    public function hasRole($role)
    {
        if ($this->roles()->where('role', $role)->first()) {
            return true;
        }

        return false;
    }
}
