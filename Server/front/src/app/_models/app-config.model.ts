import {VarSupply} from './varSupply.model';
import { ChartObject } from './chartObject.model';


/**
* Interface do define configuration of a measurement device
*/
export interface MeasurementDevice {
  /**
  * flag to enable backend to automatically change resolution when the max value is reached
  */
  autoResolution: boolean,
  /**
  * Type of the measurement <voltage/current>
  */
  type: string,
  /**
  * Current resolution.<br>
  * Normaly the following mapping is used. Can be changed in deployment part
  * @example
  * Current Device:
  * 1 <-> 500uA
  * 2 <-> 500mA
  * Voltage Device:
  * 1 <-> 50mV
  * 2 <-> 500mV
  * 3 <-> 5V
  */
  currentResolution: number,
  /**
  * Id of the measurment device. <br>
  * Must match with the id set in Devices.py
  */
  deviceId: string,
  /**
  * Custom name for the device
  */
  name: string,
  /**
  * only internal use
  */
  desiredResolution?:number,
  /**
  * only internal use
  */
  oldName?:string,

}


/**
* Interface for the app config.
*/
export interface IAppConfig {
    /**
    * Contains all the charts that are displayed in th dashboard
    */
    charts: Array<ChartObject>,
    /**
    * Contains all supplies suported by the PCB board
    */
    supplies: Array<VarSupply>,
    /**
    * Contains all the measurement devices (ADS885 chips)
    */
    devices:Array<MeasurementDevice>,

    /**
    * Contains the information to get the frontend running.
    */
    deployment : {
        /**
        * Current host for backend. is set every time the app boots
        */
        host:string,
        /**
        * The port where the backend is running. Usually 8080
        */
        apiPort:string,
        /**
        * Link to the api path. normalli just /api
        */
        apiLink:string,
        /**
        * Protcol which is used. Currently only suporting http
        */
        protocol:string
    },
    /**
    * General information for the frontend
    */
    general : {
      /**
      * How often datavalues should be refreshed. <br>
      * number in ms
      */
      timerInterval: number,
      /**
      * Array mapping index to resolution range. Used to display resolution ranges
      */
      voltageResolutionMap : Array<string>,
      /**
      * Array mapping index to resolution range. Used to display resolution ranges
      */
      currentResolutionMap : Array<string>,
      /**
      * Custom options object used in chart. See chart.js documentation
      */
      chartOptions?: any
    };
}
