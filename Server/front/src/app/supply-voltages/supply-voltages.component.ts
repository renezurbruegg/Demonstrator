import { Component, OnInit, Inject } from '@angular/core';
import { AppConfig } from '../_services/app.config';
import { IAppConfig } from '../_models/app-config.model';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { VarSupply } from '../_models/varSupply.model';
import { HttpClient} from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';


/**
* Inteface used to define the structure of the data that is shown in the confirmationdialog
*/
interface ConfirmationDialogData {
  /**
  * Array containing name, oldValue and newValue information. These information will be shown like follows:
  * @example
  * [name] : [oldValue] -> [newValue]
  */
    values: Array<{
      "name": string,
      "oldValue": any,
      "newValue": any
    }>,
    /**
    * The Object that gets send to the backend if the dialog is confirmed.
    * <br> this will be the content of the post request
    */
    submitObject: any,
    /**
    *  The part of the url following the /api <callPath> which will get called if the dialog is confirmed
    */
    callPath: string
}
/**
* General Dialog used to show and confirm changes to an object.
*/
@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
})
export class ConfirmDialog {

  /**
  * Creates the dialog.
  * @param {HttpClient} http httpclient used to send api requests to the backend
  * @param {MatDialogRef} dialogRef reference to show the dialog
  * @param{ConfirmationDialogData} data Data containing the changes the user needs to confirm.
  */
  constructor(
    public http: HttpClient,
    public dialogRef: MatDialogRef<ConfirmDialog>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmationDialogData,
    private toastr: ToastrService
  ) { }

  /**
  * If no is clicked , close dialog and notify listeners
  */
  public onNoClick(): void {
    this.dialogRef.close(false);
  }

  /**
  * Calls backendPath with the submit object. Shows notification to inform if request was successful
  */
  public onYesClick(): void {
    this.http.post(AppConfig.apiUrl + this.data.callPath, this.data.submitObject, { responseType: 'text' })
      .subscribe(
        (val) => {
          console.log("POST call successful value returned in body",
            val);
          this.toastr.success('Values set successfully');
          this.dialogRef.close(true);
        },
        response => {
          console.log(response)
          this.toastr.error(response, "Could not set Values");
          this.dialogRef.close(false);
        });
  }
}




/**
* Component used to configure the different supply voltages on the board. <br>
* Lets the user disable/enable different supplies and choose their voltages
*/
@Component({
  selector: 'app-supply-voltages',
  templateUrl: './supply-voltages.component.html',
  styleUrls: ['./supply-voltages.component.css']
})
export class SupplyVoltagesComponent implements OnInit {
  /**
  * Object containing the settings object.
  */
  public settings: IAppConfig;

  constructor(public dialog: MatDialog) { }

  /**
  * Opens the confirmation dialog to make sure if the user wants to make the changes
  */
  public openDialog(): void {
    // Map supplies obejct to list with old and new value which will be displayed in the dialog
    let updates = this.settings.supplies.map(supply => {
      if (supply.enabled) {
        return {
          name: supply.name,
          oldValue: supply.currentVoltage,
          newValue: supply.desiredVoltage
        };
      }
      return {
        name: supply.name,
        oldValue: supply.currentVoltage,
        newValue: "Disabled"
      };
    });



  const dialogRef = this.dialog.open(ConfirmDialog, {
      width: '400px',
      data: { values: updates, submitObject: this.settings.supplies, callPath: "/updateDeviceVoltages" }
    });

    dialogRef.afterClosed().subscribe(succesfull => {
      if (succesfull) {
        for (let supply of this.settings.supplies) {
          supply.currentVoltage = supply.desiredVoltage
        }
      }
    });
  }

  /**
  * Checks if the inputs are valid and can be set
  */
  get validInputs(): boolean {
    for (let device of this.settings.supplies) {
      if ((device.desiredVoltage < device.minValue || device.desiredVoltage > device.maxValue) && (device.maxFix != device.desiredVoltage) ) {
        return false;
      }
    }
    return true;
  }


  ngOnInit() {
    this.settings = AppConfig.settings;
  }

  /**
  * @ignore
  */
  onSubmit() {
    for (let sup of this.settings.supplies) {
      if (sup.maxValueChecked) {
        sup.desiredVoltage = sup.maxFix;
      }
    }
    this.openDialog();
  }
}
