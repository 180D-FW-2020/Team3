#pragma once

#include "sensor.h"

struct RotationalSpeed
{
    int rpm;
    int linear;
};

struct RpmState
{
    volatile int ticks = 0;
    volatile unsigned long last_refresh_micros = 0;
};

class RpmSensor : public Sensor<RotationalSpeed, RpmState>
{
    void read_sensor();
    void interrupt_handler();
};
