import { ChartDataset } from './chartDataset.model';

/**
* Interface defining a ChartObject stored in settings
*/
export interface ChartObject {
  /**
  * Max number of values on graph.
  */
  maxValues: number;
  /**
  * Name of the chart (Title)
  */
  name:string,
  /**
  * Array containing all Datasets that belong to this Chart
  */
  datasets: Array<ChartDataset>,
  /**
  * ID, must be unique
  */
  chartId:string,
  /**
  * Custom chart options (See Chart.js documentation). These will overwrite the objects from general config
  */
  options?:any,

  /**
  * Different y Axis that are on this chart
  */
  axes?: Array<ChartAxis>
}

/**
* Interface to define different axes on this chart.
*/
export interface ChartAxis {
  /**
  * Position of the axis <left|right>
  */
  position:string,
  /**
  * Unique ID for this axis.
  */
  id: string
}
