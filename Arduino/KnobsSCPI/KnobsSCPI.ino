// Created by Scott Feister, Keily Valdez Sereno, and Alex Crawford on Oct 31, 2022
// BasicEncoder portions are modeled off of documentation found here: https://github.com/micromouseonline/BasicEncoder

// Note that the positive direction is clockwise

#include <Arduino.h>
#include <BasicEncoder.h>
#include <TimerOne.h>
#include "Vrekrer_scpi_parser.h"                          // SCPI libraries, for sending commands over USB

#define NKNOBS 5 // number of knobs total

#define KNOB0_CLK_PIN 8
#define KNOB0_DT_PIN 9

#define KNOB1_CLK_PIN 5
#define KNOB1_DT_PIN 10

#define KNOB2_CLK_PIN 12 // digital pin number
#define KNOB2_DT_PIN 11

#define KNOB3_CLK_PIN 2
#define KNOB3_DT_PIN 3

#define KNOB4_CLK_PIN 7
#define KNOB4_DT_PIN 6

SCPI_Parser my_instrument;                                //starts the SCPI command library

BasicEncoder encoder0(KNOB0_DT_PIN, KNOB0_CLK_PIN);
BasicEncoder encoder1(KNOB1_DT_PIN, KNOB1_CLK_PIN);
BasicEncoder encoder2(KNOB2_DT_PIN, KNOB2_CLK_PIN);
BasicEncoder encoder3(KNOB3_DT_PIN, KNOB3_CLK_PIN);
BasicEncoder encoder4(KNOB4_DT_PIN, KNOB4_CLK_PIN);

BasicEncoder encoders[NKNOBS] = {encoder0, encoder1, encoder2, encoder3, encoder4};

/* Serial communication functions */
void identify(SCPI_C commands, SCPI_P parameters, Stream& interface) {      //identifying what object you're using
    interface.println(F("DolphinDAQ,SC22 Knobs,#00,20221109"));             //printing this line to the Serial Monitor
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
