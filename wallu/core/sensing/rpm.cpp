#include "rpm.h"
#include "Arduino.h"

void RpmSensor::read_sensor()
{
    auto time_diff = micros() - m_state.last_refresh_micros;
    m_sensor_value.rpm = m_state.ticks * 60000000l / time_diff;

    if (micros() - m_state.last_refresh_micros > 500000l)
    {
        m_state.ticks = 0;
        m_state.last_refresh_micros = micros();
    }
}

void RpmSensor::interrupt_handler()
{
    m_state.ticks += 1;
}
