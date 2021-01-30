#pragma once
#include "constants.h"
#include "Servo.h"

class Servo;

class Shooter
{
public:
	Shooter(int servo_pin, int motor_pin, int windup_time);
	void shoot();
	bool toggle_motor();
	bool get_motor_state();

private:
	void motor_control(bool state);
	bool m_shoot_state;
	bool m_motor_state;
	int windup_time;
	Servo m_load_servo;
	int m_motor_pin;
};