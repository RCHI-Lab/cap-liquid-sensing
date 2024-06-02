IntervalTimer myTimer; 

int samp_freq = 100;
char newline = B11111111;
unsigned long curr_time;
unsigned long start_time;
unsigned long last_time;
int pin1;
int pin2;
int pin3;
int pin4;
int pin5;

void setup(void) {
  Serial.begin(115200);
  
  myTimer.priority(255); 
  
  start_time = micros();
  last_time = 0;
  
  // collects values at 100 Hz
  myTimer.begin(vals, 1000000/samp_freq);
}

void vals() {
//   test code for outputs, uncomment to use plot to test sensors
//  Serial.print(touchRead(23));
//  Serial.print(",");
//  Serial.print(touchRead(18));
//  Serial.print(",");
//  Serial.print(touchRead(16));
//  Serial.print(",");
//  Serial.print(touchRead(15));
//  Serial.print(",");
//  Serial.println(touchRead(1));

// code for running collection, comment out to test sensors
// upload this to teensy before running data_collection.py
  curr_time = micros() - start_time;
  last_time = curr_time;
  pin1 = touchRead(1);
  pin2 = touchRead(15);
  pin3 = touchRead(16);
  pin4 = touchRead(18);
  pin5 = touchRead(23);
  Serial.write((byte *)&newline, 1); 
  Serial.write((byte *)&newline, 1); 
  Serial.write((byte *)&newline, 1); 
  Serial.write((byte *)&pin1, 2);
  Serial.write((byte *)&pin2, 2);
  Serial.write((byte *)&pin3, 2);
  Serial.write((byte *)&pin4, 2);
  Serial.write((byte *)&pin5, 2);
  Serial.write((byte *)&curr_time, 4);
  Serial.flush();
}

void loop() {
  
}
