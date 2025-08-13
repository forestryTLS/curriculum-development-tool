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
        Schema::create('course_description', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('course_id')->unique();
            $table->foreign('course_id')->references('course_id')->on('courses')->onDelete('cascade');
            $table->longText('description')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('course_description');
    }
};
