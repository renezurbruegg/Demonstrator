import { Component, OnInit,Input } from '@angular/core';
import { AppConfig } from '../../_services/app.config'
import { VarSupply } from '../../_models/varSupply.model';

/**
* Component used to create a slider with arrows on the side, to select a voltage for var supplies. <br>
* [<] =====O================ [>]
*/
@Component({
  selector: 'app-control-slider',
  templateUrl: './control-slider.component.html',
  styleUrls: ['./control-slider.component.css']
})
export class ControlSliderComponent implements OnInit {
  /**
  * The var supply which is controlled by this slider. gets set programatically
  */
  public supply: VarSupply;

  /**
  * index of the supply in config array
  */
  @Input()
  private deviceId: number;
  constructor() { }

  /**
  * Checks if selected value from slider is in selecetable range
  */
  get checkInput() {
    return this.supply.maxValueChecked || (this.supply.desiredVoltage >= this.supply.minValue && this.supply.desiredVoltage <= this.supply.maxValue) ;
  }
  /**
  * Disables / enables the supply
  */
  public toggleEnabled() {
    this.supply.enabled = !this.supply.enabled;
  }

  /**
  * gets called when arrow right (add) button is pressed
  */
  public addToSlider() {
    if(this.supply.desiredVoltage < this.supply.maxValue)
      this.supply.desiredVoltage = Math.round( (this.supply.desiredVoltage + this.supply.stepSize )* 1000) / 1000;
  }
  /**
  * gets called when arrow left (subtract) button is pressed
  */
  public subFromSlider() {
    if(this.supply.desiredVoltage > this.supply.minValue)
      this.supply.desiredVoltage = Math.round( (this.supply.desiredVoltage - this.supply.stepSize )* 1000) / 1000;
  }

  ngOnInit() {
    if(this.deviceId) {
      this.supply = AppConfig.settings.supplies[this.deviceId];
      this.supply.desiredVoltage = 0 + this.supply.currentVoltage;
      //this.supply.maxValueChecked = false;
    }
  }
}
