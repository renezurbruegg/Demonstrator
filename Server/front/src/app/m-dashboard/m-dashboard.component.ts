import { Component, OnDestroy } from '@angular/core';
import { AppConfig } from '../_services/app.config'
import {MeasurementUpdateService} from '../_services/MeasurementUpdateService';
import { ChartObject } from '../_models/chartObject.model';


/**
* Component that creates the dashboard. <br>
* Simple container that holds all chart components
*/
@Component({
  selector: 'app-m-dashboard',
  templateUrl: './m-dashboard.component.html',
  styleUrls: ['./m-dashboard.component.css']
})
export class MDashboardComponent implements OnDestroy {
  chartObjects: Array<ChartObject>;

  /**
  * @param{MeasurementUpdateService} measurementUpdateService update service that polls for new measurement data. <br>
  * Reference needed so polling can be terminated once the dashboard is not visible anymore
  */
  constructor(private measurementUpdateService: MeasurementUpdateService) {
    // load chartobject from config
    this.chartObjects = AppConfig.settings.charts;
  }

  /**
  * Makes sure that voltage polling serves stops, when dashboard is no longer visible
  */
  ngOnDestroy() {
    this.measurementUpdateService.stop();
  }
}
