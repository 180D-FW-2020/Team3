#include <motor.h>
//#include <rpm.h>
#include <ctype.h>
#include "constants.h"
// RPI Incoming Messages
char com_buff[256];
int com_buff_count;


// Flags
byte error_flag = 0; // 0 for invalid motor message, 1 for etc. etc, need to document this.
bool stationary = true;
bool direction_change = false;

bool motor_request = false;
bool cam_servo_request = false;

// WALL-U
Motor left_motor = Motor(MOTOR_L_PWM, MOTOR_L_IN1, MOTOR_L_IN2);
Motor right_motor = Motor(MOTOR_R_PWM, MOTOR_R_IN1, MOTOR_R_IN2);
MotorDirection current_dir = FORWARD;
int steering_angle = 0;
int requested_steering_angle = -1;
MotorDirection requested_dir;
int requested_throttle = 0;

byte servo_position = 0; // placeholder until servo library made
byte lock_hall = -1;

// HUD
int battery_level = -1;
unsigned int rpm_right = -1;
unsigned int rpm_left = -1;
byte lock_status = 0;    // 1 for locked, 0 for unlocked

//Motor motor1 = Motor(9, 8, 7);

void self_test() {
  strcpy(com_buff, "MF90M0");
  com_buff_count = 4;
  process_command();
  Serial.println(requested_dir);
  Serial.println(requested_throttle);
}

void process_movement(MotorDirection dir, int throttle, int angle) {
  throttle = 255; // Temporary
  if (dir == BACKWARD) {
    //Run normally
    left_motor.set_throttle(throttle, BACKWARD);
    right_motor.set_throttle(throttle, BACKWARD);
  }
  else if (dir == FORWARD) { // if it's forward, we need to account for turning
    int percentage = map(abs(angle), 0, 90, 0, 100);
    float reduction = 100.0 - (float)percentage;
    int new_pwm = reduction / 100.0 * throttle;
    if (angle < 0) {
      // Reduce left motor speed to turn left
      left_motor.set_throttle(new_pwm, FORWARD);
      right_motor.set_throttle(throttle, FORWARD);
    }
    else if (angle > 0) {
      // Reduce right motor speed to turn right
      left_motor.set_throttle(throttle, FORWARD);
      right_motor.set_throttle(new_pwm, FORWARD);
    }
    else {
      // Go straight
      left_motor.set_throttle(throttle, FORWARD);
      right_motor.set_throttle(throttle, FORWARD);
    }
  }
  else if (dir == STOP) {
    left_motor.set_throttle(throttle, STOP);
    right_motor.set_throttle(throttle, STOP);
  }
  else {
    error_flag = 2;
  }
}

int calculate_battery(int read_in) {
  // Vout = Vs x R2 / R1 + R2
  // Vout * (R1 + R2) / R2 = Vs
  float val = analogRead(read_in);
  float input_voltage = val / 1023.0 * 5.0;
  float raw_voltage = (input_voltage * (BATTERY_R1 + BATTERY_R2) / BATTERY_R2);
  if (raw_voltage < BATT_MIN)
    return 0;
  return 100.0 * (raw_voltage - BATT_MIN) / (BATT_MAX - BATT_MIN);
}

void process_command() {
  char atoi_buff[2];
  if (com_buff_count == 1) {
    ;
  }
  // Servo commands S_ _ _ (angle)
  if (com_buff_count == 4) {
    ;
  }
  // Motor Commands
  if (com_buff_count == 6) {
    if (com_buff[0] == 'M') {
      if (com_buff[1] == 'F')
        requested_dir = FORWARD;
      else if (com_buff[1] == 'B')
        requested_dir = BACKWARD;
      else if (com_buff[1] == 'S')
        requested_dir = STOP;
      else
        error_flag = 1; 
    }
    if (isDigit(com_buff[2]) && isDigit(com_buff[3])) {
      atoi_buff[0] = com_buff[2];
      atoi_buff[1] = com_buff[3];
      requested_steering_angle = atoi(atoi_buff);
    }
    else
      error_flag = 1;
    if (com_buff[4] == 'M') //max speed
      requested_throttle = 100;
    else if (isDigit(com_buff[4]) && isDigit(com_buff[5]))
      requested_throttle = atoi(com_buff+4);
    else
      error_flag = 1;
  }
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
 
void setup() {
  // Initialization of all Arduino pins
  pinMode(BATTERY_MONITOR_PIN, INPUT);
  pinMode(LEFT_RPM_PIN, INPUT);
  pinMode(RIGHT_RPM_PIN, INPUT);
  pinMode(MOTOR_R_PWM, OUTPUT);
  pinMode(MOTOR_R_IN1, OUTPUT);
  pinMode(MOTOR_R_IN2, OUTPUT);
  pinMode(MOTOR_R_PWM, OUTPUT);
  pinMode(MOTOR_L_IN1, OUTPUT);
  pinMode(MOTOR_L_IN2, OUTPUT);
  pinMode(LOCK_SERVO_PIN, OUTPUT);
  pinMode(CAMERA_SERVO_PIN, OUTPUT);
  pinMode(LOCK_SENSOR_PIN, INPUT);
  pinMode(RANGE_TRIG_PIN, INPUT); // need to double check
  pinMode(RANGE_ECHO_PIN, INPUT);
  pinMode(RED_LED_EN_PIN, OUTPUT);
  pinMode(GREEN_LED_EN_PIN, OUTPUT);
  pinMode(BLUE_LED_EN_PIN, OUTPUT);
  Serial.begin(9600);
  self_test();
}

void loop() {
  // Read in Serial messages from Pi
  check_for_command();

  // Handle motor requests
  if (motor_request) {
    if (requested_dir == STOP)
      process_movement(requested_dir, requested_throttle, requested_steering_angle);
    else if (requested_dir != current_dir) {
      if (stationary)
        process_movement(requested_dir, requested_throttle, requested_steering_angle);
      else
        process_movement(STOP, requested_throttle, requested_steering_angle);
    }
    else
      process_movement(requested_dir, requested_throttle, requested_steering_angle);
    motor_request= 0;
  }

  // Handle servo requests
  if (cam_servo_request) {
    ;
  }
  // update WALL-U HUD status
  battery_level = calculate_battery(BATTERY_MONITOR_PIN);
  // Read in RPM sensors, then do this
  if (rpm_right == 0 && rpm_left == 0)
    stationary = 0;
  // Lock status

  //
}
