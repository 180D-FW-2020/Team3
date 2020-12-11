#pragma once
#include "constants.h"

struct MotorDriverPinSet
{
    int pwm;
    int forward;
    int backward;
};

class Motor
{
public:
    Motor(const int &enable_pin, const int &forward_pin, const int &backward_pin);
    void set_throttle(int pwm_value, MotorDirection dir);
    int get_rpm();
    int get_pwm();
    bool ramp();

private:
    MotorDriverPinSet m_pins{};
    MotorDirection m_dir;
    MotorDirection m_prev_dir;

    unsigned long m_timer;
    unsigned long m_stop_timer;
    int m_rpm;
    int m_pwm;
};
