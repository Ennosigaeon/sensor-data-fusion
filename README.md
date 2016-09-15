# sensor-data-fusion

## Requirements
- Those packages are necessary to compile all requirements
    - `sudo apt install swig build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev`
- Python 2.7.x
- opencv 3.1.x (https://github.com/Itseez/opencv/archive/3.1.0.zip)
    To compile the project download the opencv sources. Furthermore, the aruco library is needed.
    Download it from https://github.com/opencv/opencv_contrib and store the _aruco_ module in
    _opencv_contrib_.
    - `mkdir build`
    - `cd build`
    - `cmake -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib/ -DINSTALL_PYTHON_EXAMPLES=ON -DBUILD_DOCS=ON -DBUILD_EXAMPLES=ON ..`
    - `make -j4`
    - `sudo make install`
    
    If the `make` command fails with compilation exceptions try fixing
    _opencv_contrib/aruco/src/aruco.cpp_ by using this code (mind the comments).
    ```
    return calibrateCamera(processedObjectPoints, processedImagePoints,
                           imageSize, _cameraMatrix, _distCoeffs, _rvecs, _tvecs,
                           //_stdDeviationsIntrinsics,
                           //_stdDeviationsExtrinsics,
                           //_perViewErrors,
                           flags, criteria);
    ```
    The same fix may be necessary in _opencv_contrib/aruco/src/charuco.cpp_.