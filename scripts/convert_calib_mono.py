import sys

import cv2
import yaml

if len(sys.argv) != 4:
    print("err: bad params")
    exit()
else:
    print(f"converting: {sys.argv[1]} and {sys.argv[2]} , saving to: {sys.argv[3]}")
    left_in = open(sys.argv[1])
    right_in = open(sys.argv[2])
    left_data = yaml.safe_load(left_in)
    right_data = yaml.safe_load(right_in)


    # calib stereo
    cv2.stereoCalibrateExtended()


    # make new yaml
    new_data = {
        "File.version": "1.0",
        "Camera.type": "pinhole",
        "Camera1.fx": left_data["camera_matrix"]["data"][0],
        "Camera1.fy": left_data["camera_matrix"]["data"][4],
        "Camera1.cx": left_data["camera_matrix"]["data"][2],
        "Camera1.cy": left_data["camera_matrix"]["data"][5],
        "Camera1.k1": left_data["distortion_coefficients"][0],
        "Camera1.k2": left_data["distortion_coefficients"][1],
        "Camera1.p1":  left_data["distortion_coefficients"][2],
        "Camera1.p2":  left_data["distortion_coefficients"][3],
        "Camera1.k3":  left_data["distortion_coefficients"][4],
        "Camera2.fx": right_data["camera_matrix"]["data"][0],
        "Camera2.fy": right_data["camera_matrix"]["data"][4],
        "Camera2.cx": right_data["camera_matrix"]["data"][2],
        "Camera2.cy": right_data["camera_matrix"]["data"][5],
        "Camera2.k1": right_data["distortion_coefficients"][0],
        "Camera2.k2": right_data["distortion_coefficients"][1],
        "Camera2.p1":  right_data["distortion_coefficients"][2],
        "Camera2.p2":  right_data["distortion_coefficients"][3],
        "Camera2.k3":  right_data["distortion_coefficients"][4],
        "Camera.width": right_data["image_width"],
        "Camera.height": right_data["image_height"],
        "Camera.fps": 30,
        "Camera.RGB": 1,
        "Stereo.ThDepth": 40.0,
        "Stereo.b": 0.07732,
    }
        with open(sys.argv[2], 'w') as f_out:
            yaml.dump(new_data, f_out)
