#include <NMEAGPS.h>
#include <NeoSWSerial.h>
#include <MPU9255.h>//include MPU9255 library
#include <SPI.h>
#include <SD.h>
#include <ezButton.h>

NeoSWSerial gpsPort(3, 2);

// Variable for loop state toggle by button
#define LOOP_STATE_STOPPED 0
#define LOOP_STATE_STARTED 1

#define ARDUINO_USD_CS 8 // uSD card CS pin (pin 8 on Duinopeak GPS Logger Shield)

#define GPS_BAUD 9600

ezButton button(7);  // create ezButton object that attach to pin 7;
int loopState = LOOP_STATE_STOPPED;
int gpsState = 0;
static const int ERROR_LED = 4;
static const int SAVING_LED = 9;

File LogFile;
MPU9255 mpu;

static NMEAGPS  gps;
static gps_fix  fix;

void setup()
{
  gpsPort.begin( GPS_BAUD );

  // initialize the SD card if it is present
  if (!SD.begin(ARDUINO_USD_CS))
  {
    digitalWrite(ERROR_LED,HIGH);
  }

  // Initialize the mpu
  if(mpu.init())
  {
    digitalWrite(ERROR_LED,HIGH);
  }
  
  mpu.set_acc_scale(scale_16g);//set accelerometer scale
  
  button.setDebounceTime(50); // set debounce time to 50 milliseconds
}


void createFile()
{
  char filename[15] = "data_##.txt";
  
  for (uint8_t i=1; i<100; i++){
    filename[5] = '0' + i/10;
    filename[6] = '0' + i%10;
    if (!SD.exists(filename))
    {
      break; // Break out of this loop if file not fount
    }
  }
  logFile = SD.open(filename, FILE_WRITE); // Open log file
  logFile.println("imu;TMS;AX;AY;AZ");
  logFile.println("gps;TMS;LAT;LONG;SPEED;HH;MM;SS");
}

void logGps(){
  if (fix.valid.time){
    LogFile.print("gps");
    LogFile.print(";");
    LogFile.print(millis());
    LogFile.print(";");
    LogFile.print(fix.latitude(), 6);
    LogFile.print(";");
    LogFile.print(fix.longitude(), 6);
    LogFile.print(";");
    LogFile.print(fix.speed_kph());
    LogFile.print(";");
    LogFile.print(fix.dateTime.hours);
    LogFile.print(";");
    LogFile.print(fix.dateTime.minutes);
    LogFile.print(";");
    LogFile.print(fix.dateTime.seconds);
    LogFile.println(";");
    gpsState = 0;
    
  }
}

void logImu(){
  mpu.read_acc();//get data from the accelerometer

  //print all data in serial monitor
  LogFile.print("imu");
  LogFile.print(";");
  LogFile.print(millis());
  LogFile.print(";");
  LogFile.print(mpu.ax);
  LogFile.print(";");
  LogFile.print(mpu.ay);
  LogFile.print(";");
  LogFile.println(mpu.az);
}

void loop() {
  button.loop();

  // Control the button state
  if (button.isPressed()) {
    if (loopState == LOOP_STATE_STOPPED){
      loopState = LOOP_STATE_STARTED;
      createFile(); // create log file
      digitalWrite(SAVING_LED, HIGH);
    }
    else{
      loopState = LOOP_STATE_STOPPED;
      LogFile.close(); // close the file 
      digitalWrite(SAVING_LED, LOW);
    }
  }

  // If button is push we log the data
  if (loopState == LOOP_STATE_STARTED){
    logImu();
    if (gpsState){
      logGps();
    }
    delay(1.0);
  }

  // Always need to feed the gps data (to validate)
  while (gps.available( gpsPort )) {
    fix = gps.read();
    gpsState = 1;
  }
}
