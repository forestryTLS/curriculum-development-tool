<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\CourseMaterial>
 */
class CourseMaterialFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'course_id' => Course::factory(),
            'name' => $this->faker->sentence(4),
            'type' => $this->faker->randomElement(['textbook', 'video', 'article', 'reading']),
            'description' => $this->faker->optional()->paragraph(),
            'is_required' => $this->faker->boolean(),
            'position' => $this->faker->numberBetween(0, 100),
        ];
    }
}
