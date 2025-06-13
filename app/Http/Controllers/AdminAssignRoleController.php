<?php 

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Gate;
use App\Models\Campus;
use App\Models\Department;
use App\Models\Faculty;
use App\Models\Program;
use App\Models\User;
use App\Models\Role;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

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

        $campuses = Campus::all();
        $faculties = Faculty::orderBy('faculty')->get();
        $departments = Department::orderBy('department')->get();
        $programs = Program::orderBy('program')->get();

        return view('pages.assignRole')->with('campuses', $campuses)->with('faculties', $faculties)->with('departments', $departments)->with('programs', $programs);
    }

    public function store(Request $request): RedirectResponse
    {
        //
        $this->validate($request, [
            'email' => 'required',
            'role' => 'required',
            'campus' => 'required_if:role,deprtment-head',
            'faculty' => 'required_if:role,deprtment-head',
            'department' => 'required_if:role,deprtment-head', 
            'program' => 'required_if:role,program-direactor'
        ]);

        if($request->input('role')=='deprtment-head' && $request->input('campus') == "Other"){
            $request->validate([
                'campus-text' => 'required',
                'faculty-text' => 'required',
                'department-text' => 'required'
            ]);
        }

        if($request->input('role')=='deprtment-head' && $request->input('faculty') == "Other"){
            $request->validate([
                'faculty-text' => 'required',
                'department-text' => 'required'
            ]);
        }

        if($request->input('role')=='deprtment-head' && $request->input('department') == "Other"){
            $request->validate([
                'department-text' => 'required'
            ]);
        }

        $user = User::where('email', $request->input('email'))->first();
        
        if(!$user){
            return back()->with('error', 'User not found');
        }

        if($request->input('role')=='admin'){
            $role = Role::where('role', 'administrator')->first();
            $user->roles()->save($role);
        }

        return redirect()->back()->with('success', 'User successfully assigned role');

    }
}