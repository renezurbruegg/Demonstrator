import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { map } from 'rxjs/operators';

import { User } from '../_models';
import { AppConfig } from './app.config';



@Injectable({ providedIn: 'root' })
export class AuthenticationService {
    private currentUserSubject: BehaviorSubject<User>;
    public currentUser: Observable<User>;

    constructor(private http: HttpClient) {
        this.currentUserSubject = new BehaviorSubject<User>(JSON.parse(localStorage.getItem('currentUser')));
        this.currentUser = this.currentUserSubject.asObservable();
    }

    /**
    * @returns the userSubject. Updates will be triggered whenever somebody logs in or out
    */
    public getCurrentUserObservable(): BehaviorSubject<User> {
      return this.currentUserSubject;
    }

    /**
    * @returns the current user.
    */
    public get currentUserValue(): User {
        return this.currentUserSubject.value;
    }

    /**
    * @returns true if user is logged in, false otherwise
    */
    public isLoggedIn() {
      if (this.currentUserValue) {
        return true;
      }
      return false
    }

    /**
    * tries to log in using the given credentials. <br>
    * If login is succesfully a user object with a JWT token is stored in the currentUser variable.
    * @param {string} username a username for the user. currently not used in backend
    * @param{string} password the password
    */
    public login(username: string, password: string) {
        return this.http.post<any>(AppConfig.apiUrl + "/login", { username, password })
            .pipe(map(user => {
                // login successful if there's a jwt token in the response
                if (user && user.token) {
                    // store user details and jwt token in local storage to keep user logged in between page refreshes
                    localStorage.setItem('currentUser', JSON.stringify(user));
                    this.currentUserSubject.next(user);
                }
                return user;
            }));
    }

    /**
    * logs out a user that is currently logged in.
    */
    public logout() {
        // remove user from local storage to log user out
        localStorage.removeItem('currentUser');
        this.currentUserSubject.next(null);
    }
}
