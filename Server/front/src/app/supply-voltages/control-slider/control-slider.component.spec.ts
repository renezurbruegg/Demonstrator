import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ControlSliderComponent } from './control-slider.component';

describe('ControlSliderComponent', () => {
  let component: ControlSliderComponent;
  let fixture: ComponentFixture<ControlSliderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ControlSliderComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ControlSliderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
