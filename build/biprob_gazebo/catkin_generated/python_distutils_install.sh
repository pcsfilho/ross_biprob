#!/bin/sh -x

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

cd "/home/paulo/ros_biprob/src/biprob_gazebo"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
/usr/bin/env \
    PYTHONPATH="/home/paulo/ros_biprob/install/lib/python2.7/dist-packages:/home/paulo/ros_biprob/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/paulo/ros_biprob/build" \
    "/usr/bin/python" \
    "/home/paulo/ros_biprob/src/biprob_gazebo/setup.py" \
    build --build-base "/home/paulo/ros_biprob/build/biprob_gazebo" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/paulo/ros_biprob/install" --install-scripts="/home/paulo/ros_biprob/install/bin"
