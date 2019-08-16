import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MyNavComponent, PowerOffDialog } from './navigation/my-nav.component';
import { LayoutModule } from '@angular/cdk/layout';
import { MatToolbarModule, MatButtonModule, MatSidenavModule, MatIconModule, MatListModule, MatGridListModule, MatCardModule, MatMenuModule, MatDialogModule, MatExpansionModule } from '@angular/material';
import { MDashboardComponent } from './m-dashboard/m-dashboard.component';
import { ChartComponent } from './m-dashboard/chart/chart.component';
import { SupplyVoltagesComponent, ConfirmDialog } from './supply-voltages/supply-voltages.component';
import { ReactiveFormsModule }    from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { NgxBootstrapSliderModule } from 'ngx-bootstrap-slider';
import {AuthenticationService} from './_services';
import { APP_INITIALIZER } from '@angular/core';
import { AppConfig } from './_services/app.config';
import { ToastrModule } from 'ngx-toastr';
import { CommonModule } from '@angular/common';
import { JwtInterceptor, ErrorInterceptor } from './_helpers';
import { LoginComponent } from './login';
import { ControlSliderComponent } from './supply-voltages/control-slider/control-slider.component';
import { VideostreamComponent } from './videostream/videostream.component';
import { ChartFormComponent } from './chart-form/chart-form.component';
import { FormsModule } from '@angular/forms';
import { MenuListItemComponent } from './navigation/menu-list-item/menu-list-item.component';
import { EditorComponent } from './editor/editor.component';
import { NgJsonEditorModule } from 'ang-jsoneditor';
import { GeneralSettingsComponent } from './general-settings/general-settings.component'
import { MeasurementConfigurationComponent } from './measurement-config/measurement-config.component';


/**
* loads the config from the backend.
* Needs to be called before starting the rest of the application
*/
export function initializeApp(appConfig: AppConfig) {
  return () => appConfig.load();
}


@NgModule({
  declarations: [
    AppComponent,
    MyNavComponent,
    MDashboardComponent,
    ChartComponent,
    SupplyVoltagesComponent,
    LoginComponent,
    ControlSliderComponent,
    VideostreamComponent,
    ChartFormComponent,
    MenuListItemComponent,
    ConfirmDialog,
    PowerOffDialog,
    MeasurementConfigurationComponent,
    EditorComponent,
    GeneralSettingsComponent
  ],
  imports: [
    MatExpansionModule,
    MatDialogModule,
    FormsModule,
    ReactiveFormsModule,
    NgxBootstrapSliderModule,
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    LayoutModule,
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatIconModule,
    MatListModule,
    MatGridListModule,
    MatCardModule,
    MatMenuModule,
    HttpClientModule,
    NgJsonEditorModule,
    CommonModule,
    ToastrModule.forRoot({
     timeOut: 1500,
     positionClass: 'toast-bottom-right',
     preventDuplicates: true,
   })
   ],
   providers: [
       { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
       { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },
         AuthenticationService,
         AppConfig,
         // Call initializeApp before application boots
       { provide: APP_INITIALIZER,  useFactory: initializeApp,  deps: [AppConfig], multi: true }
   ],
  entryComponents: [ConfirmDialog, PowerOffDialog],
  bootstrap: [AppComponent]
})
export class AppModule { }
