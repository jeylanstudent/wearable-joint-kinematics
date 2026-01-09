from machine import Pin, I2C
import time, struct

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=50_000)
ADDR = 0x69

REG_BANK_SEL = 0x7F
PWR_MGMT_1   = 0x06
GYRO_XOUT_H  = 0x33
GYRO_CONFIG_1 = 0x01

def bank(n):
    i2c.writeto_mem(ADDR, REG_BANK_SEL, bytes([n << 4]))
    time.sleep_ms(5)

def write_reg(reg, val):
    i2c.writeto_mem(ADDR, reg, bytes([val]))
    time.sleep_ms(5)

def safe_read(reg, n, tries=5):
    for _ in range(tries):
        try:
            return i2c.readfrom_mem(ADDR, reg, n)
        except OSError:
            time.sleep_ms(10)
    return None

# ---- IMU init ----
bank(0); write_reg(PWR_MGMT_1, 0x01)
bank(2); write_reg(GYRO_CONFIG_1, 0x00)   # ±250 dps
bank(0)

scale = 131.0  # LSB per deg/s for ±250 dps

# ---- Calibrate gyro bias (keep IMU still) ----
print("Hold IMU still for 3 seconds (calibrating)...")
bx = 0.0
count = 0
t_end = time.ticks_add(time.ticks_ms(), 3000)

while time.ticks_diff(t_end, time.ticks_ms()) > 0:
    data = safe_read(GYRO_XOUT_H, 6)
    if data:
        gx, gy, gz = struct.unpack(">hhh", data)
        bx += gx / scale
        count += 1
    time.sleep_ms(10)

bx /= max(count, 1)
print("Bias X (deg/s):", round(bx, 4))

# ---- Open CSV file ----
filename = "joint_log.csv"
f = open(filename, "w")
f.write("t_s,gyro_x_dps,angle_x_deg,gyro_x_jerk_dps2\n")

print("Logging to", filename)
print("Move IMU. Press Ctrl+C to stop and save.")

# ---- Logging loop ----
angle_x = 0.0
last_ms = time.ticks_ms()
t0_ms = last_ms

prev_gx = 0.0

try:
    while True:
        data = safe_read(GYRO_XOUT_H, 6)
        now_ms = time.ticks_ms()

        dt = time.ticks_diff(now_ms, last_ms) / 1000.0
        last_ms = now_ms

        if data and dt > 0:
            gx_raw, gy_raw, gz_raw = struct.unpack(">hhh", data)
            gx = gx_raw / scale - bx  # deg/s

            # integrate to angle
            angle_x += gx * dt

            # "jerk" proxy (change in gyro rate per second)
            jerk = (gx - prev_gx) / dt
            prev_gx = gx

            t_s = time.ticks_diff(now_ms, t0_ms) / 1000.0

            # write row
            f.write("{:.3f},{:.4f},{:.3f},{:.3f}\n".format(t_s, gx, angle_x, jerk))

            # print occasionally
            if int(t_s * 5) % 5 == 0:  # about once per second-ish
                print("t", round(t_s,1), "gyro_x", round(gx,2), "angle_x", round(angle_x,1))

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    f.close()
    print("Saved:", filename)



# Print the CSV file to the console so we can copy it

filename = "joint_log.csv"

with open(filename, "r") as f:
    for line in f:
        print(line, end="")

