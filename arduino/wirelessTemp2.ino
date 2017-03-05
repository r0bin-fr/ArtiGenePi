/*********************************************************************
 This is an example for our nRF51822 based Bluefruit LE modules

 MIT license, check LICENSE for more information
 All text above, and the splash screen below must be included in
 any redistribution
*********************************************************************/

#include <Arduino.h>
#if not defined (_VARIANT_ARDUINO_DUE_X_) && not defined (_VARIANT_ARDUINO_ZERO_)
  #include <SoftwareSerial.h>
#endif
#include <SPI.h>
#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"
#include "Adafruit_BLEGatt.h"

#include "BluefruitConfig.h"
/*=========================================================================
    APPLICATION SETTINGS

    FACTORYRESET_ENABLE       Perform a factory reset when running this sketch
                              Enabling this will put your Bluefruit LE module in a 'known good' state and clear any config
                              data set in previous sketches or projects, so running this at least once is a good idea.   
                              When deploying your project, however, you will want to disable factory reset by setting this
                              value to 0.  If you are making changes to your Bluefruit LE device via AT commands, and those
                              changes aren't persisting across resets, this is the reason why.  Factory reset will erase
                              the non-volatile memory where config data is stored, setting it back to factory default values.       
                              Some sketches that require you to bond to a central device (HID mouse, keyboard, etc.)
                              won't work at all with this feature enabled since the factory reset will clear all of the
                              bonding data stored on the chip, meaning the central device won't be able to reconnect.
                              
    MINIMUM_FIRMWARE_VERSION  Minimum firmware version to have some new features
    MODE_LED_BEHAVIOUR        LED activity, valid options are
                              "DISABLE" or "MODE" or "BLEUART" or
                              "HWUART"  or "SPI"  or "MANUAL"
    -----------------------------------------------------------------------*/
    #define FACTORYRESET_ENABLE         1
    #define MINIMUM_FIRMWARE_VERSION    "0.6.6"
    //#define MODE_LED_BEHAVIOUR          "MODE"
    #define MODE_LED_BEHAVIOUR          "0" 
/*=========================================================================*/

//******************************
// SECTION BLUEFRUIT 
//******************************

// Create the bluefruit object, either software serial...uncomment these lines
/* ...hardware SPI, using SCK/MOSI/MISO hardware SPI pins and then user selected CS/IRQ/RST */
Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_CS, BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);

#define ENABLE_SERIAL 0

//Service GATT
Adafruit_BLEGatt gatt(ble);

// A small helper
void error(const __FlashStringHelper*err) {
  Serial.println(err);
  while (1);
}
// The BLE service information 
int32_t htsServiceId;
int32_t htsMeasureCharId;
// BLE Characteristics & services
int32_t temperatureCharacteristicMax;
int32_t temperatureCharacteristicMin;
int32_t temperatureCharacteristicCurr;
int32_t batteryCharacteristic;
int32_t thermometerService;

//******************************
// SECTION TEMPERATURE 
//******************************
#include <OneWire.h>
#include <DallasTemperature.h>
// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

void setupMaxim(void){
  // locate devices on the bus
  Serial.print("Locating devices...");
  sensors.begin();
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices.");

  // set the resolution to 9 bit
  sensors.setResolution(9);
  
  // report parasite power requirements
  Serial.print("Parasite power is: "); 
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");  
}

//get temperature from sensor
float getKTemp(){
  // Send the command to get temperatures
  sensors.requestTemperatures(); 
  //return value
  return sensors.getTempCByIndex(0);
}


union float_bytes {
  float value;
  uint8_t bytes[sizeof(float)];
};
static union float_bytes tCelsius = { .value = 0.0 };
static union float_bytes tCelsiusMin = { .value = 0.0 };
static union float_bytes tCelsiusMax = { .value = 0.0 };
static union float_bytes bPercent = { .value = 0.0 };
  
float Tnow,Tmin,Tmax,Tlast = 0;
float T_dif_now, T_dif_last = 0;
int TminLoopCount, TmaxLoopCount = 0;

// algorithme de tri de temperature 
// compute mini and maxi values (Gene Cafe hack)
// algoritm from evquink/RoastGenie (thank you!)
void updateTempCounters(float newtemp)
{
  Tnow = newtemp;
  TminLoopCount = TminLoopCount+1;
  TmaxLoopCount = TmaxLoopCount+1;
  T_dif_now = Tnow - Tlast;

  if (T_dif_now >= 0.0 and T_dif_last < 0.0 and TminLoopCount > 1){  // this is a local minimum
    Tmin = Tlast  ;                                                  // best estimate of environmental$
    TminLoopCount = 0;                                               // reset loop counter
    //update BLE value
    if(tCelsiusMin.value != Tlast){
      tCelsiusMin.value = Tlast;
      gatt.setChar(temperatureCharacteristicMin, tCelsiusMin.bytes, sizeof(tCelsiusMin));
      Serial.print("Temp min: ");
      Serial.println(tCelsiusMin.value);
    }
  }
  if (T_dif_now <= 0.0 and T_dif_last > 0.0 and TmaxLoopCount > 1){  // this is a local maximum
    Tmax = Tlast;                                                    // best estimate of bean mass temp
    TmaxLoopCount = 0;                                               // reset loop counter
    //update BLE value
    if(tCelsiusMax.value != Tlast){
      tCelsiusMax.value = Tlast;
      gatt.setChar(temperatureCharacteristicMax, tCelsiusMax.bytes, sizeof(tCelsiusMax));
      Serial.print("Temp max: ");
      Serial.println(tCelsiusMin.value);
    }
  }
  Tlast = Tnow;
  T_dif_last = T_dif_now;
}

//******************************
// SECTION BATTERIE
//******************************
//pin pour check voltage batterie
#define VBATPIN   A9
//vars pour VMAX et VMIN
#define BATT_VCHARGE 4.3
#define BATT_VMAX 4.18
#define BATT_VMIN 3.7

//var globale pour la derniere mesure (moyenne)
float lastBattVal = 4.2;
//Affiche le voltage de la batterie lu
float getBattVal() {
  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage
  return measuredvbat;
}

//convertit le voltage en pourcentage
float getBattPercent() {
  int bperc = 0;
  //recupere le voltage et fait la moyenne
  float bvolt = getBattVal();
  bvolt = (bvolt + lastBattVal) / 2;
  Serial.print("bvolt=");Serial.println(bvolt);
  //Serial.print("lastBattVal=");Serial.println(lastBattVal);
  lastBattVal = bvolt;
  //if we are charging, return a special value
  if (bvolt > BATT_VCHARGE)
    return 200;
  //calcul du pourcentage
  bperc = (100 * (bvolt - BATT_VMIN)) / (BATT_VMAX - BATT_VMIN);
  //Serial.print("bperc=");Serial.println(bperc);
  if (bperc > 100)
    bperc = 100;
  if (bperc < 0)
    bperc = 0;
  //Serial.print("bperc final=");Serial.println(bperc);
  return float(bperc);
  //return bvolt;
}

//******************************
// SETUP BLE
//******************************
void setupBLE(void){
  
  /* Initialise the module */
  Serial.print(F("Initialising the Bluefruit LE module: "));
  
  if ( !ble.begin(VERBOSE_MODE) ){
    error(F("Couldn't find Bluefruit, make sure it's in CoMmanD mode & check wiring?"));
  }
  Serial.println( F("OK!") );

  if ( FACTORYRESET_ENABLE ){
    /* Perform a factory reset to make sure everything is in a known state */
    Serial.println(F("Performing a factory reset: "));
    if ( ! ble.factoryReset() ){
      //error(F("Couldn't factory reset"));
      Serial.println(F("Couldn't factory reset"));
    }
  }

  /* Disable command echo from Bluefruit */
  ble.echo(false);

  /* Print Bluefruit information */
  Serial.println("Requesting Bluefruit info:");
  ble.info();

  uint8_t thermometerServiceUUID = 0x1809; 
  thermometerService = gatt.addService(thermometerServiceUUID);
  /* Thermo characteristics, current temp */
  uint8_t thermometerCharacteristicUUID = 0x2221; 
  temperatureCharacteristicCurr = gatt.addCharacteristic(thermometerCharacteristicUUID,
                                                     GATT_CHARS_PROPERTIES_READ | GATT_CHARS_PROPERTIES_NOTIFY,
                                                     sizeof(float), sizeof(float), BLE_DATATYPE_BYTEARRAY);
  /* Thermo characteristics, min temp */
  uint8_t thermometerMinCharacteristicUUID = 0x2222; 
  temperatureCharacteristicMin = gatt.addCharacteristic(thermometerMinCharacteristicUUID,
                                                     GATT_CHARS_PROPERTIES_READ | GATT_CHARS_PROPERTIES_NOTIFY,
                                                     sizeof(float), sizeof(float), BLE_DATATYPE_BYTEARRAY);
  /* Thermo characteristics, max temp */
  uint8_t thermometerMaxCharacteristicUUID3 = 0x2223; 
  temperatureCharacteristicMin = gatt.addCharacteristic(thermometerMaxCharacteristicUUID3,
                                                     GATT_CHARS_PROPERTIES_READ | GATT_CHARS_PROPERTIES_NOTIFY,
                                                     sizeof(float), sizeof(float), BLE_DATATYPE_BYTEARRAY);

  /* Battery characteristic */
  uint8_t batteryCharacteristicUUID = 0x2224; 
  batteryCharacteristic = gatt.addCharacteristic(batteryCharacteristicUUID,
                                                     GATT_CHARS_PROPERTIES_READ | GATT_CHARS_PROPERTIES_NOTIFY,
                                                     sizeof(float), sizeof(float), BLE_DATATYPE_BYTEARRAY);

  /* Reset the device for the new service setting changes to take effect */
  Serial.print(F("Performing a SW reset (service changes require a reset): "));
  ble.reset();
  
//  Serial.println(F("Change power to -16dB to save power" ));
//  ble.sendCommandCheckOK("AT+BLEPOWERLEVEL=-16");

  Serial.println(F("Now, please use Adafruit Bluefruit LE app to connect in UART mode"));
  Serial.println();

  ble.verbose(false);  // debug info is a little annoying after this point!

  // LED Activity command is only supported from 0.6.6
  if ( ble.isVersionAtLeast(MINIMUM_FIRMWARE_VERSION) )
  {
    // Change Mode LED Activity
    Serial.println(F("******************************"));
    Serial.println(F("Change LED activity to " MODE_LED_BEHAVIOUR));
    ble.sendCommandCheckOK("AT+HWModeLED=" MODE_LED_BEHAVIOUR);
    Serial.println(F("******************************"));
  }
}

//******************************
// SETUP
//******************************
void setup(void)
{ 
//*** uncomment to wait for the serial debug console ***
//  while (!Serial);  // required for Flora & Micro
//    delay(500);

  Serial.begin(115200);
  Serial.println(F("Adafruit Bluefruit --- Temperature sensor by Matt"));
  Serial.println(F("-------------------------------------------------"));
  setupBLE();
  setupMaxim();
}

float tLastVal = 0;
float bLastVal = 0;

//******************************
// LOOP
//******************************
void loop(void)
{  
  tCelsius.value = getKTemp();
  bPercent.value = getBattPercent();

  //debug print
  Serial.print("Temperature for the device 1 (index 0) is: ");
  Serial.println(tCelsius.value);   
  Serial.print("Batt percent: ");
  Serial.println(bPercent.value);
  
  //avoid NAN numbers
  if(isnan(tCelsius.value))
    Serial.println("NAN val");
  else{
    if(tCelsius.value != tLastVal){
       updateTempCounters(tCelsius.value);
       gatt.setChar(temperatureCharacteristicCurr, tCelsius.bytes, sizeof(tCelsius));
    }
    tLastVal= tCelsius.value;
  }

  //update batt value
  if(bPercent.value != bLastVal) 
    gatt.setChar(batteryCharacteristic, bPercent.bytes, sizeof(bPercent));
  bLastVal = bPercent.value;
  
  //delay a bit
  delay(200);
}
