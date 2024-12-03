# https://github.com/osrf/docker_images/blob/df19ab7d5993d3b78a908362cdcd1479a8e78b35/ros/noetic/ubuntu/focal/ros-base/Dockerfile
# This is an auto generated Dockerfile for ros:ros-base
# generated from docker_images/create_ros_image.Dockerfile.em
FROM ros:noetic

RUN apt-get update && apt-get install -y \
    ros-noetic-demo-nodes-cpp \
    ros-noetic-demo-nodes-py && \
    rm -rf /var/apt/lists/*


