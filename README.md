# Wearable Joint Kinematics Assessment Device
This project implements a wearable inertial sensing system to measure human joint angular motion and smoothness using a low-cost IMU and microcontroller.

## Overview
The system captures gyroscopic data from a body-mounted IMU, computes angular velocity, integrates joint angle over time, and calculates angular jerk as an indicator of motino smoothness and high-stress joint events.

## Hardware
- Rasberry Pi
- ICM-20948 9-DOF IMU
- Breadboard Wires
- I2C Communication

- ## Methods
- Gyroscope bias calibration
- Numerical integration for joint angle estimation
- Angular jerk computation
- Time-series data logging for offline analysis
- Angular jerk computation
- Time-series data logging for offline analysis

- ## Results
- The system captures:
- Join angle trajectories during voluntary motion
- High-jerk events during rapid direction changes
- Gyroscope drift during static periods

- ## Applications
- Biomechanics
- Rehabilitation monitoring
- Injury risk assessment

- ## Future fixes
- Drift compensation
- Sensor fusion
- Multi-joint tracking
