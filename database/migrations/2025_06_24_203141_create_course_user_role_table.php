<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('course_user_role', function (Blueprint $table) {
            $table->id();
            $table->timestamps();
            $table->unsignedBigInteger('course_id');
            $table->foreign('course_id')->references('course_id')->on('courses')->constrained()->onDelete('cascade');
            $table->unsignedBigInteger('user_id');
            $table->unsignedBigInteger('role_id')->nullable();
            $table->foreign(['user_id', 'role_id'])->references(['user_id', 'role_id'])->on('role_user')->onDelete('cascade');
            $table->unsignedBigInteger('program_id')->nullable();
            $table->foreign('program_id')->references('program_id')->on('programs')->constrained()->onDelete('cascade');
            $table->unsignedBigInteger('department_id')->nullable();
            $table->foreign('department_id')->references('department_id')->on('departments')->onDelete('cascade');
            $table->unique(['course_id', 'user_id', 'role_id', 'program_id', 'department_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('course_user_role');
    }
};
