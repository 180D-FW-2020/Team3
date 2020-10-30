#pragma once

namespace core::movement
{

    struct MotorDriverPinSet
    {
        int pwm;
        int forward;
        int backward;
    };

    enum MotorDirection
    {
        STOP,
        FORWARD,
        BACKWARD
    };

    class Motor
    {
    public:
        Motor(const int &enable_pin, const int &forward_pin, const int &backward_pin);
        void set_throttle(int pwm_value, MotorDirection dir);
        int get_rpm();

    private:
        MotorDriverPinSet m_pins{};
        MotorDirection m_dir;

        int m_rpm;
        int m_pwm;
    };

} // namespace core::movement