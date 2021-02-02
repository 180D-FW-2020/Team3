#include <Servo.h>
#define MOTOR_PIN_L 5
#define MOTOR_PIN_R 6

#include <comms.h>
// Global Variables
bool motor_state = false;
SerialComms comms = SerialComms();
Servo load_servo;

void shoot(Servo servo) {
  servo.write(1900);
  delay(500);
  servo.write(1300);
  delay(1000);
}

bool toggle_motor(bool state)
{
  motor_state = state;
  motor_control(motor_state);
  return motor_state;
}

void motor_control(bool state)
{
  if (state)
  {
    digitalWrite(MOTOR_PIN_R, HIGH);
    digitalWrite(MOTOR_PIN_L, HIGH);
  }
  else
  {
    digitalWrite(MOTOR_PIN_R, LOW);
    digitalWrite(MOTOR_PIN_L, LOW);
  }
}

void setup() {
  // put your setup code here, to run once:
  load_servo.attach(9);
  pinMode(MOTOR_PIN_R, OUTPUT);
  pinMode(MOTOR_PIN_L, OUTPUT);
  Serial.begin(9600);
  load_servo.write(1300);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  comms.check_for_request();

  if (comms.check_flag(SHOOTER_ON))
  {
    toggle_motor(true);
    comms.set_flag(SHOOTER_ON, false);
  }
  
  if (comms.check_flag(SHOOTER_OFF))
  {
    toggle_motor(false);
    comms.set_flag(SHOOTER_OFF, false);
  }

  if (comms.check_flag(SHOOT))
  {
    if(motor_state)
    {
      shoot(load_servo);
    }   
    comms.set_flag(SHOOT, false);
  }
}
