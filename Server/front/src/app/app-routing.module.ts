import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MDashboardComponent } from './m-dashboard/m-dashboard.component';
import { AuthGuard } from './_guards';
import {LoginComponent} from './login/login.component';
import { SupplyVoltagesComponent } from './supply-voltages/supply-voltages.component';
import {VideostreamComponent} from './videostream/videostream.component';
import { ChartFormComponent } from './chart-form/chart-form.component';
import { EditorComponent } from './editor/editor.component';
import { GeneralSettingsComponent } from './general-settings/general-settings.component';
import { MeasurementConfigurationComponent } from './measurement-config/measurement-config.component';

/**
* Array containing all paths<->Components  the application knows. 
*/
const routes: Routes = [
  { path: 'dashboard', component:MDashboardComponent },
  { path: '', component:MDashboardComponent },
  { path: 'login', component: LoginComponent },
  { path: 'video', component: VideostreamComponent },
  // Routes that require the user to be logged in
  { path: 'settings', component: SupplyVoltagesComponent, canActivate: [AuthGuard] },
  { path: 'chartsettings', component: ChartFormComponent, canActivate: [AuthGuard]},
  { path: 'measDevices', component:MeasurementConfigurationComponent, canActivate: [AuthGuard]},
  { path: 'general', component: GeneralSettingsComponent, canActivate: [AuthGuard]},
  { path: 'editor', component:EditorComponent, canActivate: [AuthGuard]}
  ];
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
