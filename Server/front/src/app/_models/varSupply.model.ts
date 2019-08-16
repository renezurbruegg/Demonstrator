/**
* Interface for the config entry concerning VarSupplies
*/
export interface VarSupply {
  /**
  * Name of the VarSupply. Must be unique and corelate with the name given in the backend
  */
  name:string,
  /**
  * Min stepsize that the voltage can be increased
  */
  stepSize: number,
  /**
  * Current voltage value
  */
  currentVoltage:number,
  /**
  * Lowest value for the voltage
  */
  minValue:number,
  /**
  * highest value for the voltage that can be set using the slider
  */
  maxValue:number,
  /**
  * Unit of the var supply. currently only [V] only supported
  */
  unit:string,
  /**
  * Boolean if supply is enabled
  */
  enabled:boolean,
  /**
  * Voltage we want to set on the varsuplly
  */
  desiredVoltage?:number,
  /**
  * If maxvalue is checked. Since there is a bug that in full scale mode we output 3.5V instead of 3.3 we had to create this flag
  */
  maxValueChecked?:boolean,
  /**
  * Max value that can be achieved by clicking the checkbox
  */
  maxFix?:number
}
