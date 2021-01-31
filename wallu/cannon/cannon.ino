#include <Servo.h>
#define MOTOR_PIN 5
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

bool toggle_motor()
{
  motor_state = !motor_state;
  motor_control(motor_state);
  return motor_state;
}

void motor_control(bool state)
{
  if (state)
  {
    digitalWrite(MOTOR_PIN, HIGH);
  }
  else
  {
    digitalWrite(MOTOR_PIN, LOW);
  }
}

void setup() {
  // put your setup code here, to run once:
  load_servo.attach(9);
  pinMode(5, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  comms.check_for_request();

  if (comms.check_flag(SHOOTER_TOGGLE))
  {
    toggle_motor();
    comms.set_flag(SHOOTER_TOGGLE, false);
  }

  if (comms.check_flag(SHOOT))
  {
    if(motor_state)
    {
      shoot(load_servo);
      comms.set_flag(SHOOT, false);
    }   
  }
}
