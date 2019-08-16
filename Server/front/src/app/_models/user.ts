/**
* Custom user object to store information about the user that is currently logged in
*/
﻿export class User {
    /**
    * currently not used
    */
    id: number;
    /**
    * currently not used
    */
    username: string;
    /**
    * currently not used
    */
    password: string;
    /**
    * currently not used
    */
    firstName: string;
    /**
    * currently not used
    */
    lastName: string;
    /**
    * JWT token. Gets returned from backend to verify that user is logged in
    */
    token?: {
        /**
        * The jwt token
        */
        jwt : string,
        /**
        * expiry date
        */
        JWT_EXPIRES : string
      };
}
