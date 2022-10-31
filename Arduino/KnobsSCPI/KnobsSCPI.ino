// Created by Scott Feister, Keily Valdez Sereno, and Alex Crawford on Oct 31, 2022
// BasicEncoder portions are modeled off of documentation found here: https://github.com/micromouseonline/BasicEncoder

#include <Arduino.h>
#include <BasicEncoder.h>
#include <TimerOne.h>
#include "Vrekrer_scpi_parser.h"                          // SCPI libraries, for sending commands over USB

#define NKNOBS 5 // number of knobs total

#define KNOB0_CLK_PIN 12 // digital pin number
#define KNOB0_DT_PIN 11

#define KNOB1_CLK_PIN 5
#define KNOB1_DT_PIN 10

#define KNOB2_CLK_PIN 8
#define KNOB2_DT_PIN 9

#define KNOB3_CLK_PIN 7
#define KNOB3_DT_PIN 6

#define KNOB4_CLK_PIN 2
#define KNOB4_DT_PIN 3

SCPI_Parser my_instrument;                                //starts the SCPI command library

BasicEncoder encoder0(KNOB0_CLK_PIN, KNOB0_DT_PIN);
BasicEncoder encoder1(KNOB1_CLK_PIN, KNOB1_DT_PIN);
BasicEncoder encoder2(KNOB2_CLK_PIN, KNOB2_DT_PIN);
BasicEncoder encoder3(KNOB3_CLK_PIN, KNOB3_DT_PIN);
BasicEncoder encoder4(KNOB4_CLK_PIN, KNOB4_DT_PIN);

BasicEncoder encoders[NKNOBS] = {encoder0, encoder1, encoder2, encoder3, encoder4};

/* Serial communication functions */
void identify(SCPI_C commands, SCPI_P parameters, Stream& interface) {      //identifying what object you're using
    interface.println(F("DolphinDAQ,Arduino Knobs,#00,v0.1"));             //printing this line to the Serial Monitor
}

void timer_service() {
  for (int i=0; i < NKNOBS; i++) {
    encoders[i].service();
  }
}

void setup() {

  my_instrument.RegisterCommand(F("*IDN?"), &identify);     //first command "*IDN?"

  Serial.begin(115200);
  Timer1.initialize(1000);
  Timer1.attachInterrupt(timer_service);
}

void loop() {
  for (int i=0; i < NKNOBS; i++) {
    if (encoders[i].get_change()) {
      Serial.print("ROT");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(encoders[i].get_count());
    }
  }
  my_instrument.ProcessInput(Serial, "\r\n");   //starts allowing the Serial Monitor input for SCPI use
}
