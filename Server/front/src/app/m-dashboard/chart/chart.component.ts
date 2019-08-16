import { Component, OnInit, AfterViewInit, Input, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { Chart } from 'chart.js';
import { MeasurementUpdateService } from '../../_services/MeasurementUpdateService';
import { AppConfig } from '../../_services/app.config';

import { ChartDataset } from '../../_models/chartDataset.model';
import { ChartObject } from '../../_models/chartObject.model';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { ToastrService } from 'ngx-toastr';




/**
* Interfaces that defines the ResponseObject of the VoltageUpdate Subscription
*/
interface DataEntry {
  /**
  * Max Value that is possible to send in this resolution => used to scale the graph
  */
   max: number;
   /**
   * e.g. V, mV, mA, uA
   */
   unit:string;
   /**
   * The value for this measurement
   */
   value:number;
}

export function scaleToSiUnit(data:DataEntry):number {
      let unit = data.unit.charAt(0)
      let multiplier = 1;

      if (unit == "m") {
        multiplier =  1/1000;
      } else if(unit == "u") {
        multiplier = 1/1000000
      }
      return data.value * multiplier;

  }

/**
* Component that creates a chart graph with reload, pause and export button.
* @example
*
* | ----------------------------------------------------------------|
* |                                        [Play][Reload][export]   |
* |        |---------------------------------|                      |
* |        |                                 |                      |
* |        |     Chart JS (chartObject)      |                      |
* |        |                                 |                      |
* |        |                                 |                      |
* |        |---------------------------------|                      |
* |                                                                 |
* | ----------------------------------------------------------------|
*
*/
@Component({
  selector: 'app-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.css']
})

export class ChartComponent implements OnInit, AfterViewInit, OnDestroy {

  /**
  * Object that stores custom transform function for every dataset.  <br>
  * This is used to created custom datasets. e.g. power calculation
  */
  private dataSetHandlerFunctions: Record<string, (data: any) => number> = {}
  /**
  * the chartobject stored in the config which contains all the information about this chart. (name, datasets etc.)
  */
  @Input()
  public chartObject: ChartObject;

  /**
  *  boolean that stores state of graph.
  */
  public paused: boolean = false;
  // message: any;

  private subscription: Subscription;

  // public currValue: string;

  /**
  * Holds the real Chart.js chart objects.
  */
  public chartLine: Chart;

  /**
  * Defines how many decimal numbers we want to show.
  */
  private precision: number = Math.pow(10, 3);


  /**
  *  Contains the last resolution for every measurement in the graph. <br>
  *  Used to find resolution changes and rescale values
  */
  private lastResolution: Record<string, string> = {}

  /**
  * Contains all the data that will be passed to the chart objects.
  */
  private data = {
    labels: [""],
    datasets: []
  };


  /**
  * Contains mapping axis id to axis position in chart.js options
  */
  idToYAxis:Record<string, number> = {}

  /**
  * @param {MeasurementUpdateService} measurementUpdateService Service that polls every <intervaltime> and publishes new measurement values using observables
  * @param {ChangeDetectorRef} cd Angular class to notify angular about frontend changes. Needed because the graph convas doesn't trigger changes on it's own when set up
  * @param {HttpClient} http http client to communicate with backend
  * @param {ToastrService} toastr Service used to create small notification on the screen
  */
  constructor(private measurementUpdateService: MeasurementUpdateService, private cd: ChangeDetectorRef, private http: HttpClient,  private toastr: ToastrService) { }

  /**
  * called when component is destroyed. Unsubscribes from VoltageUpdateSubscription
  */
  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  /**
  * Sets up a subscription from measurementUpdateService. <br>
  */
  private setUpSubscription() {

    // Add all datasets to chart
    for (let dataset of this.chartObject.datasets) {
      this.addDatasetToChart(dataset);
    }

    // Every time a measurement update is triggered call addDataToChart function
    this.subscription = this.measurementUpdateService.getVoltageUpdateObs(this.chartObject.chartId)
                                                 .subscribe(data => this.addDataToChart(data));

    // Notify service that we subscribed.
    this.measurementUpdateService.notifySubscribe();
  }

  /**
  * Called when component is created. Sets up a subscription from measurementUpdateService to get measurement Updates
  */
  ngOnInit() {
    this.setUpSubscription()
  }

  /**
  * After view element is created.  <br>
  *  Sets up Chart.js element (chartLine)
  */
  ngAfterViewInit() {
    // load options from general config
    let options = AppConfig.settings.general.chartOptions;

    // Check if there are own options set for this particular graph.
    if (this.chartObject.hasOwnProperty("options")) {
      options = this.chartObject.options;
    }

    this.setUpAxesConfig(options.scales.yAxes);

    // Set up Chart.js chart
    this.chartLine = new Chart(this.chartObject.chartId, {
      type: 'line',
      data: this.data,
      options: options
    });
    // default value
    this.paused = false;

    // Notify angular that we changed stuff
    this.cd.detectChanges();
  }



/**
* Adds data obtained from measurementUpdateService to the graph. <br>
* @param { Record<string, DataEntry>} data Record containg all measurements from backend
*/
  private addDataToChart(data: Record<string, DataEntry>): void {

    // Every dataset can decide which data it wants to use.
    for (let dataset of this.chartObject.datasets) {

      let datasetId = dataset.datasetId;
      let unit = dataset.unit;

      // get value from datasetHandlerFunction. Scale it to precision


      let value = Math.round(this.dataSetHandlerFunctions[datasetId](data) * this.precision) / this.precision;

      let lastUnit = this.lastResolution[dataset.datasetId];

      if (!lastUnit || lastUnit == "") {
        lastUnit = unit
        this.lastResolution[dataset.datasetId] = unit
      }

      if (!dataset.chartDataset.data) {
        dataset.chartDataset.data = [];
      }

      // Check if units changed. If yes, rescale all old values.
      let dataCount = dataset.chartDataset.data.length;
      if (lastUnit != "" && lastUnit != unit && dataCount) {

          console.log("found resolution change " + lastUnit + " -> " + unit)
          // We got a resolution change. Figure out if we need to down or upscale values
          let multiplier = 1;
          if (unit == "mV" || unit == "uA") {
            // V -> mV
            multiplier = 1000;
          } else if (unit == "V" || unit == "mA") {
            // mV -> V
            multiplier = 1 / 1000;
          }

          // recalculate all old datas
          for (let i = 0; i < dataCount; i++) {
            dataset.chartDataset.data[i] = dataset.chartDataset.data[i] * multiplier;
          }
          this.lastResolution[dataset.datasetId] = unit
      }


      // Add value to graph.
      dataset.chartDataset.data.push(value);
      dataset.chartDataset.currValue = value;


      // If we reached max items shift() data array so do not show too many points.
      if (dataset.chartDataset.data.length >= this.chartObject.maxValues) {
        dataset.chartDataset.data.shift();
      }

      // Create label from datasetName and unit if option is enabled
      if (dataset.autoLabel) {
        dataset.unit = data[dataset.sourceId].unit;
        dataset.chartDataset.label = dataset.name + "[" + unit + "]";
      }

      // Rescale Axis
      if (dataset.chartDataset.yAxisID && (dataset.autoRange || dataset.negRange)) {
        // Get Axis from mapping
        let axis = this.chartLine.options.scales.yAxes[this.idToYAxis[dataset.chartDataset.yAxisID]]
        if (dataset.autoRange) {
          axis.ticks.max = data[dataset.sourceId].max
          axis.ticks.min = 0
        }

        if (dataset.negRange) {
          axis.ticks.min = -data[dataset.sourceId].max;
        }
      }

    }

    // We need to push a label for the x-axis. in this case it is empty, so we do not write anything
    // If nothing is pushed, graph won't show new values
    this.data.labels.push('');

    // shift labels if maxvalues reached
    if (this.data.labels.length > this.chartObject.maxValues) {
      this.data.labels.shift();
    }

    // notify update
    this.chartLine.update()
  }

  /**
  * Adds a new dataset to the chart.  Only call this function once when setting up a new dataset.
  * @param {ChartDataset} dataset The Dataset object we want to add to the chart.
  */
  private addDatasetToChart(dataset: ChartDataset) {
    // Register in lastResolution array
    this.lastResolution[dataset.datasetId] = "";
    // Register as a dataset for this graph
    this.data.datasets.push(dataset.chartDataset);

    // Set up custom handler function if this is a "fake Dataset".
    if (dataset.customDataHandlerEnabled) {
      this.dataSetHandlerFunctions[dataset.datasetId] = function(data: DataEntry) {

        return eval(dataset.handler)
        // return scaleToSiUnit(data['vm1']) * scaleToSiUnit(data['cm3']);
      }
    } else {
      // just return the value.
      this.dataSetHandlerFunctions[dataset.datasetId] = function(data: DataEntry) {
        return data[dataset.sourceId].value;
      }
    }
  }



  /**
  * Removes all points from Graph. <br>
  */
  public clear() {
    for (let dataset of this.chartObject.datasets) {
      dataset.chartDataset.data = [];
      this.lastResolution[dataset.datasetId] = "";
    }

    this.data.labels = [];
    this.chartLine.update();

    if (this.paused) {
      this.togglePlay();
    }
  }

  /**
  * Exports the current graph as image. Sends image as base64 string to the backend.
  */
  public exportImage() {
    this.http.post(AppConfig.apiUrl + "/storeImage", { "image": this.chartLine.ctx.canvas.toDataURL() }, { responseType: 'text' })
      .subscribe(
        (val) => {
          this.toastr.success('Image exported');
       },
        response => {
         this.toastr.error(response, "Could not export Image");
        });
  }



  /**
  * sets up the axis of the chart.
  */
  private setUpAxesConfig(axes:Array<any>) {
    axes.length = 0;

    if(this.chartObject.axes) {
      let i = 0;
      for (let axis of this.chartObject.axes) {
        var entry = {
              id: axis.id,
              type: "linear",
              position: axis.position,
              ticks: {}
          }

        axes.push(entry)
        this.idToYAxis[axis.id] = i++;
      }
    }
  }
  /**
  * TODO
  */
  public exportCsv() {
    console.log("exp csv")
    let obj:Record<string,Array<any>> = {};
    for (let dataset of this.chartObject.datasets) {
      obj[dataset.name] = dataset.chartDataset.data
    }
    this.http.post(AppConfig.apiUrl + "/storeCsv", obj, { responseType: 'text' })
      .subscribe(
        (val) => {
          this.toastr.success('CSV exported');
       },
        response => {
         this.toastr.error(response, "Could not export CSV");
        });
  }

  /**
  * halts / resumes adding of values to the graph.
  */
  public togglePlay() {
    //console.log("play called")
    if (!this.paused) {
      this.paused = true;
      this.subscription.unsubscribe();
      this.measurementUpdateService.notifyUnsubscribe();
    } else {
      this.paused = false;
      this.subscription = this.measurementUpdateService.getVoltageUpdateObs(this.chartObject.chartId)
                                                    .subscribe(data => this.addDataToChart(data));
      this.measurementUpdateService.notifySubscribe();
    }
  }
}
