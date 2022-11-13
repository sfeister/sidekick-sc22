/*
NeoLEDsSCPI.ino

When externally triggered, flashes six LEDs a single time. Each LED has its own flash duration and brightness.

Built directly off of LEDsSCPI.ino from the Sidekick system. Adapted for use with Adafruit Neopixels.

Important Notes:
 * LED flash begins abbout 1000 microseconds after the external trigger is received.
 * External trigger should be wired to Arduino Pin 2.
 * The Neopixel data pin should be wired to Arduino Pin 3.
 
Serial Commands (lower-case portions are optional):
  *IDN?                 Responds with a device identification string.
  DURation:LEDN VAL     Sets LED N (0-5) pulse duration to VAL (unsigned long integer, in microseconds).
  DURation:LEDN?        Responds with LED N (0-5) pulse duration (unsigned long integer, in microseconds).
  BRIGhtness:LEDN VAL   Sets LED N (0-5) brightness (PWM duty cycle) to VAL (integer, 0 to 255).
  BRIGhtness:LEDN?      Responds with LED N (0-5) brightness (PWM duty cycle)(integer, 0 to 255).
  RED:LEDN VAL          Sets LED N (0-5) to a Red VAL (0-1)
  RED:LEDN?             Responds with LED N (0-5) Red VAL (0-1)
  GREEN:LEDN VAL        Sets LED N (0-5) to a Green VAL (0-1)
  GREEN:LEDN?           Responds with LED N (0-5) Green VAL (0-1)
  BLUE:LEDN VAL         Sets LED N (0-5) to a Blue VAL (0-1)
  BLUE:LEDN?            Responds with LED N (0-5) Blue VAL (0-1)
 
References:
 1. Following timer instructions at: https://github.com/contrem/arduino-timer
 2. Following Vrekrer SCPI Parser examples, e.g. at https://github.com/Vrekrer/Vrekrer_scpi_parser/blob/master/examples/Numeric_suffixes/Numeric_suffixes.ino
 3. Attaching an interrupt pin for external triggering: https://www.arduino.cc/reference/en/language/functions/external-interrupts/attachinterrupt/ 

Created by Emiko Ito, Keily Valdez-Sereno, and Scott Feister of California State University Channel Islands between 2021 - 2022.
*/

#include "Arduino.h" 
#include <arduino-timer.h>
#include "Vrekrer_scpi_parser.h"
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif


#define EXTTRIG 2 // Note that this pin must be one of the Arduino pins capable of digital interrupt. See table at https://www.arduino.cc/reference/en/language/functions/external-interrupts/attachinterrupt/

#define NLED 6 // Total number of Neopixels in the strand, each with independent duration and brightness
#define LED0 3  //this is the data pin we will use for the neopixel strand

Adafruit_NeoPixel pixels(NLED, LED0, NEO_RGBW + NEO_KHZ800);


Timer<16, micros, int> timer1; // Timer with 16 task slots, microsecond resolution, and handler argument type int

//int LEDPins[NLED]; // Arduino pin numbers for each of the six LED outputs
int brights[NLED]; // Brightnesses for each of the six LEDs, when on
float red[NLED] =   {1, 0, 0, 1, 0, 0.75}; //red values for each pixel
float green[NLED] = {0, 1, 0, 0, 1, 0.25}; //green values for each pixel
float blue[NLED] =  {0, 0, 1, 1, 1, 0.50}; //blue values for each pixel
unsigned long durations[NLED]; // Pulse duration times, in microseconds, for each of the six LEDs
unsigned long t0;
int trigCount = 0;

SCPI_Parser my_instrument;
int brightness = 0; // temp variable
float value = 0; // temp variable

/* LED control functions */
bool LEDStart(int LEDid) {
    // Turn on the LED of this index (0-5), with a specified brightness
    pixels.setPixelColor(LEDid, pixels.Color(brights[LEDid] * red[LEDid], brights[LEDid] * green[LEDid], brights[LEDid] * blue[LEDid]));
    pixels.show();
    return false; // to repeat the action - false to stop
}

bool LEDStop(int LEDid) {
    // Turn off the LED of this index (0-5)
    //just sets whatever pixel to all 0s so it's nothing
    pixels.setPixelColor(LEDid, pixels.Color(0, 0, 0, 0)); //set first pixel to color RED
    pixels.show();
    return false; // to repeat the action - false to stop
}

/* Timing functions */

// Interrupt service routine (ISR): Called upon external trigger.
// Starts one-time timers that govern the start/stop pulse of the LEDs
void myISR() {
    // Pulse the LEDs once, each with its own brightness and duration
    trigCount++;
    if (timer1.size() < 1) { // Only start a new set of LED pulses if the old set is completed
      t0 = micros() + 1000; // Set "LED pulse time zero" to one thousand microseconds into the future to get everything set up first

      // Schedule the LED pulse starts and stops
      for(int i = 0; i < (NLED-1); ++i)
      {
          timer1.at(t0, LEDStart, i); // Set the start time for this LED
          timer1.at(t0 + durations[i], LEDStop, i); // Set the stop time for this LED (must be significantly after the start time)
      }
    }
    String triggerMsg = "TRIG: " + trigCount;
    Serial.print("TRIG: " + String(trigCount) + ", ");
    for (int i = 0; i < NLED; i++){
      Serial.print("L" + String(i) + ": " + String(brights[i]) + ", ");
    }    
    Serial.println();
}

/* Serial communication functions */
void identify(SCPI_C commands, SCPI_P parameters, Stream& interface) {
  interface.println(F("DolphinDAQ,SC22 Neo-LEDs,#00,20221109"));
}

void getBrightness(SCPI_C commands, SCPI_P parameters, Stream& interface) {
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid, respond with the LED's duration
  if ( (suffix >= 0) && (suffix < NLED) ) {
     interface.println(String(brights[suffix], DEC));
  }
}

void setBrightness(SCPI_C commands, SCPI_P parameters, Stream& interface) { 
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid,
  //use the first parameter (if valid) to set the LED brightness
  if ( (suffix >= 0) && (suffix < NLED) ) {
    if(parameters.Size() > 0) {
      value = String(parameters[0]).toInt();
      brights[suffix] = constrain(value, 0, 255);
      //set brightness value in array, then we're gucci
    }
  }
}

void getDuration(SCPI_C commands, SCPI_P parameters, Stream& interface) {
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid, respond with the LED's duration
  if ( (suffix >= 0) && (suffix < NLED) ) {
     interface.println(durations[suffix]);
  }
}

void setDuration(SCPI_C commands, SCPI_P parameters, Stream& interface) { 
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid,
  //use the first parameter (if valid) to set the LED duration
  if ( (suffix >= 0) && (suffix < NLED) ) {
    if(parameters.Size() > 0) {
      //durations[suffix] = strtoul(String(parameters[0]).toCharArray(buf, len));
      durations[suffix] = strtoul(parameters[0], NULL, 0);
    }
  }
}

void getRed(SCPI_C commands, SCPI_P parameters, Stream& interface) {
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid, respond with the LED's red value
  if ( (suffix >= 0) && (suffix < NLED) ) {
     interface.println(String(red[suffix], DEC));
  }
}

void setRed(SCPI_C commands, SCPI_P parameters, Stream& interface) { 
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid,
  //use the first parameter (if valid) to set the LED duration
  if ( (suffix >= 0) && (suffix < NLED) ) {
    if(parameters.Size() > 0) {
      value = String(parameters[0]).toFloat();
      red[suffix] = constrain(value, 0, 1);
      interface.println("LED" + String(suffix) + " red set to " + String(value));
    }
  }
}

void getGreen(SCPI_C commands, SCPI_P parameters, Stream& interface) {
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid, respond with the LED's green value
  if ( (suffix >= 0) && (suffix < NLED) ) {
     interface.println(String(green[suffix], DEC));
  }
}

void setGreen(SCPI_C commands, SCPI_P parameters, Stream& interface) { 
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid,
  //use the first parameter (if valid) to set the LED duration
  if ( (suffix >= 0) && (suffix < NLED) ) {
    if(parameters.Size() > 0) {
      value = String(parameters[0]).toFloat();
      green[suffix] = constrain(value, 0, 1);
      interface.println("LED" + String(suffix) + " green set to " + String(value));
    }
  }
}

void getBlue(SCPI_C commands, SCPI_P parameters, Stream& interface) {
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid, respond with the LED's blue value
  if ( (suffix >= 0) && (suffix < NLED) ) {
     interface.println(String(blue[suffix], DEC));
  }
}

void setBlue(SCPI_C commands, SCPI_P parameters, Stream& interface) { 
  //Get the numeric suffix/index (if any) from the commands
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[LED]%u", &suffix);

  //If the suffix is valid,
  //use the first parameter (if valid) to set the LED duration
  if ( (suffix >= 0) && (suffix < NLED) ) {
    if(parameters.Size() > 0) {
      value = String(parameters[0]).toFloat();
      blue[suffix] = constrain(value, 0, 1);
      interface.println("LED" + String(suffix) + " blue set to " + String(value));
    }
  }
}

void setup() { 
  my_instrument.RegisterCommand(F("*IDN?"), &identify); 
  my_instrument.SetCommandTreeBase(F("BRIGhtness:"));
  my_instrument.RegisterCommand(F("LED#?"), &getBrightness);
  my_instrument.RegisterCommand(F("LED#"), &setBrightness);
  my_instrument.SetCommandTreeBase(F("DURation:"));
  my_instrument.RegisterCommand(F("LED#?"), &getDuration);
  my_instrument.RegisterCommand(F("LED#"), &setDuration);
  my_instrument.SetCommandTreeBase(F("Red:"));
  my_instrument.RegisterCommand(F("LED#?"), &getRed);
  my_instrument.RegisterCommand(F("LED#"), &setRed);
  my_instrument.SetCommandTreeBase(F("Green:"));
  my_instrument.RegisterCommand(F("LED#?"), &getGreen);
  my_instrument.RegisterCommand(F("LED#"), &setGreen);
  my_instrument.SetCommandTreeBase(F("Blue:"));
  my_instrument.RegisterCommand(F("LED#?"), &getBlue);
  my_instrument.RegisterCommand(F("LED#"), &setBlue);
  
  // Set initial LED pulse durations (in microseconds)
  durations[0] = 500000;
  durations[1] = 500000;
  durations[2] = 500000;
  durations[3] = 500000;
  durations[4] = 500000;
  durations[5] = 100000000; //last Neopixel should have very long duration so it always stays on

  // Set intial LED brightnesses
  brights[0] = 200;
  brights[1] = 200;
  brights[2] = 200;
  brights[3] = 200;
  brights[4] = 200;
  brights[5] = 200; //last Neopixel remains bright

  // Set up external triggering
  attachInterrupt(digitalPinToInterrupt(EXTTRIG), myISR, RISING);

  //Initialize Neopixel strand
  pixels.begin();
  pixels.show();
  pixels.clear();

  // Begin accepting SCPI commands
  Serial.begin(115200);
}

void loop() {
  timer1.tick();
  LEDStart(NLED-1);
  my_instrument.ProcessInput(Serial, "\r\n");
} 
