import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';

import { AuthenticationService } from '../_services';

/**
* Adds the jwt Token to the header of every request. <br>
* Used to call API-Routes which need authorization
*/
@Injectable()
export class JwtInterceptor implements HttpInterceptor {

    constructor(private authenticationService: AuthenticationService) { }
    /**
    * Appends jwt token to every request. (If user is logged in)
    */
    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        let currentUser = this.authenticationService.currentUserValue;
        // check user and token exist.
        if (currentUser && currentUser.token) {
          // apend it to header
            request = request.clone({
                setHeaders: {
                    Authorization: `Bearer ${currentUser.token.jwt}`
                }
            });
        }
        return next.handle(request);
    }
}
