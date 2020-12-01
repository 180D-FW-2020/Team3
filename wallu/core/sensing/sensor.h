#pragma once

template <class SensorDataType, class SensorState>
class Sensor
{
public:
    Sensor(const int &pin)
    {
        m_pin = pin;
        pinMode(m_pin, INPUT);
    }

    virtual void read_sensor() = 0; // implemented differently for each sensor

    int get_raw_value() const
    {
        return m_raw_value;
    }

    SensorDataType get_sensor_value() const
    {
        return m_sensor_value;
    }

protected:
    int m_raw_value;
    SensorDataType m_sensor_value;
    SensorState m_state;
    int m_pin;
};
