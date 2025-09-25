<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Queue\SerializesModels;

class CourseCreationFromUploadedFilesNotification extends Mailable
{
    use Queueable, SerializesModels;

    public $successfulCreations;
    public $unsuccessfulCreations;
    public $userName;

    /**
     * Create a new message instance.
     *
     * @return void
     */
    public function __construct($successfulCreations, $unsuccessfulCreations, $userName)
    {
        $this->successfulCreations = $successfulCreations;
        $this->unsuccessfulCreations = $unsuccessfulCreations;
        $this->userName = $userName;
    }

    /**
     * Build the message.
     */
    public function build(): static
    {
        return $this->markdown('emails.courseCreationFromUploadedFilesNotification', [ // pass public variables (set in __construct) to notifyInstructor.blade
            'successfulCreations' => $this->successfulCreations,
            'unsuccessfulCreations' => $this->unsuccessfulCreations,
            'userName' => $this->userName,
        ])
            ->subject('Courses created from uploaded syllabi files');  // set subject to Invitation to Collaborate, see Mail docs for more info.
    }
}
