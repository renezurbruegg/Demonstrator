/**
* Interface for a Dataset that will be added to a graph
*/
export interface ChartDataset {
  /**
  * ID of the dataset. must be unique
  */
  datasetId:string,
  /*
  * id of the sourcedevice. must correspond to a measurment ID.
  */
  sourceId:string,
  /**
  * Custom name for the dataset. Will be its label if option is set.
  */
  name:string,
  /**
  * Unit of the dataset
  */
  unit:string,
  /**
  * Function to transform measurement data
  */
  handler?:string,
  /**
  * Flag to enable custom function on data
  */
  customDataHandlerEnabled:boolean,

  /**
  * Options for the Dataset that will be be submitted to the chart.js object
  */
  chartDataset:ChartJsDataset,

  /**
  * Flag if label should be automatically generated from datasetName + unit
  */
  autoLabel?:boolean,
  /**
  * Flag if range of axis should be automatically set to max values of current range
  */
  autoRange?:boolean,

  /**
  * Also show negative values. Only useful if autoRange is set.
  */
  negRange?:boolean,

}

export interface ChartJsDataset {
  /**
  * fill area under chart. default false
  */
  fill?:boolean,
  /**
  * Hex String. Defines color of line in chart
  */
  borderColor?:string,
  /**
  * Label of the dataset. if autoLabel is set, this will be set automatically
  */
  label?:string,
  /**
  * ID of the yAxis that belongs to this dataset
  */
  yAxisID?:string,

  /**
  * datapoints of the dataset. will be set programmatically
  */
  data? : Array<number>,
  /**
  * Current value of this dataset, will be set programmatically
  */
  currValue? :number,
  /**
  * Private value for chart.js
  */
  _meta? : any
}
