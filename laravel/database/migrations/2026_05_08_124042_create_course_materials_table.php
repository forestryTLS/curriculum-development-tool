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
        Schema::create('course_materials', function (Blueprint $table) {
            $table->id('course_material_id');

            $table->unsignedBigInteger('course_id');
            $table->foreign('course_id')->references('course_id')->on('courses')->onDelete('cascade');

            $table->string('name');
            $table->string('type')->nullable();
            $table->text('description')->nullable();
            $table->boolean('is_required')->nullable();
            $table->string('url')->nullable();
            $table->unsignedInteger('position')->default(0);




            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('course_materials');
    }
};
