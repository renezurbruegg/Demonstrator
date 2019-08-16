import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AuthenticationService } from '../_services';

/**
* Class to show a modal login window to log a user in.
*/
@Component({ templateUrl: 'login.component.html' })
export class LoginComponent implements OnInit {
    loginForm: FormGroup;
    loading = false;
    submitted = false;
    /**
    * Url to the page where to login should redirect
    */
    returnUrl: string;
    /**
    * Variable to store errors and show them
    */
    error = '';
    isEmpty = true;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private authenticationService: AuthenticationService
    ) { }



    /**
    * navigates back to the dashboard component. Used if cancel button is pressed
    */
    public goBack() {
        this.router.navigate(["/dashboard"]);
    }

    /**
    * Removes last number entered in the pin field
    */
    public removeLastNumber() {
        let value = this.f.password.value;
        this.f.password.setValue(value.substring(0,value.length - 1));
    }
    /**
    * Adds a number to the password field
    * @param {number} number Number that should be appended to the text field
    */
    public onClickMe(number:number) {
      this.f.password.setValue(this.f.password.value + number);
    }


    ngOnInit() {
      // Set up login form
        this.loginForm = this.formBuilder.group({
            username: ['test', Validators.required],
            password: ['', Validators.required]
        });
        // Update remove last number button
        this.f.password.valueChanges.subscribe(e => this.isEmpty = (e == "" ) );
        // reset login status
        this.authenticationService.logout();

        // get return url from route parameters or default to '/'
        this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/settings';
    }

    // convenience getter for easy access to form fields
    get f() { return this.loginForm.controls; }

    /**
    * Submits the form to the backend
    */
    public onSubmit() {
        this.submitted = true;

        // stop here if form is invalid
        if (this.loginForm.invalid) {
            return;
        }

        this.loading = true;
        this.authenticationService.login(this.f.username.value, this.f.password.value)
            .pipe(first())
            .subscribe(
                data => {
                    this.router.navigate([this.returnUrl]);
                },
                error => {
                    this.error = error;
                    this.loading = false;
                    this.f.password.setValue("");
                });
    }
}
