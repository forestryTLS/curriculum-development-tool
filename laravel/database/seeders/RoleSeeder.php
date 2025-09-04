<?php

namespace Database\Seeders;

use App\Models\Role;
use Illuminate\Database\Seeder;

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        //
        //Role::delete();
        Role::create(['role' => 'administrator']);
        Role::create(['role' => 'program director']);
        Role::create(['role' => 'department head']);
        Role::create(['role' => 'user']);

    }
}
