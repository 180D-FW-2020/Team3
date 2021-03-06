#include "comms.h"
#include "Arduino.h"

SerialComms::SerialComms()
{
    m_flags = new Flags();
    m_com_buff_count = 0;
    m_req_dir = STOP;
    m_req_throttle = 0;
    m_req_angle = 0;
    m_error_flag = 0;
}

bool SerialComms::check_flag(flag flag)
{
    return m_flags->check_flag(flag);
}

void SerialComms::set_flag(flag flag, bool state)
{
    m_flags->set_flag(flag, state);
}
void SerialComms::process_request()
{
    char atoi_buff[2];
    if (m_com_buff_count == 2)
    {
        if (m_com_buff[1] == '0')
            m_flags->set_flag(UNLOCK0, true);
        if (m_com_buff[1] == '1') // unlock
            m_flags->set_flag(UNLOCK1, true);
        if (m_com_buff[1] == '2')
            m_flags->set_flag(UNLOCK2, true);
    }
    else if (m_com_buff_count == 3)
    {
        if (m_com_buff[2] == 'n')
            m_flags->set_flag(SHOOTER_ON, true);
        if (m_com_buff[2] == 'f')
            m_flags->set_flag(SHOOTER_OFF, true);
        if (m_com_buff[2] == 'i')
            m_flags->set_flag(SHOOT, true);
    }
    // Servo commands S_ _ _ (angle)
    else if (m_com_buff_count == 4)
        ;
    // Motor Commands
    else if (m_com_buff_count == 7)
    {
        if (m_com_buff[0] == 'M')
        {
            if (m_com_buff[1] == 'F')
                m_req_dir = FORWARD;
            else if (m_com_buff[1] == 'B')
                m_req_dir = BACKWARD;
            else if (m_com_buff[1] == 'S')
                m_req_dir = STOP;
            else
                m_error_flag = 1;
        }
        int multiplier = 1;
        if (m_com_buff[2] == 'N') // NEGATIVE
            multiplier = -1;
        else if (m_com_buff[2] == 'P') // POSITIVE
            multiplier = 1;
        else
            m_error_flag = 1;
        if (isDigit(m_com_buff[3]) && isDigit(m_com_buff[4]))
        {
            atoi_buff[0] = m_com_buff[3];
            atoi_buff[1] = m_com_buff[4];
            m_req_angle = atoi(atoi_buff) * multiplier;
        }
        else
            m_error_flag = 1;
        if (m_com_buff[5] == 'M') //max speed
            m_req_throttle = 100;
        else if (isDigit(m_com_buff[5]) && isDigit(m_com_buff[6]))
            m_req_throttle = atoi(m_com_buff + 5);
        else
            m_error_flag = 1;
        if (m_error_flag != 1)
            m_flags->set_flag(MOTOR, true);
    }
}
void SerialComms::check_for_request()
{
    //buffer incoming data until ; indicates end of command
    char incomingByte;
    while (Serial.available() > 0)
    {
        incomingByte = Serial.read();
        if (incomingByte == '\r' || incomingByte == '\n')
            continue;
        if (incomingByte == ';')
        {
            process_request();
            memset(m_com_buff, 0, sizeof(m_com_buff));
            m_com_buff_count = 0;
        }
        else
        {
            m_com_buff[m_com_buff_count] = incomingByte;
            m_com_buff_count += 1;
        }
    }
}

int SerialComms::get_req_throttle()
{
    return m_req_throttle;
}
MotorDirection SerialComms::get_req_dir()
{
    return m_req_dir;
}
int SerialComms::get_req_angle()
{
    return m_req_angle;
}
int HUD::get_batt()
{
    ;
}

unsigned int HUD::get_rpml()
{
    ;
}

unsigned int HUD::get_rpmr()
{
    ;
}

void HUD::print_batt()
{
    ;
}

void HUD::print_rpm()
{
    ;
}

void HUD::print_lock()
{
    ;
}

int Flags::set_flag(flag flag, bool state)
{
    switch (flag)
    {
    case SHOOT:
        m_shoot_request = state;
        break;
    case SHOOTER_ON:
        m_shooter_on_request = state;
        break;
    case SHOOTER_OFF:
        m_shooter_off_request = state;
        break;
    case MOTOR:
        m_motor_request = state;
        break;
    case UNLOCK0:
        m_unlock0_request = state;
        break;
    case UNLOCK1:
        m_unlock1_request = state;
        break;
    case UNLOCK2:
        m_unlock2_request = state;
        break;
    case CAMERA:
        m_cam_servo_request = state;
        break;
    }
}

int Flags::check_flag(flag flag)
{
    switch (flag)
    {
    case SHOOT:
        return m_shoot_request;
        break;
    case SHOOTER_ON:
        return m_shooter_on_request;
        break;
    case SHOOTER_OFF:
        return m_shooter_off_request;
        break;
    case MOTOR:
        return m_motor_request;
        break;
    case UNLOCK0:
        return m_unlock0_request;
        break;
    case UNLOCK1:
        return m_unlock1_request;
        break;
    case UNLOCK2:
        return m_unlock2_request;
        break;
    case CAMERA:
        return m_cam_servo_request;
        break;
    }
}