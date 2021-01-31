#include <motor.h>
#include <motor_control.h>
#include <comms.h>
#include <ctype.h>
#include <shooter.h>
#include <Servo.h>

// WALL-U
MotorControl motor_control = MotorControl();
SerialComms wallu_comms = SerialComms();
bool stationary = true;
bool shooter_state = false;
bool ready_to_shoot = false;

Servo lock_servo;
Servo camera_servo;
byte servo_position = 0; // placeholder until servo library made
byte lock_hall = -1;
auto lock_timer = 0;
auto unlock_timer = 0;
auto vital_timer = 0;
bool disable = 0; //disable wallu from moving

// HUD
int battery_level = -1;
unsigned int rpm_right = 0;
unsigned int rpm_left = 0;
byte lock_status = 1; // 1 for locked, 0 for unlocked

// Auxillury function
int NumDigits(int x)
{
  x = abs(x);
  return (x < 10 ? 1 : (x < 100 ? 2 : (x < 1000 ? 3 : (x < 10000 ? 4 : (x < 100000 ? 5 : (x < 1000000 ? 6 : (x < 10000000 ? 7 : (x < 100000000 ? 8 : (x < 1000000000 ? 9 : 10)))))))));
}

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

float calculate_battery(int read_in)
{
  // Vout = Vs x R2 / R1 + R2
  // Vout * (R1 + R2) / R2 = Vs
  float val = analogRead(read_in);
  float input_voltage = val / 1023.0 * 5.0;
  float raw_voltage = (input_voltage * (BATTERY_R1 + BATTERY_R2) / BATTERY_R2);
  return raw_voltage;
}

void set_eye_pattern(String pattern)
{
  if (pattern == "RED")
  {
    digitalWrite(RED_LED_EN_PIN, LOW);
    digitalWrite(GREEN_LED_EN_PIN, HIGH);
    digitalWrite(BLUE_LED_EN_PIN, HIGH);
  }
  else if (pattern == "GREEN")
  {
    digitalWrite(RED_LED_EN_PIN, HIGH);
    digitalWrite(GREEN_LED_EN_PIN, LOW);
    digitalWrite(BLUE_LED_EN_PIN, HIGH);
  }
  else if (pattern == "BLUE")
  {
    digitalWrite(RED_LED_EN_PIN, HIGH);
    digitalWrite(GREEN_LED_EN_PIN, HIGH);
    digitalWrite(BLUE_LED_EN_PIN, LOW);
  }
  else if (pattern == "WHITE")
  {
    digitalWrite(RED_LED_EN_PIN, LOW);
    digitalWrite(GREEN_LED_EN_PIN, LOW);
    digitalWrite(BLUE_LED_EN_PIN, LOW);
  }
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
  set_eye_pattern("BLUE"); // default eye color
  lock_servo.write(200);
}

void loop()
{
  // Read in Serial messages from Pi
  wallu_comms.check_for_request();

  // Handle motor requests
  if (wallu_comms.check_flag(MOTOR) && lock_status && !disable && !shooter_state)
  {
    int check = motor_control.process_request(wallu_comms.get_req_dir(), wallu_comms.get_req_throttle(), wallu_comms.get_req_angle());
  }
  wallu_comms.set_flag(MOTOR, false);

  // Read in RPM sensors, then do this
  if (motor_control.check_stationary())
    stationary = true;
  else
    stationary = false;
  // Handle servo requests
  if (wallu_comms.check_flag(CAMERA))
  {
    ;
  }

  if (wallu_comms.check_flag(UNLOCK0))
  {
    if (stationary && lock_status)
    {
      disable = 1;
      set_eye_pattern("GREEN");
      wallu_comms.set_flag(UNLOCK0, false);
    }
    //throw away request if its already unlocked
    if (lock_status == 0)
      wallu_comms.set_flag(UNLOCK0, false);
  }

  if (wallu_comms.check_flag(UNLOCK2))
  {
    wallu_comms.set_flag(UNLOCK2, false);
    disable = 0;
    set_eye_pattern("BLUE");
  }

  // Handle unlock requests
  if (wallu_comms.check_flag(UNLOCK1))
  {
    //Serial.println("got here");
    if (stationary)
    {                        // locked and stationary
      lock_servo.write(110); // unlocked
      lock_status = 0;
      lock_timer = millis();
      unlock_timer = millis();
      set_eye_pattern("WHITE");
    }
    wallu_comms.set_flag(UNLOCK1, false);
  }

  // Lock
  if (!lock_status && (millis() - unlock_timer > 5000))
  {
    if (!digitalRead(LOCK_SENSOR_PIN) && lock_hall == 0)
    {
      lock_timer = millis();
      lock_hall = 1;
    }
    else if (digitalRead(LOCK_SENSOR_PIN))
    {
      lock_hall = 0;
    }
    if (millis() - lock_timer > 500 && lock_hall == 1)
    {
      set_eye_pattern("BLUE");
      lock_servo.write(200);
      lock_status = 1;
      disable = 0;
    }
  }

  // update WALL-U HUD status
  battery_level = calculate_battery(BATTERY_MONITOR_PIN);

  if (millis() - vital_timer > 2500)
  {
    Serial.print("VIT");
    int info = int(battery_level * 10);
    if (NumDigits(info) != 3)
      info = 999;
    Serial.print(info - 16);
    Serial.print("-");
    char lock = 'L';
    if (!lock_status)
      lock = 'U';
    Serial.print(lock);
    Serial.print(";");
    vital_timer = millis();
  }
}
