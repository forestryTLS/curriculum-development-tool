<?php 

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Gate;


class AdminAssignRoleController extends Controller{

    public function __construct()
    {
        $this->middleware(['auth', 'verified']);
    }


    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        if (Gate::denies('admin-privilege')) { // This Gate checks if user is an admin
            return redirect(route('home'));  //   and redirects to home if they are not (security)
        }

        return view('pages.assignRole');          // If they are, return email.blade page
    }
}