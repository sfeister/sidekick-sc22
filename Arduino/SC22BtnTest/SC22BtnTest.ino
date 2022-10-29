/*
  ManyPrint
  Example output syntax for buttons.
 */
 
#include "Arduino.h"
#include "Vrekrer_scpi_parser.h"                          // SCPI libraries, for sending commands over USB

#define NBTNS 5

SCPI_Parser my_instrument;                                //starts the SCPI command library

unsigned long trigcnt = 0; // trigger count
uint32_t counts[NBTNS];

/* Serial communication functions */
void identify(SCPI_C commands, SCPI_P parameters, Stream& interface) {      //identifying what object you're using
    interface.println(F("DolphinDAQ,Arduino Shutter,#00,v0.1"));             //printing this line to the Serial Monitor
}

char buffer[40];

void setup() {
  my_instrument.RegisterCommand(F("*IDN?"), &identify);     //first command "*IDN?"

  // Initialize counts to something different
  for(int i = 0; i < NBTNS; i++) {
    counts[i] = 100*i;
  }
  
  Serial.begin(115200);
}

void loop() {
  for(int i = 0; i < NBTNS; i++) {
    sprintf(buffer, "B%d: %d", i, counts[i]);
    Serial.println(buffer);
    counts[i]++;
  }
  delay(1000);               // wait for a second
  my_instrument.ProcessInput(Serial, "\r\n");   //starts allowing the Serial Monitor input for SCPI use
}
