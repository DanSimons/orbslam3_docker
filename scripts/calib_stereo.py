import glob
import sys

import cv2
import numpy as np
import yaml

# https://www.youtube.com/watch?v=yKypaVl6qQo
# https://github.com/niconielsen32/ComputerVision/blob/master/stereoVisionCalibration/stereovision_calibration.py

if len(sys.argv) != 4:
    print("format calib_stereo.py left_dir right_dir output_dir")
    exit()

chessboardSize = (8,6)
frameSize = (640,480)
squareSize = 18

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)

objp = objp * 18

objpoints = []
imgpointsL = []
imgpointsR = []

path_left = sys.argv[1] + '/*.png'
path_right = sys.argv[2] + '/*.png'
imagesLeft = glob.glob(path_left)
imagesRight = glob.glob(path_right)



# load images and find chessboard

imgL = np.zeros((1,1))
grayL = np.zeros((1,1))
imgR = np.zeros((1,1))
grayR = np.zeros((1,1))

for imgLeft, imgRight in zip(imagesLeft, imagesRight):

    imgL = cv2.imread(imgLeft)
    imgR = cv2.imread(imgRight)
    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    retL, cornersL = cv2.findChessboardCorners(grayL, chessboardSize, None)
    retR, cornersR = cv2.findChessboardCorners(grayR, chessboardSize, None)

    if retL and retR:
        objpoints.append(objp)

        cornersL = cv2.cornerSubPix(grayL, cornersL, (11,11), (-1,-1), criteria)
        imgpointsL.append(cornersL)

        cornersR = cv2.cornerSubPix(grayR, cornersR, (11,11), (-1,-1), criteria)
        imgpointsR.append(cornersR)

        cv2.drawChessboardCorners(imgL, chessboardSize, cornersL, retL)
        cv2.imshow('img left', imgL)
        cv2.drawChessboardCorners(imgR, chessboardSize, cornersR, retR)
        cv2.imshow('img right', imgR)
        cv2.waitKey(1)



cv2.destroyAllWindows()

## mono calibration

print('calibrating mono cameras')
cameraMatrixL = np.zeros((3,3))
distL = np.zeros((1,5))
retL, cameraMatrixL, distL, rvecsL, tvecsL = cv2.calibrateCamera(objpoints, imgpointsL, frameSize, cameraMatrixL, distL)
heightL, widthL, channelsL = imgL.shape
newCameraMatrixL, roi_L = cv2.getOptimalNewCameraMatrix(cameraMatrixL, distL, (widthL, heightL), 1, (widthL, heightL))

cameraMatrixR = np.zeros((3,3))
distR = np.zeros((1,5))
retR, cameraMatrixR, distR, rvecsR, tvecsR = cv2.calibrateCamera(objpoints, imgpointsR, frameSize, cameraMatrixR, distR)
heightR, widthR, channelsR = imgR.shape
newCameraMatrixR, roi_R = cv2.getOptimalNewCameraMatrix(cameraMatrixR, distR, (widthR, heightR), 1, (widthR, heightR))

## stereo calib
print("calibrating stereo")

flags = 0
flags |= cv2.CALIB_FIX_INTRINSIC

criteria_stereo = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)

retStereo, newCameraMatrixL, distL, newCameraMatrixR, distR, rot, trans, essentialMatrix, fundamentalMatrix = cv2.stereoCalibrate(objpoints, imgpointsL, imgpointsR, newCameraMatrixL, distL, newCameraMatrixR, distR, grayL.shape[::-1], None, None, None, None, flags, criteria_stereo,)



# stereo recti
print("rectifying")

rectifyScale = 1
rectL, rectR, projMatrixL, projMatrixR, Q, roiL, roiR = cv2.stereoRectify(newCameraMatrixL, distL, newCameraMatrixR, distR, grayL.shape[::-1], rot, trans, None, None, None, None, None, flags, rectifyScale, (0,0))

stereoMapL = cv2.initUndistortRectifyMap(newCameraMatrixL, distL, rectL, projMatrixL, grayL.shape[::-1], cv2.CV_16SC2)
stereoMapR = cv2.initUndistortRectifyMap(newCameraMatrixR, distR, rectR, projMatrixR, grayR.shape[::-1], cv2.CV_16SC2)

# save params
print("Saving params")
T = np.eye(4)
print(rot, trans)
T[:3, :3] = rot
T[:3, 3] = trans.T
print(T.flatten().tolist())


class OpenCVMatrix:
    def __init__(self, rows, cols, dt, data):
        self.rows = rows
        self.cols = cols
        self.dt = dt
        self.data = data


def opencv_matrix_representer(dumper, obj):
    return dumper.represent_mapping(
        "!!opencv-matrix",
        {"rows": obj.rows, "cols": obj.cols, "dt": obj.dt, "data": obj.data}
    )

yaml.add_representer(OpenCVMatrix, opencv_matrix_representer)

data = {
    "File.version": "1.0",
    "Camera.type": '"PinHole"',
    "Camera1.fx": float(cameraMatrixL[0][0]),
    "Camera1.fy": float(cameraMatrixL[0][2]),
    "Camera1.cx": float(cameraMatrixL[1][1]),
    "Camera1.cy": float(cameraMatrixL[1][2]),
    "Camera1.k1": float(distL[0][0]),
    "Camera1.k2": float(distL[0][1]),
    "Camera1.p1": float(distL[0][2]),
    "Camera1.p2": float(distL[0][3]),
    "Camera1.k3": float(distL[0][4]),
    "Camera2.fx": float(cameraMatrixR[0][0]),
    "Camera2.fy": float(cameraMatrixR[0][2]),
    "Camera2.cx": float(cameraMatrixR[1][1]),
    "Camera2.cy": float(cameraMatrixR[1][2]),
    "Camera2.k1": float(distR[0][0]),
    "Camera2.k2": float(distR[0][1]),
    "Camera2.p1": float(distR[0][2]),
    "Camera2.p2": float(distR[0][3]),
    "Camera2.k3": float(distR[0][4]),
    "Camera.width": widthL,
    "Camera.hight": heightL,
    "Camera.fps": 30,
    "Camera.RGB": 1,
    "Stereo.ThDepth": 40.0,
    "Stereo.b": 0.07732,
    "Stereo.ThDepth": 60.0,
    "Stereo.T_c1_c2": OpenCVMatrix(
        rows = 4,
        cols = 4,
        dt = 'f',
        data = T.flatten().tolist()
    ),
    "ORBextractor.nFeatures": 1200,
    "ORBextractor.scaleFactor": 1.2, # for scale pyramid
    "ORBextractor.nLevels": 8,
    "ORBextractor.iniThFAST": 20, # FAST initial 
    "ORBextractor.minThFAST": 7, # if no corners are detected try this
    "Viewer.KeyFrameSize": 0.05,
    "Viewer.KeyFrameLineWidth": 1.0,
    "Viewer.GraphLineWidth": 0.9,
    "Viewer.PointSize": 2.0,
    "Viewer.CameraSize": 0.08,
    "Viewer.CameraLineWidth": 3.0,
    "Viewer.ViewpointX": 0.0,
    "Viewer.ViewpointY": -0.7,
    "Viewer.ViewpointZ": -1.8,
    "Viewer.ViewpointF": 500.0,
    "Viewer.imageViewScale": 1.0,
}

# file = cv2.FileStorage(sys.argv[3], cv2.FILE_STORAGE_WRITE)
# file.write("Stereo.T_c1_c2", T)
# file.release()

with open(sys.argv[3], 'w', encoding='utf-8') as f:
    yaml.dump(data, f)
