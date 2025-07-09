import can
import time

# Initialize CAN bus (virtual for testing)
bus = can.Bus(channel='vcan0', interface='socketcan')

def encode_frame(obj_id, dist_long, dist_lat, vel_long, vel_lat, obj_class, dyn_prop, rcs):
    frame = [0] * 8

    # Encode object ID
    frame[0] = obj_id & 0xFF

    # Encode distance longitudinal (depth)
    dist_long_raw = int((dist_long + 500) / 0.2)
    dist_long_raw = max(0, min(dist_long_raw, 0x1FFF))  # 13 bits
    frame[1] = (dist_long_raw >> 5) & 0xFF
    frame[2] = ((dist_long_raw & 0x1F) << 3)

    # Encode distance lateral (camera X coordinate)
    dist_lat_raw = int((dist_lat + 204.6) / 0.2)
    dist_lat_raw = max(0, min(dist_lat_raw, 0x7FF))  # 11 bits
    frame[2] |= (dist_lat_raw >> 8) & 0x07
    frame[3] = dist_lat_raw & 0xFF

    # Encode velocity longitudinal (depth direction)
    vel_long_raw = int((vel_long + 128.0) / 0.25)
    vel_long_raw = max(0, min(vel_long_raw, 0x3FFF))  # 14 bits
    frame[4] = (vel_long_raw >> 6) & 0xFF
    frame[5] = ((vel_long_raw & 0x3F) << 2) & 0xFC

    # Encode velocity lateral (camera X direction)
    vel_lat_raw = int((vel_lat + 64.0) / 0.25)
    vel_lat_raw = max(0, min(vel_lat_raw, 0x7FF))  # 11 bits
    frame[5] |= (vel_lat_raw >> 8) & 0x03
    frame[6] = ((vel_lat_raw & 0xFF) << 5) & 0xE0

    # Object class and dynamic property
    frame[6] |= ((obj_class & 0x03) << 3)
    frame[6] |= (dyn_prop & 0x07)

    # Encode RCS
    rcs_raw = int((rcs + 64.0) / 0.5)
    rcs_raw = max(0, min(rcs_raw, 0xFF))
    frame[7] = rcs_raw

    return [b & 0xFF for b in frame]

# Provided face detection data
face_data = [
 {'cam_coord': 0.01, 'depth': 2.93, 'ID': 1, 'timestamp': 7.618},
 {'cam_coord': 0.38, 'depth': 2.93, 'ID': 1, 'timestamp': 9.587},
 {'cam_coord': 0.5, 'depth': 3.1, 'ID': 1, 'timestamp': 9.703},
 {'cam_coord': 0.57, 'depth': 2.88, 'ID': 1, 'timestamp': 9.82},
 {'cam_coord': 0.91, 'depth': 2.88, 'ID': 1, 'timestamp': 10.392},
 {'cam_coord': 1.05, 'depth': 3.05, 'ID': 1, 'timestamp': 10.508},
 {'cam_coord': 1.02, 'depth': 2.93, 'ID': 1, 'timestamp': 10.624},
 {'cam_coord': 1.04, 'depth': 3.02, 'ID': 1, 'timestamp': 10.741},
 {'cam_coord': 1.01, 'depth': 3.01, 'ID': 1, 'timestamp': 10.857},
 {'cam_coord': 0.96, 'depth': 2.95, 'ID': 1, 'timestamp': 11.201},
 {'cam_coord': 0.96, 'depth': 2.99, 'ID': 1, 'timestamp': 11.318},
 {'cam_coord': 0.97, 'depth': 3.04, 'ID': 1, 'timestamp': 11.434},
 {'cam_coord': 0.95, 'depth': 3.04, 'ID': 1, 'timestamp': 11.55},
 {'cam_coord': 0.92, 'depth': 2.98, 'ID': 1, 'timestamp': 11.666},
 {'cam_coord': 0.95, 'depth': 3.05, 'ID': 1, 'timestamp': 11.782},
 {'cam_coord': 0.95, 'depth': 3.04, 'ID': 1, 'timestamp': 11.899},
 {'cam_coord': 0.95, 'depth': 2.98, 'ID': 1, 'timestamp': 12.015},
 {'cam_coord': 0.97, 'depth': 3.01, 'ID': 1, 'timestamp': 12.131},
 {'cam_coord': 0.95, 'depth': 2.98, 'ID': 1, 'timestamp': 12.247},
 {'cam_coord': 0.32, 'depth': 3.33, 'ID': 1, 'timestamp': 12.364},
 {'cam_coord': 0.94, 'depth': 2.99, 'ID': 2, 'timestamp': 12.363},
 {'cam_coord': 0.33, 'depth': 3.29, 'ID': 1, 'timestamp': 12.48},
 {'cam_coord': 0.87, 'depth': 2.92, 'ID': 2, 'timestamp': 12.48},
 {'cam_coord': 0.31, 'depth': 3.07, 'ID': 1, 'timestamp': 12.596},
 {'cam_coord': 0.34, 'depth': 3.19, 'ID': 1, 'timestamp': 12.713},
 {'cam_coord': 0.29, 'depth': 2.96, 'ID': 1, 'timestamp': 12.829},
 {'cam_coord': 0.91, 'depth': 2.52, 'ID': 2, 'timestamp': 12.829},
 {'cam_coord': 0.5, 'depth': 2.08, 'ID': 1, 'timestamp': 13.059},
 {'cam_coord': 0.54, 'depth': 2.45, 'ID': 1, 'timestamp': 13.175},
 {'cam_coord': 0.59, 'depth': 2.63, 'ID': 2, 'timestamp': 13.291},
 {'cam_coord': 0.61, 'depth': 2.64, 'ID': 1, 'timestamp': 13.524},
 {'cam_coord': 0.94, 'depth': 2.53, 'ID': 1, 'timestamp': 14.105},
 {'cam_coord': 1.0, 'depth': 2.85, 'ID': 2, 'timestamp': 14.222},
 {'cam_coord': 0.81, 'depth': 2.93, 'ID': 2, 'timestamp': 14.339},
 {'cam_coord': 0.9, 'depth': 3.15, 'ID': 2, 'timestamp': 14.455},
 {'cam_coord': 1.12, 'depth': 3.53, 'ID': 2, 'timestamp': 14.572},
 {'cam_coord': 0.95, 'depth': 3.49, 'ID': 2, 'timestamp': 15.853},
 {'cam_coord': 1.04, 'depth': 3.37, 'ID': 2, 'timestamp': 15.97},
 {'cam_coord': 0.94, 'depth': 3.15, 'ID': 2, 'timestamp': 16.087},
 {'cam_coord': 0.91, 'depth': 3.19, 'ID': 2, 'timestamp': 16.203},
 {'cam_coord': 0.85, 'depth': 3.15, 'ID': 2, 'timestamp': 16.32},
 {'cam_coord': 0.92, 'depth': 2.81, 'ID': 1, 'timestamp': 16.551},
 {'cam_coord': 0.12, 'depth': 3.96, 'ID': 1, 'timestamp': 16.667},
 {'cam_coord': 0.82, 'depth': 2.61, 'ID': 2, 'timestamp': 16.667},
 {'cam_coord': 0.04, 'depth': 4.33, 'ID': 1, 'timestamp': 16.898},
 {'cam_coord': 0.02, 'depth': 4.12, 'ID': 1, 'timestamp': 17.014},
 {'cam_coord': 0.0, 'depth': 3.66, 'ID': 1, 'timestamp': 17.13},
 {'cam_coord': 0.96, 'depth': 2.44, 'ID': 1, 'timestamp': 17.705},
 {'cam_coord': 0.95, 'depth': 2.48, 'ID': 1, 'timestamp': 17.821},
 {'cam_coord': 1.0, 'depth': 2.62, 'ID': 2, 'timestamp': 17.938},
 {'cam_coord': 0.94, 'depth': 2.5, 'ID': 1, 'timestamp': 18.055},
 {'cam_coord': 0.88, 'depth': 2.32, 'ID': 1, 'timestamp': 18.286},
 {'cam_coord': 0.36, 'depth': 3.9, 'ID': 1, 'timestamp': 18.402},
 {'cam_coord': 0.87, 'depth': 2.33, 'ID': 2, 'timestamp': 18.402},
 {'cam_coord': 0.34, 'depth': 3.73, 'ID': 1, 'timestamp': 18.633},
 {'cam_coord': 0.32, 'depth': 3.53, 'ID': 1, 'timestamp': 18.749},
 {'cam_coord': 0.35, 'depth': 3.85, 'ID': 1, 'timestamp': 18.867},
 {'cam_coord': 0.91, 'depth': 3.8, 'ID': 1, 'timestamp': 19.44},
 {'cam_coord': 1.22, 'depth': 2.99, 'ID': 1, 'timestamp': 20.589},
 {'cam_coord': 1.33, 'depth': 3.33, 'ID': 1, 'timestamp': 20.821},
 {'cam_coord': 0.29, 'depth': 3.24, 'ID': 1, 'timestamp': 21.392},
 {'cam_coord': 1.29, 'depth': 3.26, 'ID': 1, 'timestamp': 21.851},
 {'cam_coord': 1.24, 'depth': 3.1, 'ID': 1, 'timestamp': 21.967},
 {'cam_coord': 0.54, 'depth': 4.33, 'ID': 1, 'timestamp': 22.653},
 {'cam_coord': 1.1, 'depth': 2.62, 'ID': 1, 'timestamp': 22.769},
 {'cam_coord': 0.54, 'depth': 4.24, 'ID': 1, 'timestamp': 22.885},
 {'cam_coord': 0.55, 'depth': 4.37, 'ID': 1, 'timestamp': 23.001},
 {'cam_coord': 0.52, 'depth': 4.07, 'ID': 1, 'timestamp': 23.117},
 {'cam_coord': 0.52, 'depth': 4.09, 'ID': 1, 'timestamp': 23.233},
 {'cam_coord': 0.51, 'depth': 4.04, 'ID': 1, 'timestamp': 23.35},
 {'cam_coord': 1.02, 'depth': 2.56, 'ID': 2, 'timestamp': 23.349},
 {'cam_coord': 0.54, 'depth': 4.21, 'ID': 1, 'timestamp': 23.468},
 {'cam_coord': 0.54, 'depth': 4.3, 'ID': 1, 'timestamp': 23.584},
 {'cam_coord': 1.04, 'depth': 2.51, 'ID': 1, 'timestamp': 23.928},
 {'cam_coord': 0.86, 'depth': 4.04, 'ID': 1, 'timestamp': 24.045},
 {'cam_coord': 1.04, 'depth': 2.5, 'ID': 2, 'timestamp': 24.045},
 {'cam_coord': 0.99, 'depth': 4.04, 'ID': 1, 'timestamp': 24.389},
 {'cam_coord': 0.76, 'depth': 3.75, 'ID': 1, 'timestamp': 24.619},
 {'cam_coord': 0.65, 'depth': 3.47, 'ID': 1, 'timestamp': 24.736},
 {'cam_coord': 0.63, 'depth': 3.22, 'ID': 1, 'timestamp': 24.966},
 {'cam_coord': 0.51, 'depth': 2.95, 'ID': 1, 'timestamp': 25.083},
 {'cam_coord': 0.44, 'depth': 2.89, 'ID': 1, 'timestamp': 25.199},
 {'cam_coord': 1.29, 'depth': 2.63, 'ID': 1, 'timestamp': 25.316},
 {'cam_coord': 1.32, 'depth': 2.75, 'ID': 1, 'timestamp': 25.433},
 {'cam_coord': 0.54, 'depth': 2.32, 'ID': 1, 'timestamp': 25.891},
 {'cam_coord': 0.41, 'depth': 1.62, 'ID': 1, 'timestamp': 26.008},
 {'cam_coord': 1.4, 'depth': 2.78, 'ID': 2, 'timestamp': 26.008},
 {'cam_coord': 0.89, 'depth': 2.81, 'ID': 1, 'timestamp': 26.467},
 {'cam_coord': 0.13, 'depth': 2.83, 'ID': 1, 'timestamp': 27.27},
 {'cam_coord': 0.15, 'depth': 2.93, 'ID': 1, 'timestamp': 27.386},
 {'cam_coord': 0.16, 'depth': 2.79, 'ID': 1, 'timestamp': 27.503},
 {'cam_coord': 0.2, 'depth': 2.78, 'ID': 1, 'timestamp': 27.619},
 {'cam_coord': 0.22, 'depth': 2.67, 'ID': 1, 'timestamp': 28.079}
]
# Sort by timestamp
face_data.sort(key=lambda x: x['timestamp'])

# Calculate velocities
face_data_with_velocity = []
for i, curr in enumerate(face_data):
    if i == 0:
        vx = vz = 0.0
    else:
        prev = face_data[i - 1]
        dt = curr['timestamp'] - prev['timestamp']
        if dt == 0:
            vx = vz = 0.0
        else:
            vx = (curr['cam_coord'] - prev['cam_coord']) / dt
            vz = (curr['depth'] - prev['depth']) / dt

    face_data_with_velocity.append({
        'id': curr['ID'],
        'depth': curr['depth'],
        'cam_coord': curr['cam_coord'],
        'timestamp': curr['timestamp'],
        'vx': vx,
        'vz': vz
    })

# Send frames with velocity
while True:
    face_data_with_velocity.sort(key=lambda x: x['timestamp'])

    # Get the reference start time (wall clock)
    start_time = time.time()
    base_timestamp = face_data_with_velocity[0]['timestamp']

    for idx, face in enumerate(face_data_with_velocity, start=1):
        target_time = start_time + (face['timestamp'] - base_timestamp)
        now = time.time()
        wait_time = target_time - now
        if wait_time > 0:
            time.sleep(wait_time)

        frame = encode_frame(
            obj_id=face['id'],
            dist_long=face['depth'],
            dist_lat=face['cam_coord'],
            vel_long=face['vz'],
            vel_lat=face['vx'],
            obj_class=1,
            dyn_prop=0,
            rcs=-15
        )

        msg = can.Message(arbitration_id=0x70, data=frame, is_extended_id=False)
        try:
            bus.send(msg)
            print(f"[{face['timestamp']:.3f}s] Sent frame: ID={face['id']}, dist_long={face['depth']:.2f}m, "
                f"dist_lat={face['cam_coord']:.2f}m, vel_long={face['vz']:.2f}m/s, "
                f"vel_lat={face['vx']:.2f}m/s, frame={frame}")
        except can.CanError as e:
            print(f"CAN send failed: {e}")
