import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { IAppConfig } from '../_models/app-config.model';
import { ToastrService } from 'ngx-toastr';
import { timeout, catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';


/**
* Class to load the configuration of the frontend.
*/
@Injectable()
export class AppConfig {

  /**
  * Contains the Configuration of the app.
  */
  public static settings: IAppConfig;

  /**
  * Path to the hosts.json file. Contains different IP-Adresses on which the client should look for the backend server <br>
  * Since a host connecting to the RPI will run the same script we need to be able to use different IP's for the backend then just localhost
  */
  private hostspath: string = "assets/config/hosts.json";

  // private apiPath: string = "http://localhost:8080/api";
  /**
  * Fallback to the local config file. If no backend is found, this config will be used to make sure the frontend can boot
  */
  private fallbackConfPath: string = "assets/config/config.json";

  // /**
  // * The host for the backend. <br>
  // * Value gets set
  // */
  // private host: string;

  constructor(public http: HttpClient, private toastr: ToastrService) { }

  /**
  * Return the url leading to the API path. <
  */
  static get apiUrl(): string {
    let deploymentInfo = AppConfig.settings.deployment;
    return deploymentInfo.protocol + "://" + deploymentInfo.host + ":" + deploymentInfo.apiPort + deploymentInfo.apiLink;
  }

  /**
  * Removes all elements that start with a underscore "_". <br>
  * @param {any} obj the object whose properties should be removed
  * @param {number} level how deep we should go to remove properties
  */
  private static removePrivateValues(obj: any, level: number) {
    if (level == 0)
      return;

    for (let key in obj) {
      // console.log("key:" + key)
      // console.log(key)
      if (key.startsWith("_")) {
        delete obj.key;
        console.log("deleted" + key)
        continue;
      }
      AppConfig.removePrivateValues(obj[key], level - 1);

    }
  }

  /**
  * Removes values from the config object which should not be stored. <br>
  * e.g. private values, values that got generated from chart.js etc.
  */
  public static clear() {
    console.log("clear")
    for (let chart of AppConfig.settings.charts) {
      for (let dataset of chart.datasets) {
        // we do not want to store old data
        delete dataset.chartDataset.data;
        delete dataset.chartDataset._meta;
      }
    }
    AppConfig.removePrivateValues(AppConfig.settings, 15);
  }


  /**
  * Stores the appconfig file on the backend server. <br>
  * shows a notification if the operation was successful
  */
  public storeSettings(): void {
    this.http.post(AppConfig.apiUrl + "/storeconfig", AppConfig.settings, { responseType: 'text' })
      .subscribe(
        (val) => {
          console.log("POST call successful value returned in body",
            val);
          this.toastr.success('Settings stored successfully');
        },
        response => {
          console.log(response)
          this.toastr.error(response, "Could not store Settings");
        });
  }

  /**
  * Tries to find a working host from hostlist.<br>
  * If found the resolve function we be called and the function terminates. <br>
  * Otherwise the errorCallback will be called if no host is found.
  */
  private findWorkingHost(hostlist: Array<string>, position:number, resolve : () => void, errorCallback : () => void) {

    if (position >= hostlist.length) {
      // No host was found.
      errorCallback();
      return;
    }


    let path = "http://" + hostlist[position] + ":8080/api/loadconfig";
    console.log("trying to find working host on : " + path)

    this.http.get<any>(path)
      // check if server answers during 3s
      .pipe(timeout(3000),
        catchError((e, c) => {return throwError(e) }))
        .subscribe(data => {
        // host found. -> load settings and set host.
        AppConfig.settings = <IAppConfig>data;
        AppConfig.settings.deployment.host = hostlist[position];
        // Call resolve function
        resolve();
      }, err => {
        // Try next host
        this.findWorkingHost(hostlist, ++position, resolve, errorCallback);
        console.log(' error which is ->', err);
      });
  }


  /**
  * Loads the config from the backend and stores it in the settings object <br>
  * @return a Promise that is resolved as soon as the config is loaded
  */
  public load() {
    return new Promise<void>((resolve, reject) => {
      // load host.json file
      this.http.get(this.hostspath).toPromise().then(
        (response: any) => {
          console.log(response)

          // check hosts one for one, trying to find a working one.
          this.findWorkingHost(response.hosts, 0, resolve,
            // error callback
            () => {
              // could not find a host.-> try to use local config instead
              console.log("Could not laod config fromhosts going to fallback mode. Trying to load file from: " + this.fallbackConfPath);
              this.http.get(this.fallbackConfPath).toPromise().then((response: IAppConfig) => {
                // Get fallback config
                AppConfig.settings = <IAppConfig>response;
                resolve();
              }).catch((response: any) => {
                // Error could not load fallback config ->  reject
                reject(`Could not load file '${this.fallbackConfPath}': ${JSON.stringify(response)}`);
              });
          });
        }
      ).catch((response: any) => {
        reject(`Could not load file '${this.fallbackConfPath}': ${JSON.stringify(response)}`);
      });
    });
  };

}
