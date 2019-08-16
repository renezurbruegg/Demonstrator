import { Component, OnInit } from '@angular/core';
import { AppConfig } from '../_services/app.config';
import { HttpClient } from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';


/**
* Component to set general settings like screen brightness, hotspot options etc.
*/
@Component({
  selector: 'app-general-settings',
  templateUrl: './general-settings.component.html',
  styleUrls: ['./general-settings.component.css']
})
export class GeneralSettingsComponent implements OnInit {
  configObject = {
    "brightness": 255
  }
  constructor(public http: HttpClient,private toastr: ToastrService) { }

  ngOnInit() {}

  /**
  * Sends changes to the configObject file to the backend. <br>
  * Shows a notification wheter or not it was possible
  */
  public submit() {
    this.http.post(AppConfig.apiUrl + "/updateGeneralSettings", this.configObject, { responseType: 'text' })
      .subscribe(
        (val) => {
          console.log("POST call successful value returned in body",
            val);
          this.toastr.success('Values set successfully');

        },
        response => {
          console.log(response)
          this.toastr.error(response, "Could not set Values");
        });

  }

}
