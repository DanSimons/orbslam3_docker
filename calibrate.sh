left=cam0
right=cam2
name=myStereoCam
calib=false
while [[ "$#" -gt 0 ]]; do
  case $1 in
	-l|--left) left=$2; shift;;
	-r|--right) right=$2; shift;;
	-n|--name) name=$2; shift;;
	-c) calib=true;;
  esac
  shift
done

if $calib; then
  docker exec -it orbslam3 bash -c "source /opt/ros/noetic/setup.bash \
  && rosrun camera_calibration cameracalibrator.py --size 8x6 --square 0.018 --approximate 0.1 left:=/$left/image_raw right:=/$right/image_raw \
  " 
fi
docker exec -it orbslam3 bash -c "source /opt/ros/noetic/setup.bash \
  && rm -rf /root/catkin_ws/src/config/$name/ \
  && mkdir -p /root/catkin_ws/src/config/$name/ \
  && cp /tmp/calibrationdata.tar.gz /root/catkin_ws/src/config/$name/ \
  && cd /root/catkin_ws/src/config/$name \
  && tar -xzf calibrationdata.tar.gz \
  && mkdir -p /root/catkin_ws/src/config/$name/left \
  && mkdir -p /root/catkin_ws/src/config/$name/right \
  && mv /root/catkin_ws/src/config/$name/left*.png /root/catkin_ws/src/config/$name/left \
  && mv /root/catkin_ws/src/config/$name/right*.png /root/catkin_ws/src/config/$name/right \
  && ls  -la
  "
