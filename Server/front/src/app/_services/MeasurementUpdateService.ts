import { Injectable } from '@angular/core';
import {timer, from, Observable, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { switchMap } from 'rxjs/operators'
import { AppConfig } from '../_services/app.config';
import { ToastrService } from 'ngx-toastr';


/**
* Class that polls regulary for new measurementvalues and provides them using an Observable
*/
@Injectable({ providedIn: 'root' })
export class MeasurementUpdateService {

    /**
    * Stores List with mapping chartId <-> Subject
    */
    private subjects:Record<string, Subject<any>> = {};
    /**
    * URL to pull for measurement updates
    */
    private pollUrl = AppConfig.apiUrl + "/voltageUpdate/ALL";
    /**
    * keeps track of how many subscriber we have. gets incresed from notifySubscribe and decrease from notifyUnsubscribe
    */
    private subscriberCounter = 0;
    /**
    * internal subscription to the RXJS timer.
    */
    private subscription: any;
    /**
    * Flag to control if service is running
    */
    private running: boolean = false;

    constructor(private http: HttpClient,  private toastr: ToastrService) {}

    /**
    * returns subject from cache or creates a new one.
    */
    private _getSubjectObeservable(chartId:string) {
      if(!this.subjects.hasOwnProperty(chartId)) {
        this.subjects[chartId] = new Subject<any>();
      }
      return this.subjects[chartId];
    }
    /**
    * Notifies that an observer unsubscribed from  data updates. <br>
    * if nobody is subscribed anymore the service will stop polling
    */
    public notifyUnsubscribe() {
        this.subscriberCounter-= 1;
        if(this.subscriberCounter == 0 && this.running)
          this.stop()
    }
    /**
    * Notifies that an observer subscribed for data updates. <br>
    */
    public notifySubscribe() {
      this.subscriberCounter+= 1;
      if(this.subscriberCounter > 0 && !this.running)
        this.start()
    }

    /**
    * Sends a measurement update to all observers
    */
    public sendMeasurmentUpdate(chartId:string, voltageValue:number) {
      //console.log("sending volt updt to  " + chartId + " value:" + voltageValue)
      this._getSubjectObeservable(chartId).next(voltageValue)
    }

    /**
    * stops polling
    */
    public stop() {
      this.subscription.unsubscribe();
      this.running = false;
    }

    /**
    * starts polling for measurementupdate. Uses polling time interval specified by the config
    */
    private start() {
      // Set up timer with interval  AppConfig.settings.general.timerInterval
      this.running = true;

      this.subscription =
            timer(0, AppConfig.settings.general.timerInterval)
              // if timer is triggered, get data from this.pollUrl
              .pipe(switchMap( () => from(this.http.get(this.pollUrl))))
              .subscribe(
                // we got data
                (data) => {
                  this.handlePolledData(data)
                },
                //Error occured
                response => {
                  console.log("Error while retreaving data", response);
                  this.toastr.error(response, "Error while retreaving data");
                }
              );
    }

    /**
    * function that gets executed whenever data got polled from backend
    */
    private handlePolledData(data: any) {
      // notify all subjects
      for (let chartId in this.subjects) {
        this.subjects[chartId].next(data);
      }
    }
    /**
    * Removes a measurement
    */
    private clearMessage(chartId:string) {
        this._getSubjectObeservable(chartId).next();
    }

    /**
    * Returns a observable for a given id
    * @param {string} chartId unique Id
    */
    public getVoltageUpdateObs(chartId:string): Observable<any> {
          return this._getSubjectObeservable(chartId).asObservable();
    }

}
