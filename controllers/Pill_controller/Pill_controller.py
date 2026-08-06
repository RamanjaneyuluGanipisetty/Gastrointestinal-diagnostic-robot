from controller import Supervisor, Keyboard
import os

# Enable camera device
def setup_camera(robot, timestep):
    camera = robot.getDevice("camera") or robot.getDevice("CMOS_CAMERA")
    if camera:
        camera.enable(timestep)
    return camera

# Enable distance, pressure, and gyro sensors
def setup_sensors(robot, timestep):
    optical = robot.getDevice("optical_Blood_Detector") or robot.getDevice("distance sensor")
    pressure = robot.getDevice("Pressure_Blood_Detector") or robot.getDevice("touch sensor")
    gyro = robot.getDevice("gyro") or robot.getDevice("Gyro")

    if optical: optical.enable(timestep)
    if pressure: pressure.enable(timestep)
    if gyro: gyro.enable(timestep)

    print("Sensors Enabled")
    return optical, pressure, gyro

# Alert if optical distance or pressure breaches limits
def check_abnormalities(optical, pressure, optical_limit, pressure_limit, alert_delay):
    if alert_delay == 0 and (optical < optical_limit or pressure > pressure_limit):
        print("\n*** ABNORMALITY DETECTED ***")
        print("Optical :", optical)
        print("Pressure:", pressure)
        return 30
    return max(0, alert_delay - 1)

# Calculate 3D velocity relative to capsule orientation
def get_movement_velocity(key, robot_node, drive_speed, turn_speed):
    vx = vy = vz = wx = wy = wz = 0
    if not robot_node:
        return [vx, vy, vz, wx, wy, wz]

    orientation = robot_node.getOrientation()
    fx, fy, fz = orientation[2], orientation[5], orientation[8]

    if key == Keyboard.UP:
        vx, vy, vz = fx * drive_speed, fy * drive_speed, fz * drive_speed
    elif key == Keyboard.DOWN:
        vx, vy, vz = -fx * drive_speed, -fy * drive_speed, -fz * drive_speed
    elif key == Keyboard.LEFT:
        wy = turn_speed
    elif key == Keyboard.RIGHT:
        wy = -turn_speed

    return [vx, vy, vz, wx, wy, wz]

# Handle photo saving ('C') and manual telemetry printing ('P') without duplicate triggers
def handle_user_actions(key, camera, optical, pressure, gyro, folder, image_number, key_delay):
    # Decrement delay timer first
    if key_delay > 0:
        return image_number, key_delay - 1

    # Check key inputs only when cooldown delay has reached 0
    if key in (ord('C'), ord('c')):
        image_number += 1
        filename = f"{folder}/medical_review_{image_number}.jpg"
        if camera:
            camera.saveImage(filename, 100)
            print("Image Saved:", filename)
            print("Optical:", optical, "Pressure:", pressure)
        return image_number, 20  # Set cooldown buffer (20 timesteps)

    elif key in (ord('P'), ord('p')):
        print("Optical :", optical)
        print("Pressure:", pressure)
        print("Gyro Y  :", gyro[1])
        return image_number, 15  # Set cooldown buffer (15 timesteps)

    return image_number, 0

def setup_sensors_and_camera(robot, timestep):
    camera = setup_camera(robot, timestep)
    optical, pressure, gyro = setup_sensors(robot, timestep)
    return camera, optical, pressure, gyro

def main():
    robot = Supervisor()
    timestep = int(robot.getBasicTimeStep())

    keyboard = Keyboard()
    keyboard.enable(timestep)

    robot_node = robot.getSelf()
    camera, optical_sensor, pressure_sensor, gyro_sensor = setup_sensors_and_camera(robot, timestep)

    folder = "captured_images"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Motion & threshold limits
    DRIVE_SPEED = 0.03
    TURN_SPEED = 0.38
    OPTICAL_LIMIT = 0.05
    PRESSURE_LIMIT = 0.5

    image_number = 0
    key_delay = 0
    alert_delay = 0

    print("Arrow Keys = Move | C = Capture Image | P = Print Sensor Values")

    while robot.step(timestep) != -1:
        key = keyboard.getKey()

        # Read current telemetry
        optical = optical_sensor.getValue() if optical_sensor else 0
        pressure = pressure_sensor.getValue() if pressure_sensor else 0
        gyro = gyro_sensor.getValues() if gyro_sensor else [0, 0, 0]

        # Execute detection, key actions, and driving
        alert_delay = check_abnormalities(optical, pressure, OPTICAL_LIMIT, PRESSURE_LIMIT, alert_delay)
        image_number, key_delay = handle_user_actions(key, camera, optical, pressure, gyro, folder, image_number, key_delay)
        velocity = get_movement_velocity(key, robot_node, DRIVE_SPEED, TURN_SPEED)
        
        robot_node.setVelocity(velocity)

if __name__ == "__main__":
    main()