# checking if you have nvidia
if nvidia-smi | grep -q "Driver" 2>/dev/null; then
  echo "******************************"
  echo """It looks like you have nvidia drivers running. Please make sure your nvidia-docker is setup by following the instructions linked in the README and then run build_container_cuda.sh instead."""
  echo "******************************"
  while true; do
    read -p "Do you still wish to continue?" yn
    case $yn in
      [Yy]* ) make install; break;;
      [Nn]* ) exit;;
      * ) echo "Please answer yes or no.";;
    esac
  done
fi

# UI permisions
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

xhost +local:docker
docker pull jahaniam/orbslam3:ubuntu20_noetic_cpu

# Remove existing container
docker rm -f orbslam3 &>/dev/null
[ -d "ORB_SLAM3" ] && sudo rm -rf ORB_SLAM3 && mkdir ~/Packages/ORB_SLAM3

# Create a new container
docker run -td  --net=host --ipc=host \
    --name="orbslam3" \
    --memory=8g \
    -e "DISPLAY=$DISPLAY" \
    -e "QT_X11_NO_MITSHM=1" \
    -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    -e "XAUTHORITY=$XAUTH" \
    -e ROS_IP=127.0.0.1 \
    -v `pwd`/Datasets:/Datasets \
    -v /etc/group:/etc/group:ro \
    -v `pwd`/ORB_SLAM3:/root/Packages/ORB_SLAM3 \
    -v `pwd`/scripts:/root/scripts \
    jahaniam/orbslam3:ubuntu20_noetic_cpu bash
    
# Git pull orbslam and compile
docker exec -it orbslam3 bash -i -c  "git clone -b add_euroc_example.sh https://github.com/jahaniam/ORB_SLAM3.git ~/Packages/ORB_SLAM3 && cd ~/Packages/ORB_SLAM3 && chmod +x build.sh && ./build.sh "
# Compile ORBSLAM3-ROS
docker exec -it orbslam3 bash -i -c "echo 'ROS_PACKAGE_PATH=/opt/ros/noetic/share:~/Packages/ORB_SLAM3/Examples/ROS'>>~/.bashrc && source ~/.bashrc && cd ~/Packages/ORB_SLAM3 && chmod +x build_ros.sh && ./build_ros.sh"
docker exec -it orbslam3 bash -i -c "apt-get update && apt-get install -y python3-catkin-tools ros-noetic-camera-calibration && rm -rf /var/lib/apt/lists/* "
# Git pull orbslam ros wrapper
docker exec -it orbslam3 bash -i -c "git clone https://github.com/DanSimons/orb_slam3_ros_wrapper.git ~/catkin_ws/src/ && cd ~/catkin_ws && catkin build -j1 -p1 && cp ~/Packages/ORB_SLAM3/Vocabulary/ORBvoc.txt /root/catkin_ws/src/config/ && echo 'source /root/catkin_ws/devel/setup.bash' >> ~/.bashrc"
