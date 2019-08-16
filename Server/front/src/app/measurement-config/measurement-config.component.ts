import { Component, OnInit } from '@angular/core';
import { AppConfig } from '../_services/app.config';
import { ConfirmDialog } from '../supply-voltages/supply-voltages.component';
import { MatDialog } from '@angular/material';
import { HttpClient } from '@angular/common/http';
import { MeasurementDevice } from '../_models/app-config.model';


/**
* Component to edit all measurementdevices that are supported.
*/
@Component({
  selector: 'app-measurement-config',
  templateUrl: './measurement-config.component.html',
  styleUrls: ['./measurement-config.component.css']
})
export class MeasurementConfigurationComponent implements OnInit {

  /**
  * all devices that are configured
  */
  devices = AppConfig.settings.devices;
  /**
  * Only the devices that deal with voltages. set up in constructor
  */
  voltageDevices: Array<MeasurementDevice> = [];
  /**
  * Only the devices that deal with currents. set up in constructor
  */
  currentDevices: Array<MeasurementDevice> = [];
  /**
  * Map that maps a resolution number to a human readable string
  */
  voltageResolutionMap = AppConfig.settings.general.voltageResolutionMap;
  /**
  * Map that maps a resolution number to a human readable string
  */
  currentResolutionMap = AppConfig.settings.general.currentResolutionMap;

  constructor(public dialog: MatDialog, public http: HttpClient) { }

  /**
  * Opens a dialog to show changes and make sure if user wnats to confirm the changes
  */
  public openDialog(): void {
    // Add all devices to one array
    let updates = this.voltageDevices.map(device => {
      return {
        name: device.deviceId,
        oldValue: device.oldName + " : " + this.voltageResolutionMap[device.currentResolution - 1],
        newValue: device.name + " : " + this.voltageResolutionMap[device.desiredResolution - 1]
      };
    });

    let values = updates.concat(this.currentDevices.map(device => {
      return {
        name: device.deviceId,
        oldValue: device.oldName + " : " + this.currentResolutionMap[device.currentResolution - 1],
        newValue: device.name + " : " + this.currentResolutionMap[device.desiredResolution - 1]
      };
    })
    );
    // contains all devices that will be updated
    let submitObj = [].concat(this.voltageDevices).concat(this.currentDevices)

    const dialogRef = this.dialog.open(ConfirmDialog, {
      width: '400px',
      data: { values: values, submitObject: submitObj, callPath: "/update/measurementDevices" }
    });

    dialogRef.afterClosed().subscribe(succesfull => {
      if (succesfull) {
        for (let device of this.devices) {
          device.currentResolution = device.desiredResolution;
          device.name = device.oldName + "";
        }
      }
    });
  }


  /**
  * returns if inputs are valid and data can be set.
  * @TODO implement
  */
  get validInputs(): boolean {
    // for(let device of this.settings.supplies) {
    //   if (device.desiredVoltage < device.minValue || device.desiredVoltage > device.maxValue) {
    //     return false;
    //   }
    // }
    return true;
  }

  /**
  * Function that gets called once the submit button is pressed. <br>
  * opens confirmation dialog
  */
  public onSubmit() {
    this.openDialog();
  }

 /**
 * On init. load devices from config and setts desiredResolution to current resolution and oldName to current name. <br>
 * Needed to be able to show what changes in confirmation dialog
 */
  ngOnInit() {
    for (let device of this.devices) {
      device.desiredResolution = device.currentResolution + 0;
      device.oldName = device.name + "";

      if (device.type == "voltage") {
        this.voltageDevices.push(device);
      } else if (device.type == "current") {
        this.currentDevices.push(device);
      }
    }
  }

}
