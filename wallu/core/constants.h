#pragma once
// Pin definitions
#define BATTERY_MONITOR_PIN A0
#define LEFT_RPM_PIN 12
#define RIGHT_RPM_PIN 13
#define MOTOR_R_PWM 3
#define MOTOR_R_IN1 A3
#define MOTOR_R_IN2 A4
#define MOTOR_L_PWM 11
#define MOTOR_L_IN1 A1
#define MOTOR_L_IN2 A2
#define LOCK_SERVO_PIN 9
#define CAMERA_SERVO_PIN 5
#define LOCK_SENSOR_PIN 2
#define RANGE_TRIG_PIN 6
#define RANGE_ECHO_PIN 4
#define RED_LED_EN_PIN A5
#define GREEN_LED_EN_PIN A6
#define BLUE_LED_EN_PIN A7
#define RESERVED_1 D8
#define RESERVED_2 D7
#define RESERVED_3 D5
// Hardware Constants
#define VM 15.6
#define BATT_MIN 15.1
#define BATT_MAX 16.0
#define BATTERY_R1 1000000
#define BATTERY_R2 200000

enum MotorDirection
{
    STOP,
    FORWARD,
    BACKWARD
};