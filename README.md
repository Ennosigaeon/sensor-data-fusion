# sensor-data-fusion

## Requirements
- Packages
    - sudo apt install swig build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
- Python 2.7.x
- opencv 3.1.x (https://github.com/Itseez/opencv/archive/3.1.0.zip)
    To compile the project download the sources and run
    - mkdir build
    - cd build
    - cmake ..
    - make -j4
    - sudo make install
- aruco-2.0.10 (http://www.uco.es/investiga/grupos/ava/node/26)
    To compile the project download the sources and run
    - mkdir build
    - cd build
    - cmake ..
    - make -j4
    - sudo make install
- python-aruco (https://github.com/fehlfarbe/python-aruco)
    - ./swigbuild.sh
    - sudo python setup.py install