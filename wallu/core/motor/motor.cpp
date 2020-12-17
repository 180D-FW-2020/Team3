#include "motor.h"
#include "Arduino.h"
#include <math.h>

Motor::Motor(const int &enable_pin, const int &forward_pin, const int &backward_pin)
{
    m_pins.pwm = enable_pin;
    m_pins.forward = forward_pin;
    m_pins.backward = backward_pin;
    m_prev_dir = STOP;
    m_dir = STOP;
    m_rpm = 0;
    m_pwm = 0;
    m_timer = millis();
    m_stop_timer = 0;
}

void Motor::set_throttle(int pwm_value, MotorDirection dir)
{
    auto bounded_pwm = fmin(255, fmax(0, pwm_value));

    switch (m_dir)
    {
    case STOP:
    {
        bounded_pwm = 0;
        // activate brakes if trying to stop
        if (dir == STOP)
        {
            digitalWrite(m_pins.backward, LOW);
            digitalWrite(m_pins.forward, LOW);
        }
        // if moving in same direction as last time, no need to delay
        else if (m_prev_dir == dir)
        {
            m_dir = dir;
            return;
        }
        else
        {
            if (millis() - m_stop_timer > 100)
            {
                m_dir = dir;
                return;
            }
        }
        break;
    }
    case FORWARD:
    {
        // Although we want to switch direction, slow down in current direction
        if (dir == BACKWARD || dir == STOP)
        {
            bounded_pwm = 0;
        }
        digitalWrite(m_pins.backward, LOW);
        digitalWrite(m_pins.forward, HIGH);
        break;
    }
    case BACKWARD:
    {
        if (dir == FORWARD || dir == STOP)
        {
            bounded_pwm = 0;
        }
        digitalWrite(m_pins.backward, HIGH);
        digitalWrite(m_pins.forward, LOW);
        break;
    }
    }

    if (ramp())
        if (bounded_pwm - m_pwm > 0) // increasing
        {
            m_pwm += 50;
            if (m_pwm > bounded_pwm)
                m_pwm = bounded_pwm;
        }
        else if (bounded_pwm - m_pwm < 0) //decreasing
        {
            m_pwm -= 90;
            if (m_pwm < bounded_pwm)
                m_pwm = bounded_pwm;
        }
    analogWrite(m_pins.pwm, m_pwm);
    if (m_pwm == 0 && m_dir != STOP)
    {
        m_stop_timer = millis();
        m_prev_dir = m_dir;
        m_dir = STOP;
    }
}

int Motor::get_pwm()
{
    return m_pwm;
}

bool Motor::ramp()
{
    unsigned long range = map(m_pwm, 0, 255, 40, 0);
    if ((millis() - m_timer) > range)
    {
        m_timer = millis();
        return true;
    }
    else
        return false;
}
