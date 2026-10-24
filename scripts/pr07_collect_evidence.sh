#!/usr/bin/env bash
# Сбор evidence ПР07. Запускать из корня репозитория после:
#   sudo apt install ros-lyrical-ackermann-msgs ros-lyrical-ros-gz
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-up-to course_simulation
source install/setup.bash
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-16}"
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export GZ_SIM_RESOURCE_PATH="$ROOT/src/course_simulation/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"

mkdir -p evidence/pr07 fixtures
rm -rf fixtures/pr07-sensors

# stop leftovers
pkill -f 'gz sim' 2>/dev/null || true
pkill -f gz-sim-server 2>/dev/null || true
sleep 1

ros2 launch course_simulation simulation.launch.py \
  world:="$ROOT/src/course_simulation/worlds/mcity-minimal.sdf" \
  bridge_config:="$ROOT/src/course_simulation/config/bridge.yaml" \
  headless:=true publish_cmd:=true \
  2>&1 | tee evidence/pr07/headless.txt &
LAUNCH_PID=$!
sleep 15

{
  echo '## clock'
  ros2 topic echo /clock --once || true
  echo '## topic hz /vehicle/scan (5s)'
  timeout 5 ros2 topic hz /vehicle/scan || true
  echo '## topic hz /vehicle/imu'
  timeout 3 ros2 topic hz /vehicle/imu || true
  echo '## odom once'
  timeout 3 ros2 topic echo /vehicle/odom --once || true
  echo '## gz_cmd_vel once'
  timeout 3 ros2 topic echo /vehicle/gz_cmd_vel --once || true
} | tee evidence/pr07/live-checks.txt

# sensors.json scaffold filled from live echo
python3 - <<'PY'
import json, subprocess, time
from pathlib import Path

def hz(topic, seconds=4):
    try:
        out = subprocess.check_output(
            f'timeout {seconds} ros2 topic hz {topic}',
            shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        out = e.output or ''
    for line in out.splitlines():
        if 'average rate' in line:
            return float(line.split(':')[1].strip())
    return None

def once(topic):
    try:
        return subprocess.check_output(
            f'timeout 3 ros2 topic echo {topic} --once',
            shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output or ''

sensors = []
specs = [
    ('/vehicle/camera/image_raw', 'sensor_msgs/msg/Image', 'camera_link', 20),
    ('/vehicle/scan', 'sensor_msgs/msg/LaserScan', 'lidar_link', 5),
    ('/vehicle/imu', 'sensor_msgs/msg/Imu', 'imu_link', 100),
    ('/vehicle/odom', 'nav_msgs/msg/Odometry', 'odom', 50),
]
for topic, typ, frame, claimed in specs:
    sample = once(topic)
    measured = hz(topic, 4)
    sensors.append({
        'topic': topic,
        'type': typ,
        'frame_id': frame,
        'time_source': 'sim_time (/clock)',
        'claimed_hz': claimed,
        'measured_hz': measured,
        'note': 'lidar update_rate changed 10→5 in model.sdf',
        'sample_preview': sample[:400],
    })
# raw gz frames
odom_gz = once('/vehicle/odom_gz')
Path('evidence/pr07/sensors.json').write_text(json.dumps({
    'sensors': sensors,
    'odom_gz_frames': {
        'header.frame_id': 'course_ackermann/odom',
        'child_frame_id': 'course_ackermann/base_link',
        'sample_preview': odom_gz[:400],
    },
    'lidar_param_change': 'update_rate 10 → 5 Hz in model.sdf',
}, ensure_ascii=False, indent=2) + '\n')
print('wrote sensors.json')
PY

# bag ≥ 30 s sim time
timeout --preserve-status --signal=INT --kill-after=5s 50s \
  ros2 bag record --storage mcap --use-sim-time -o fixtures/pr07-sensors \
  --topics /vehicle/camera/image_raw /vehicle/scan /vehicle/imu /vehicle/odom \
  /tf /tf_static /clock || true

ros2 bag info fixtures/pr07-sensors | tee evidence/pr07/bag-info.txt

# defect: broken bridge IMU direction
kill "$LAUNCH_PID" 2>/dev/null || true
sleep 2
pkill -f 'gz sim' 2>/dev/null || true
pkill -f gz-sim-server 2>/dev/null || true
sleep 2

ros2 launch course_simulation simulation.launch.py \
  bridge_config:="$ROOT/src/course_simulation/config/bridge-broken.yaml" \
  headless:=true publish_cmd:=false \
  > /tmp/pr07_broken.log 2>&1 &
BROKEN_PID=$!
sleep 12
{
  echo '## DEFECT: IMU direction ROS_TO_GZ in bridge-broken.yaml'
  echo '## ros2 topic info -v /vehicle/imu'
  ros2 topic info -v /vehicle/imu || true
  echo '## echo --once (expect timeout / no data)'
  timeout 3 ros2 topic echo /vehicle/imu --once || true
  echo "echo_exit=$?"
  echo '## gz topic -i /vehicle/imu'
  gz topic -i -t /vehicle/imu || true
} | tee evidence/pr07/defect-imu.txt
kill "$BROKEN_PID" 2>/dev/null || true
pkill -f 'gz sim' 2>/dev/null || true
pkill -f gz-sim-server 2>/dev/null || true

echo 'DONE. Fill report.json commit SHA after impl commit, then check_practice.'
