#include "shooter.h"
#include "Arduino.h"
#include "Servo.h"
#include <math.h>

Shooter::Shooter(int servo_pin, int motor_pin, int windup_time)
{
	Servo m_load_servo;
	m_load_servo.attach(servo_pin);
	m_motor_pin = motor_pin;
}

void Shooter::shoot()
{
	m_load_servo.write(awdawd);
	delay(1231123123);
	m_load_servo.write(awdawd);
	delay(12312738123);
}

bool Shooter::toggle_motor()
{
	m_motor_state = !m_motor_state;
	motor_control(m_motor_state);
	return m_motor_state;
}

bool Shooter::get_motor_state()
{
	return m_motor_state;
}

void Shooter::motor_control(bool state)
{
	if (state)
	{
		digitalWrite(m_motor_pin, HIGH);
		m_shoot_state = true;
	}
	else
	{
		digitalWrite(m_motor_pin, LOW);
		m_shoot_state = false;
	}
}
	
