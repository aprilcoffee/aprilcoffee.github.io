
var sun;
var SB = [];
var capture;
var video
var osc;
var reverb;
var playing = false;
var reverb;
var x,y,z;
var easing = 0.05;
var xx;
var yy;
var zz;
var flag = 0;
function setup() {
	xx = 0.01;
	yy = 0.01;
  	createCanvas(window.innerWidth, window.innerHeight);
  //sun = loadImage("sun.png");
  	//video = createVideo("data/transit.mov");
  	//video.loop();
  	for (var s = 0; s < 10000; s++) {
    	SB.push(new sunBall(90, random(360), random(360), width / 2, height / 2));
  	}
  	//video.hide();
  	background(0);

   osc = new p5.Oscillator();
   osc.setType('sine');
   osc.freq(140);
   osc.amp(0.4,1);
   osc.start();
}

function draw() {
	//if(frameCount%10==0){
 	//let url = 'https://api.apixu.com/v1/current.json?key=513d8003c8b348f1a2461629162106&q=NYC';
  	//loadJSON(url, gotWeather);
	//}
	flag+=0.5;
	if(flag>100)flag=100;
	blendMode(BLEND);
	background(30 + 25*sin(frameCount/80));
	fill(255);
	var targetX = x;
	var dx = targetX - xx;
	
	var targetY = y;
	var dy = targetY - yy;
	xx += dx*easing;
	yy += dy*easing;
	translate(-x*3,-5+y*5);
  	blendMode(ADD);
  	for(var i = 0; i <50; i++){
  		fill(240,80,20,flag-i*2);
  		var tempR = 25*sin(frameCount/80);
  		ellipse(width/2,height/2,100+i*3+tempR,100+i*3+tempR);
 	 }

	osc.freq(140+(30*abs(sin(frameCount/80))));

	if(flag<100){
		for(var s=0;s<SB.length;s++){
			SB[s].update();
			SB[s].show(flag);
		}
	}
	else{
  		for (var s = 0; s < SB.length; s++) {
    	SB[s].update();
    	SB[s].show(flag);
  		}
	}
	//for(var cor_x=-1;cor_x<=1;x++){
	//	for(var cor_y=-1;cor_y<=1;y++){
		//image(video,width/2+cor_x,height/2+cor_y,1,1);
	//	}	
	//}
	 //filter(BLUR, 3);
}

function sunBall(A, _delta, B, C, D) {
  this.R = A;
  this.R_ori = A;
  this.theta = B;
  this.delta = _delta;
  this.cx = C;
  this.cy = D;
  this.v = random(0.01, 0.02);

  this.update = function() {
    this.theta += this.v;
    this.delta += this.v * 10;
    this.R = this.R_ori + 15*sin(frameCount/80);
  }
  this.show = function(a) {
    this.px = this.cx + this.R * (0.5 + 0.1 * tan(radians(this.delta - 90))) * sin(radians(this.theta));
    this.py = this.cy + this.R * (0.5 + 0.1 * tan(radians(this.delta - 90))) * cos(radians(this.theta));
    //colorMode(HSB);
if(flag>=90){
    if (this.delta % 180 > 60) {
      noStroke();
      fill(240, 80, 10, map(this.delta % 180, 60, 180, 160, 0));
      //tint(255, map(this.delta % 180, 135, 180, 255, 0));
    } else if (this.delta % 180 < 60) {
      noStroke();
      fill(240, 80, 10, map(this.delta % 180, 0, 60, 0, 60));
      //tint(255, map(this.delta % 180, 0, 45, 25, 255));
    } else {
      noStroke();
      fill(240, 80, 40,50);
    }}
	  else{
if (this.delta % 180 > 60) {
      noStroke();
      fill(240, 80, 10, map(this.delta % 180, 60, 180, flag, 0));
      //tint(255, map(this.delta % 180, 135, 180, 255, 0));
    } else if (this.delta % 180 < 60) {
      noStroke();
      fill(240, 80, 10, map(this.delta % 180, 0, 60, 0, flag));
      //tint(255, map(this.delta % 180, 0, 45, 25, 255));
    } else {
      noStroke();
      fill(240, 80, 40,20);
    }
	  }
    //image(a, this.px, this.py, 6, 4.5);
	smooth();
    ellipse(this.px, this.py, 8,6);
  }
}


window.addEventListener('devicemotion', function(e)
{
  // get accelerometer values
  x = e.accelerationIncludingGravity.x;
  y = e.accelerationIncludingGravity.y;
  z = e.accelerationIncludingGravity.z;
});


function gotWeather(weather) {
 let wind; 
  // Get the angle (convert to radians)
  let angle = radians(Number(weather.current.wind_degree));
  // Get the wind speed
  let windmag = Number(weather.current.wind_mph);
  
  // Display as HTML elements
  //let temperatureDiv = createDiv(floor(weather.current.temp_f) + '&deg;');
  //let windDiv = createDiv("WIND " + windmag + " <small>MPH</small>");
  
  // Make a vector
  wind = p5.Vector.fromAngle(angle);
}

function touchMoved(event){
	console.log(event);
	return false;
}
