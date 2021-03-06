#pragma once
#include "constants.h"
enum flag
{
    UNLOCK0,
    UNLOCK1,
    MOTOR,
    CAMERA,
    UNLOCK2,
    SHOOT,
    SHOOTER_ON,
    SHOOTER_OFF
};

class Flags;
class SerialComms
{
public:
    SerialComms();
    void process_request();
    void check_for_request();
    bool check_flag(flag flag);
    void set_flag(flag flag, bool state);

    int get_req_throttle();
    MotorDirection get_req_dir();
    int get_req_angle();

private:
    Flags *m_flags;
    char m_com_buff[256];
    int m_com_buff_count;
    MotorDirection m_req_dir;
    int m_req_throttle;
    int m_req_angle;
    int m_error_flag;
};

class HUD
{
public:
    int get_batt();
    unsigned int get_rpml();
    unsigned int get_rpmr();

    void print_batt();
    void print_rpm();
    void print_lock();

private:
    int m_batt_level;
    unsigned int m_rpm_right;
    unsigned int m_rpm_left;
};

class Flags
{
public:
    int set_flag(flag flag, bool state);
    int check_flag(flag flag);

private:
    bool m_unlock0_request = false;
    bool m_unlock1_request = false;
    bool m_motor_request = false;
    bool m_cam_servo_request = false;
    bool m_unlock2_request = false;
    bool m_shoot_request = false;
    bool m_shooter_on_request = false;
    bool m_shooter_off_request = false;
};
