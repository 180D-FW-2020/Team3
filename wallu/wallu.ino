#include <motor.h>
#include <motor_control.h>
#include <comms.h>
#include <ctype.h>
#include <Servo.h>

// WALL-U
MotorControl motor_control = MotorControl();
SerialComms wallu_comms = SerialComms();
bool stationary = true;

Servo lock_servo;
Servo camera_servo;
byte servo_position = 0; // placeholder until servo library made
byte lock_hall = -1;
auto lock_timer = 0;

// HUD
int battery_level = -1;
unsigned int rpm_right = 0;
unsigned int rpm_left = 0;
byte lock_status = 1; // 1 for locked, 0 for unlocked

void print_all()
{
  /*
  Serial.print("T"); Serial.print(current_throttle);
  Serial.print("M"); Serial.print(left_motor.get_pwm());
  Serial.print("M"); Serial.print(right_motor.get_pwm());
  Serial.print("A"); Serial.print(steering_angle);
  Serial.print("D"); Serial.print(current_dir);
  Serial.print("B"); Serial.print(battery_level);
  Serial.print("R"); Serial.print(rpm_right);
  Serial.print("L"); Serial.print(rpm_right);
  Serial.print("S"); Serial.print(stationary);
  Serial.print("T"); Serial.println(lock_status);
  */
}
void self_test()
{
  /*
  strcpy(com_buff, "MF90M0");
  com_buff_count = 4;
  process_command();
  memset(com_buff, 0, sizeof(com_buff));
  com_buff_count = 0;
  */
  ;
}

int calculate_battery(int read_in)
{
  // Vout = Vs x R2 / R1 + R2
  // Vout * (R1 + R2) / R2 = Vs
  float val = analogRead(read_in);
  float input_voltage = val / 1023.0 * 5.0;
  float raw_voltage = (input_voltage * (BATTERY_R1 + BATTERY_R2) / BATTERY_R2);
  if (raw_voltage < BATT_MIN)
    return 0;
  return 100.0 * (raw_voltage - BATT_MIN) / (BATT_MAX - BATT_MIN);
}

void setup()
{
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
  //pinMode(CAMERA_SERVO_PIN, OUTPUT);
  pinMode(LOCK_SENSOR_PIN, INPUT);
  pinMode(RANGE_TRIG_PIN, INPUT); // need to double check
  pinMode(RANGE_ECHO_PIN, INPUT);
  pinMode(RED_LED_EN_PIN, OUTPUT);
  pinMode(GREEN_LED_EN_PIN, OUTPUT);
  pinMode(BLUE_LED_EN_PIN, OUTPUT);
  lock_servo.attach(LOCK_SERVO_PIN);
  Serial.begin(9600);
  self_test();
}

void loop()
{
  // Read in Serial messages from Pi
  wallu_comms.check_for_request();

  // Handle motor requests
  if (wallu_comms.check_flag(MOTOR))
  {
    int check = motor_control.process_request(wallu_comms.get_req_dir(), wallu_comms.get_req_throttle(), wallu_comms.get_req_angle());
    wallu_comms.set_flag(MOTOR, false);
  }

  // Handle servo requests
  if (wallu_comms.check_flag(CAMERA))
  {
    ;
  }

  // Handle unlock requests
  if (wallu_comms.check_flag(UNLOCK))
  {
    if (stationary)
    {                        // locked and stationary
      lock_servo.write(200); // unlocked
      lock_status = 0;
      lock_timer = millis();
    }
    wallu_comms.set_flag(UNLOCK, false);
  }

  // update WALL-U HUD status
  battery_level = calculate_battery(BATTERY_MONITOR_PIN);
  // Read in RPM sensors, then do this
  if (rpm_right == 0 && rpm_left == 0)
    stationary = true; // FIX

  // Lock after 5 seconds
  if (!lock_status)
  {
    if (millis() - lock_timer > 5000)
    {
      lock_servo.write(110);
      lock_status = 1;
    }
  }
}
