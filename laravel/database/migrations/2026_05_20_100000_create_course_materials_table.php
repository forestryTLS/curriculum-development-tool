<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('course_materials', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('course_id');
            $table->foreign('course_id')->references('course_id')->on('courses')->onDelete('cascade');
            $table->unsignedBigInteger('uploaded_by')->nullable();
            $table->foreign('uploaded_by')->references('id')->on('users')->onDelete('set null');
            $table->string('file_name'); // Just for display, can make user-changeable in future
            $table->string('file_path');
            $table->unsignedInteger('file_size');
            $table->string('status', 16)->default('PENDING');
            $table->text('error_message')->nullable();
            $table->unsignedInteger('page_count')->nullable();
            // TODO: See if ocr_enabled and extraction_engine can just be combined into
            //       a single 'ocr_engine' column which can be NULL, 'tesseract', or 'textract'
            $table->boolean('ocr_enabled')->default(false);
            $table->unsignedInteger('ocr_threshold')->default(0); // Used only for Tesseract
            $table->string('extraction_engine')->default('tesseract');
            // processing_time_seconds created to compare models, can drop in future
            $table->unsignedInteger('processing_time_seconds')->nullable();
            $table->timestamps();

            $table->index('course_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('course_materials');
    }
};
