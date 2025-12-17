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
        Schema::table('course_programs', function (Blueprint $table) {
            $table->boolean('manual_map_status')->default(false);
            $table->boolean('ai_suggestion_status')->default(false);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('course_programs', function (Blueprint $table) {
            $table->dropColumn('manual_map_status');
            $table->dropColumn('ai_suggestion_status');
        });
    }
};
