#!/usr/bin/env sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:$LOCALLIB:/usr/lib:/usr/lib/x86_64-linux-gnu:/work/cv2/imagelibs/lib:/u/hanselmann/lib:/u/dreuw/lib_x86_64:/u/hanselmann/lib64/lib:/usr/local/cuda-6.0/lib64


GLOG_logtostderr=1 /work/cv2/forster/software/caffe/build/tools/caffe train --solver=/u/haiwang/projects/Task3/caffenet_solver_softmax.prototxt -weights /work/cv2/forster/software/caffe/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel

