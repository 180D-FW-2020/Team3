#include <motor.h>
#include <ctype.h>

// Pin Definitions
#define BATTERY_MONITOR_PIN A0
#define LEFT_RPM_PIN 12
#define RIGHT_RPM_PIN 13
#define MOTOR_R_PWM 3
#define MOTOR_R_IN1 A3
#define MOTOR_R_IN2 A4
#define MOTOR_L_PWM 11
#define MOTOR_L_IN1 A1
#define MOTOR_L_IN2 A2
#define LOCK_SERVO_PIN 9
#define CAMERA_SERVO_PIN 5 
#define LOCK_SENSOR_PIN 3
#define RANGE_TRIG_PIN 6
#define RANGE_ECHO_PIN 4
#define RED_LED_EN_PIN A5
#define GREEN_LED_EN_PIN A6
#define BLUE_LED_EN_PIN A7
#define RESERVED_1 D8
#define RESERVED_1 D7
#define RESERVED_1 D5
// Hardware Constants
#define VM 14.8
#define BATTERY_R1 1000000
#define BATTERY_R2 200000

// Serial buffer
char com_buff[256];
int com_buff_count;

// Flags
byte error_flag = 0; // 0 for invalid motor message, 1 for etc. etc, need to document this.
bool stationary = true;
bool direction_change = false;

// WALL-U
Motor left_motor = Motor(11, A1, A2);
Motor right_motor = Motor(3, A3, A4);
MotorDirection current_dir = FORWARD;
MotorDirection requested_dir;
int requested_throttle = 0;

byte servo_position = 0; // placeholder until servo library made
byte lock_status = 0;    // 1 for locked, 0 for unlocked

// HUD
int battery_level = -1;
unsigned int rpm_right = -1;
unsigned int rpm_left = -1;

//Motor motor1 = Motor(9, 8, 7);

void self_test() {
  strcpy(com_buff, "MFM0");
  com_buff_count = 4;
  process_command();
  Serial.println(requested_dir);
  Serial.println(requested_throttle);
}

float calculate_battery(int read_in) {
  // Vout = Vs x R2 / R1 + R2
  // Vout * (R1 + R2) / R2 = Vs
  float voltage = analogRead(BATTERY_MONITOR_PIN);
  voltage = map(voltage, 0, 1023, 0, 5);
  return (voltage * (BATTERY_R1 + BATTERY_R2) / BATTERY_R1) / VM;
}

void process_command() {
  
  if (com_buff_count == 1) {
    ;
  }
  // Motor Commands
  if (com_buff_count == 4) {
    if (com_buff[0] == 'M') {
      if (com_buff[1] == 'F')
        requested_dir = FORWARD;
      else if (com_buff[1] == 'B')
        requested_dir = BACKWARD;
      else
        error_flag = 1; 
    }
    if (com_buff[2] == 'M') //max speed
      requested_throttle = 100;
    else if (isDigit(com_buff[2]) && isDigit(com_buff[3])) {
      requested_throttle = atoi(com_buff+2);
    }
    else
      error_flag = 1;
      
  }
  //command stored in 256 byte buffer => can implement multi-char commands too
}

void check_for_command() {
  //buffer incoming data until ; indicates end of command
  char incomingByte;
  while (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == ';') {
      process_command();
      memset(com_buff, 0, sizeof(com_buff));
      com_buff_count = 0;
    }
    else {
      com_buff[com_buff_count] = incomingByte;
      com_buff_count += 1;
    }
  }
}

//void process_movement(bool stationary, 
void setup() {
  // Initialization of all Arduino pins
  pinMode(BATTERY_MONITOR_PIN, INPUT);
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(7,OUTPUT);
  Serial.begin(9600);

}

void loop() {
  check_for_command();
  self_test();
}
