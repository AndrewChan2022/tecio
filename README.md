# tecio

## build on windows

check teciosrc/readme.txt

    1. unzip boost 
    2. mkdir build
    3. cmake-gui
        build dir: ./build
        src dir: ./teciosrc
        => config
        => then set Boost_INCLUDE_DIR
        => config again
        => then generate
    3. build with vs

## tools rawtoplt

this tool convert raw file to plt binary file.

target data type is float, tecio lib only support write float or double, new szplt lib support more data type.

datapacking is block, afterplt version 112, point is not supported any more.


source code in 

    examples/rawtoplt/rawtoplt.cpp

exe:

    tools/rawtoplt.exe


command:

    ./rawtoplt.exe -d 64 -h 64 -w 64 -t uint8 D:\data\dataset\scivis\foot_64x64x64_uint8.raw


## tools rawtotec

this tool convert raw file to plt binary file.

datapacking is block

command:

    python .\rawtotec.py -d 64 -h 64 -w 64 D:/data/dataset/scivis/foot_64x64x64_uint8.raw


## tools rawdownsample

downsample raw file


    py .\rawdownsample.py D:/data/dataset/scivis/foot_256x256x256_uint8.raw -o  D:/data/dataset/scivis/foot_64x64x64_uint8.raw

