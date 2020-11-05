#include "motor.hh"
#include <math.h>

Motor::Motor(const int &enable_pin, const int &forward_pin, const int &backward_pin)
{
    m_pins.pwm = enable_pin;
    m_pins.forward = forward_pin;
    m_pins.backward = backward_pin;
    m_rpm = 0;
    m_pwm = 0;
}

void Motor::set_throttle(int pwm_value, MotorDirection dir)
{
    auto bounded_pwm = fmin(255, fmax(0, pwm_value));
    m_pwm = bounded_pwm;
    m_dir = dir;

    switch (m_dir)
    {
    case STOP:
    {
        m_pwm = 0;
        digitalWrite(m_pins.backward, LOW);
        digitalWrite(m_pins.forward, LOW);
    }
    case FORWARD:
    {
        digitalWrite(m_pins.backward, LOW);
        digitalWrite(m_pins.forward, HIGH);
    }
    case BACKWARD:
    {
        digitalWrite(m_pins.backward, HIGH);
        digitalWrite(m_pins.forward, LOW);
    }
    }

    analogWrite(m_pins.pwm, m_pwm);
}
