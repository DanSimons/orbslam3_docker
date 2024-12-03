# docker exec -it orbslam3 bash -c "ls /root/catkin_ws/src/config/myStereoCam/left"
docker exec -it orbslam3 bash -c "python3 /root/scripts/calib_stereo.py /root/catkin_ws/src/config/myStereoCam/left /root/catkin_ws/src/config/myStereoCam/right /root/catkin_ws/src/config/myStereoCam/params.yaml"
docker exec -it orbslam3 bash -c "cat /root/catkin_ws/src/config/myStereoCam/params.yaml"
