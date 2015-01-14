#!/bin/sh

if [ "$#" -ne 2 ]; then
    echo "Usage:"
    echo "verilate-system.sh <verilog_module> <target_dir>"
    exit
fi

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

echo "Converting Verilog module $1 into SystemC at $2..."

WORK_DIR="/tmp/verilog-to-sc"
MODULE_NAME=$1
TARGET_DIR=$(get_abs_filename $2)
VERILATOR_DIR="/usr/share/verilator/include"
SRC_DIR=$(pwd)

cd $SRC_DIR
mkdir -p $WORK_DIR
mkdir -p $TARGET_DIR
sbt "run --targetDir $WORK_DIR --backend v"
cd $WORK_DIR
verilator --sc $MODULE_NAME.v +define+SYNTHESIS+1 -Wno-lint
cp -f obj_dir/*.cpp $TARGET_DIR/
cp -f obj_dir/*.h $TARGET_DIR/
cp -f $VERILATOR_DIR/verilated.cpp $TARGET_DIR

cd $SRC_DIR
rm -rf $WORK_DIR


