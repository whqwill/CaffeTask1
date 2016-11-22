#!/usr/bin/env sh

source /u/standard/settings/sge_settings.sh
export PATH=${HOME}/bin:${PATH}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:$LOCALLIB:/usr/lib:/usr/lib/x86_64-linux-gnu:/work/cv2/imagelibs/lib:/u/hanselmann/lib:/u/dreuw/lib_x86_64:/u/hanselmann/lib64/lib:/usr/local/cuda-6.0/lib64

TOOLS=/work/cv2/forster/software/caffe/build/tools

TRAIN=normalization/
TEST=normalization/

TRAIN_DATA_ROOT=/work/cv2/haiwang/data/CUB200-2011/images/$TRAIN
TEST_DATA_ROOT=/work/cv2/haiwang/data/CUB200-2011/images/$TEST

RESIZE_HEIGHT=256
RESIZE_WIDTH=256

echo "Creating train leveldb..."

GLOG_logtostderr=1 $TOOLS/convert_imageset \
    --backend="leveldb" \
    --resize_height=$RESIZE_HEIGHT \
    --resize_width=$RESIZE_WIDTH \
    --shuffle=true \
    $TRAIN_DATA_ROOT \
    /u/haiwang/projects/Task3/cub200-2011.train.imageList.txt \
    /work/cv2/haiwang/data/Task3/train_leveldb_prototype

echo "Creating mean file of train leveldb..."
GLOG_logtostderr=1 $TOOLS/compute_image_mean \
    /work/cv2/haiwang/data/Task3/train_leveldb_prototype \
    /work/cv2/haiwang/data/Task3/train_leveldb_prototype_mean.binaryproto \
    leveldb

echo "Creating test leveldb..."

GLOG_logtostderr=1 $TOOLS/convert_imageset \
    --backend="leveldb" \
    --resize_height=$RESIZE_HEIGHT \
    --resize_width=$RESIZE_WIDTH \
    --shuffle=true \
    $TEST_DATA_ROOT \
    /u/haiwang/projects/Task3/cub200-2011.test.imageList.txt \
    /work/cv2/haiwang/data/Task3/test_leveldb_prototype

echo "Creating mean file of test leveldb..."
GLOG_logtostderr=1 $TOOLS/compute_image_mean \
    /work/cv2/haiwang/data/Task3/test_leveldb_prototype \
    /work/cv2/haiwang/data/Task3/test_leveldb_prototype_mean.binaryproto \
    leveldb



echo "Done."

