<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('course_materials', function (Blueprint $table) {
            $table->boolean('ocr_enabled')->default(false)->after('page_count');
            $table->unsignedInteger('ocr_threshold')->default(0)->after('ocr_enabled');
        });
    }

    public function down(): void
    {
        Schema::table('course_materials', function (Blueprint $table) {
            $table->dropColumn(['ocr_enabled', 'ocr_threshold']);
        });
    }
};
