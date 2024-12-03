import yaml
import sys

if len(sys.argv) < 3:
    print("err: bad params")
    exit()
elif len(sys.argv) == 3:
    with open(sys.argv[1]) as f_in:
        old_data = yaml.safe_load(f_in)
        print(old_data)
        new_data = {
            "File.version": "1.0",
            "Camera.type": "pinhole",
            "Camera1.fx": old_data["camera_matrix"]["data"][0],
            "Camera1.fy": old_data["camera_matrix"]["data"][4],
            "Camera1.cx": old_data["camera_matrix"]["data"][2],
            "Camera1.cy": old_data["camera_matrix"]["data"][5],
            "Camera1.k1": old_data["distortion_coefficients"]["data"][0],
            "Camera1.k2": old_data["distortion_coefficients"]["data"][1],
            "Camera1.p1": old_data["distortion_coefficients"]["data"][2],
            "Camera1.p2": old_data["distortion_coefficients"]["data"][3],
            "Camera1.k3": old_data["distortion_coefficients"]["data"][4],
            "Camera.width": old_data["image_width"],
            "Camera.height": old_data["image_height"],
            "Camera.fps": 30,
            "Camera.RGB": 1,
            "Stereo.ThDepth": 40.0,
            "Stereo.b": 0.07732,
        }
        with open(sys.argv[2], 'w') as f_out:
            yaml.dump(new_data, f_out)
else:
    new_data = {}
    new_data['File.version'] = "1.0"
    new_data['Camera.type'] = "pinhole"
    for filename, i in zip(sys.argv[1:-1], range(1, len(sys.argv)-1)):
        with open(filename, 'r') as f_in:
            old_data = yaml.safe_load(f_in)
            new_data[f"Camera{i}.fx"] = old_data["camera_matrix"]["data"][0],
            new_data[f"Camera{i}.fy"] = old_data["camera_matrix"]["data"][4],
            new_data[f"Camera{i}.cx"] = old_data["camera_matrix"]["data"][2],
            new_data[f"Camera{i}.cy"] = old_data["camera_matrix"]["data"][5],
            new_data[f"Camera{i}.k1"] = 0,
            new_data[f"Camera{i}.k2"] = 0,
            new_data[f"Camera{i}.k3"] = 0,
            new_data[f"Camera{i}.p1"] = 0,
            new_data[f"Camera{i}.p2"] = 0,
