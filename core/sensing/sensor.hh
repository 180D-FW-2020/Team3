#pragma once

template <class SensorDataType>
class Sensor
{
public:
    Sensor(const int &pin)
    {
        m_pin = pin;
    }

    virtual void read_sensor() = 0; // implemented differently for each sensor

    SensorDataType get_raw_value() const
    {
        return m_raw_value;
    }

    SensorDataType get_sensor_value() const
    {
        return m_sensor_value;
    }

private:
    SensorDataType m_raw_value;
    SensorDataType m_sensor_value;
    int m_pin;
};
