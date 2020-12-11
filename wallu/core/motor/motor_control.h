#pragma once
#include "constants.h"
class Motor;
class MotorControl
{
public:
    MotorControl();
    int process_request(MotorDirection req_dir, int req_throttle, int req_angle);
    int perform_movement(MotorDirection dir, int throttle, int angle);
    int check_stationary();

private:
    Motor *m_left_motor;
    Motor *m_right_motor;
    MotorDirection m_current_dir;
    int m_angle;
    int m_throttle;
    bool m_stationary;
};