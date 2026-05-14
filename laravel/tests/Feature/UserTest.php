<?php

namespace Tests\Feature;

use App\Models\Invite;
use App\Models\User;
use Carbon\Carbon;
use Tests\TestCase;

class UserTest extends TestCase
{
    /**
     * A basic feature test example.
     */

    /*
    public function test_example()
    {
        $response = $this->get('/');

        $response->assertStatus(200);
    }
    */
    public function test_register_user(): void
    {
        $response = $this->post(route('register'), [
            'name' => 'Test Register',
            'email' => 'test.register@ubc.ca',
            'password' => 'password',
            'password_confirmation' => 'password',
        ]);

        $this->assertDatabaseHas('users', [
            'name' => 'Test Register',
            'email' => 'test.register@ubc.ca',
        ]);
    }

    public function test_login_user(): void
    {
        $response = $this->post(route('login'), [
            'email' => 'test.register@ubc.ca',
            'password' => 'password',
        ]);

        $user = User::where('email', 'test.register@ubc.ca')->first();

        $response->assertStatus(302);
        $response->assertRedirect('home');
        $this->assertAuthenticatedAs($user);
    }

    public function test_user_invite(): void
    {
        // InviteController has middleware(['auth', 'verified']) and its store()
        // method requires user_id in the request body. The user created via the
        // public register route does not have email_verified_at set, so mark
        // them verified here before invoking the protected endpoint.
        $user = User::where('email', 'test.register@ubc.ca')->first();
        $user->email_verified_at = Carbon::now();
        $user->save();

        $response = $this->actingAs($user)->post(route('storeInvitation'), [
            'email' => 'test.register-invite@ubc.ca',
            'user_id' => $user->id,
        ]);

        $this->assertDatabaseHas('invites', [
            'email' => 'test.register-invite@ubc.ca',
        ]);
    }

    /*
    public function test_recover_password(): void
    {
        // No assertions yet; needs assertions about response status and
        // the password_resets table before being useful.
        $response = $this->post(route('password.email'), [
            'email' => 'test.register@ubc.ca',
        ]);
    }
    */

    /*
    public function testVerifyEmailValidatesUser(): void
    {
        // Broken: $notification->toMail() requires a Notification class;
        // App\Models\Invite is an Eloquent model with no toMail() method.
        $notification = new Invite();
        $user = User::where('email', 'test.register@ubc.ca')->first();

        $this->assertFalse($user->hasVerifiedEmail());

        $mail = $notification->toMail($user);
        $uri = $mail->actionUrl;

        $this->actingAs($user)->get($uri);

        $this->assertTrue(User::find($user->id)->hasVerifiedEmail());

        User::where('email', 'test.register@ubc.ca')->delete();
    }
    */
}