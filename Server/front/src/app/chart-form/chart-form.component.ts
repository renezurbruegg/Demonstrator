import { Component, OnInit } from '@angular/core';
import { AppConfig } from '../_services/app.config';
import { ChartObject, ChartAxis } from '../_models/chartObject.model';
import { HttpClient } from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';
import { MeasurementDevice } from '../_models/app-config.model';

/**
* Component to add / edit and delete charts from the dashboard
*/
@Component({
  selector: 'app-chart-form',
  templateUrl: './chart-form.component.html',
  styleUrls: ['./chart-form.component.css']
})
export class ChartFormComponent implements OnInit {

  /**
  * Array containing all charts shown in dashboard
  */
  public chartObjects: Array<ChartObject>;
  /**
  * Object that is currently selected in the frontend
  */
  public selectedObject: ChartObject;
  /**
  * index of the currently selected deice
  */
  public selectedDeviceNumb: number = 0;
  /**
  * Array containing all avaiable measurement device
  */
  public devices: Array<MeasurementDevice>;


  constructor(private http: HttpClient, private toastr: ToastrService) { }

  ngOnInit() {
    this.chartObjects = AppConfig.settings.charts;
    this.selectedObject = this.chartObjects[0];
    this.devices = AppConfig.settings.devices;
  }

  /**
  * Sends changes on chart array to the backend.
  */
  public storeSettings() {
    // Remove pirvate values before storing config.
    AppConfig.clear();
    this.http.post(AppConfig.apiUrl + "/update/chartConfig", this.chartObjects, { responseType: 'text' })
      .subscribe(
        (val) => {
          console.log("POST call successful value returned in body",
            val);
          this.toastr.success('Changes stored successfully');
        },
        response => {
          console.log(response)
          this.toastr.error(response, "Could not store changes");
        });

  }

  /**
  * Deletes a axis that belongs to a chart object.
  */
  public deleteAxis(axis: ChartAxis) {
    for (let i = 0; i < this.selectedObject.axes.length; i++) {
      if (this.selectedObject.axes[i] == axis) {
        this.selectedObject.axes.splice(i, 1);
        break;
      }
    }
  }

  /**
  * Adds a new axis to the selected chartobject
  */
  public addAxis() {
    if (!this.selectedObject.axes) {
      this.selectedObject.axes = []
    }
    this.selectedObject.axes.push(
      {
        id: "yAxis",
        position: "left"
      }
    );
  }

  /**
  * Adds a new dataset to the selected chartobject. Datasetid is the current timestamp
  */
  public addDataset() {
    this.selectedObject.datasets.push({
      datasetId: "dataset-" + new Date().getTime(),
      sourceId: "",
      name: "",
      unit: "",
      handler: "",
      customDataHandlerEnabled: false,
      chartDataset: {
        fill: false
      }
    });
  }

  /**
  * Deletes the currently selected chart object
  */
  public deleteChart() {
    for (let i = 0; i < this.chartObjects.length; i++) {
      if (this.chartObjects[i] == this.selectedObject) {
        this.chartObjects.splice(i, 1);
        break;
      }
    }
    if (this.chartObjects.length > 0) {
      this.selectedObject = this.chartObjects[0]
    } else {
      this.chartObjects = undefined;
    }
  }

  /**
  * Adds a new chartobject to the array
  */
  public addChart() {
    let chart = {
      chartId: "chart" + new Date().getTime(),
      maxValues: 20,
      datasets: [],
      name: "new Chart",
      col: {
        lg: 6,
        md: 12,
        sm: 12,
        xs: 12
      },
    }
    this.chartObjects.push(chart);
    this.selectedObject = chart;
  }

  /**
  * Change the selected chartObject. Triggered whenever dropdown selection (selectedDeviceNumb) changes
  */
  public updateSelectedDevice() {
    this.selectedObject = this.chartObjects[this.selectedDeviceNumb];
  }

  /**
  * Deltes a dataset from the currently selected chart.
  * @param {string} datasetId the id of the dataset which should be removed
  */
  public deleteDataset(datasetId:string) {
    for (let i = 0; i < this.selectedObject.datasets.length; i++) {
      if (this.selectedObject.datasets[i].datasetId == datasetId) {
        this.selectedObject.datasets.splice(i, 1);
        return;
      }
    }
  }
}
