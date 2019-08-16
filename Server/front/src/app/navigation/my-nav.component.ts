import { Component } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable, timer, from } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { AuthenticationService } from '../_services';
import { NavItem } from './menu-list-item/nav-item';
import { AppConfig } from '../_services/app.config';
import { ToastrService } from 'ngx-toastr';
import { HttpClient } from '@angular/common/http';
import { MatDialogRef, MatDialog } from '@angular/material';


interface ROUTE {
  icon?: string;
  route?: string;
  title?: string;
}

/**
* The navigation component. <br>
* Creates a sidebar with different components and a toolbar showing battery percentage, log out button and temperature
*/
@Component({
  selector: 'app-my-nav',
  templateUrl: './my-nav.component.html',
  styleUrls: ['./my-nav.component.css']
})
export class MyNavComponent {
  /**
  * List containing all items shown in the sidebar
  */
  public navItems: NavItem[] = [
    {
      displayName: 'Dashboard',
      iconName: 'dashboard',
      route: '/dashboard',
      loginRequired: false,
    }, {
      displayName: 'Video',
      iconName: 'videocam',
      route: '/video',
      loginRequired: false,
    }, {
      displayName: 'Settings',
      iconName: 'settings',
      route: '/settings',
      loginRequired: true,
      children: [{
        displayName: 'Charts',
        iconName: 'show_chart',
        route: '/chartsettings',
        loginRequired: true,
      },
      {
        displayName: 'Supply Voltages',
        iconName: 'power',
        route: '/settings',
        loginRequired: true,
      },
      {
        displayName: 'Measurement',
        iconName: 'flash_on',
        route: '/measDevices',
        loginRequired: true,
      }, {
        displayName: "General",
        iconName: 'settings_input_antenna',
        route: 'general',
        loginRequired: true
      },
      {
        displayName: 'Editor',
        iconName: 'edit',
        route: '/editor',
        loginRequired: true,
      }]
    }


  ];

  /**
  * List containing all "big" dropdown navigation objects.
  */
  public routes: ROUTE[] = [
    {
      icon: 'dashboard',
      route: '/dashboard',
      title: 'Dashboard',
    },
    {
      icon: 'videocam',
      route: '/video',
      title: 'Video',
    },
    {
      icon: 'settings',
      route: '/settings',
      title: 'Settings',
    }
  ];



  /**
  * flag to show if user is logged or not. <br>
  * Used to show/hide the logout button
  */
  public loggedIn: boolean;
  /**
  * flag to store information about the sidebar.  <br>
  * if false, sidebar is always visible, if ture, sidebar can be hidden by pressing the toggle button
  */
  public isToggleEnabled = false;
  /**
  * the current battery level.
  */
  public batteryLevel: any = 0;
  /**
  * the battery icon. can be critical, loading, normal or just unknown
  */
  public batteryIcon: string = "battery_unknown";
  /**
  * Current heat of the RPI CPU
  */
  public heat: string = ""

  /**
  * Observable that gets triggered if screen size changes.  <br>
  * True if device is handset and toggle button is shown.
  */
  public isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches)
    );

  /**
  * Logs out the user that is currently logged in
  */
  public logout() {
    this.authenticationService.logout();
  }

  constructor(private breakpointObserver: BreakpointObserver, private dialog: MatDialog, private authenticationService: AuthenticationService, private http: HttpClient, private toastr: ToastrService) {  }

  /**
  * Shows a dialog to make sure if the user really wants to shut the device down
  */
  public shutdownDialog(): void {
    this.dialog.open(PowerOffDialog, {
      width: '400px'
    });
  }

  /**
  * On init creates a timer that polls every 10s for new information about Batterylevel, CPU tmp etc. <br>
  * Shows an error notification if it fails.
  */
  ngOnInit() {
    timer(0, 10000)
      .pipe(
        switchMap(() => from(this.http.get(AppConfig.apiUrl + "/getSystemInfos"))),
        )
      .subscribe((data: any) => {

        this.heat = data.temp
        this.batteryLevel = data.battery.value;

        let val = parseInt(data.battery.value)
        this.batteryIcon = "battery"
        if (data.charging) {
          this.batteryIcon += "_charging"
        }
        if (val < 10) {
          this.batteryIcon += "_alert"
        } else {
          this.batteryIcon += "_full"
        }

      },
      response => {
        console.log("Error while retreaving data", response);
        this.toastr.error(response, "Error while getting battery data");

      }
    );
    this.loggedIn = this.authenticationService.isLoggedIn();

    // Set up Listener to remove log out icon
    this.authenticationService.getCurrentUserObservable().subscribe(val =>
      this.loggedIn = this.authenticationService.isLoggedIn()
    );

    this.isHandset$.subscribe(handset => this.isToggleEnabled = handset);
  }
}








/**
* Confirmation dialog to make sure if the user really wants to shut down device.
*/
@Component({
  selector: 'app-power_off_dialog',
  templateUrl: './power_off_dialog.component.html',
})
export class PowerOffDialog {

  constructor(
    public http: HttpClient,
    public dialogRef: MatDialogRef<PowerOffDialog>,
    private toastr: ToastrService
  ) { }

  onNoClick(): void {
    this.dialogRef.close(false);
  }
  /**
  * Sends shutdown request to backend,
  */
  onYesClick(): void {
    this.http.get(AppConfig.apiUrl + "/shutdown", { responseType: 'text' })
      .subscribe(
        (val) => {
          this.toastr.success('Powering Off');
          this.dialogRef.close(true);
        },
        response => {
          this.toastr.error(response, "Error");
          this.dialogRef.close(false);
        });
  }
}
