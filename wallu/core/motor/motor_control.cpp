#include "motor_control.h"
#include "motor.h"
#include "Arduino.h"
#include <math.h>

MotorControl::MotorControl()
{
    m_left_motor = new Motor(MOTOR_L_PWM, MOTOR_L_IN1, MOTOR_L_IN2);
    m_right_motor = new Motor(MOTOR_R_PWM, MOTOR_R_IN1, MOTOR_R_IN2);
    MotorDirection m_current_dir = FORWARD;
    m_angle = 0;
    m_throttle = 0;
    m_stationary = true;
}
int MotorControl::process_request(MotorDirection req_dir, int req_throttle, int req_angle)
{
    int val = 0;
    if (req_dir == STOP)
        val = perform_movement(req_dir, req_throttle, req_angle);
    else if (req_dir != m_current_dir)
    {
        if (m_stationary)
            val = perform_movement(req_dir, req_throttle, req_angle);
        else
            val = perform_movement(STOP, req_throttle, req_angle);
    }
    else
    {
        val = perform_movement(req_dir, req_throttle, req_angle);
    }
    return val;
}

int MotorControl::perform_movement(MotorDirection dir, int throttle, int angle)
{
    throttle = map(throttle, 0, 100, 0, 255);
    if (dir == BACKWARD)
    {
        //Run normally
        m_left_motor->set_throttle(throttle, BACKWARD);
        m_right_motor->set_throttle(throttle, BACKWARD);
    }
    else if (dir == FORWARD)
    { // if it's forward, we need to account for turning
        if (thottle < 5)
        {
            throttle = 0;
        }
        else if (throttle < 15)
        {
            throttle = 15;
        }
        int percentage = map(abs(angle), 0, 90, 0, 100);
        float reduction = 100.0 - (float)percentage;
        int new_pwm = reduction / 100.0 * throttle;
        if (angle < 0)
        {
            // Reduce left motor speed to turn left
            m_left_motor->set_throttle(new_pwm, FORWARD);
            m_right_motor->set_throttle(throttle, FORWARD);
        }
        else if (angle > 0)
        {
            // Reduce right motor speed to turn right
            m_left_motor->set_throttle(throttle, FORWARD);
            m_right_motor->set_throttle(new_pwm, FORWARD);
        }
        else
        { // Go straight
            m_left_motor->set_throttle(throttle, FORWARD);
            m_right_motor->set_throttle(throttle, FORWARD);
        }
    }
    else if (dir == STOP)
    {
        m_left_motor->set_throttle(throttle, STOP);
        m_right_motor->set_throttle(throttle, STOP);
    }
    else
    {
        return 1;
    }
    m_throttle = throttle;
    m_angle = angle;
    m_current_dir = dir;
    return 0;
}