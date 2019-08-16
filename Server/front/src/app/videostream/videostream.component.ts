import {  Component,} from '@angular/core';

/**
* Component used to show a simple picture - video feed from the backend.
*/
@Component({
  selector: 'app-videostream',
  templateUrl: './videostream.component.html',
  styleUrls: ['./videostream.component.css']
})
export class VideostreamComponent {
  title = "live-video-demo";
}
