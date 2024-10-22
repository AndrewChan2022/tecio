import time
import numpy as np
import struct
import argparse

def load_raw_to_np(file, d, h, w, dtype = np.uint8):
    element_count = w * h * d
    size = element_count * np.dtype(dtype).itemsize
    data_array = np.fromfile(file, dtype, element_count)
    data_array = data_array.reshape((d, h, w))
    print(f'load data shape: {data_array.shape}')
    return data_array

# 70.6ms
def write_np_to_raw(file, data, factor, dtype=np.uint8):
    d, h, w = data.shape
    newfile=open(file,'wb')
    for z in range(0, d, factor):
        for y in range(0, h, factor):
            for x in range(0, w, factor):
                if dtype == np.uint8:
                    binary_data = struct.pack("B", data[z, y, x])
                elif dtype == np.uint32:
                    binary_data = struct.pack("I", data[z, y, x])
                elif dtype == np.uint32:
                    binary_data = struct.pack("f", data[z, y, x])
                else:
                    print("unkown dtype")
                    assert(False)
                newfile.write(binary_data)

# 35.2ms
def write_np_to_raw_fast(file, data, factor, dtype=np.uint8):
    d, h, w = data.shape
    newarray = []
    for z in range(0, d, factor):
        for y in range(0, h, factor):
            for x in range(0, w, factor):
                newarray.append(data[z, y, x])
    with open(file,'wb') as f:
        byteArray = bytearray(newarray)
        f.write(byteArray)


# 0.9ms
def write_np_to_raw_fast2(file, data, factor, dtype=np.uint8):
    d, h, w = data.shape
    newarray = data[::factor, ::factor, ::factor]
    with open(file,'wb') as f:
        byteArray = bytearray(newarray)
        f.write(byteArray)

def main(file, out, d, h, w, factor, dtype = np.uint8):
    # a = load_raw_to_np("D:/data/dataset/scivis/foot_256x256x256_uint8.raw", 256, 256, 256)
    # print(a[:1000])
    values = load_raw_to_np(file, d, h, w, dtype)
    tic = time.time()
    write_np_to_raw_fast2(out, values, factor, dtype)
    toc = time.time()
    print(f'Time:{(toc-tic)*1000} ms')
    # print(values[:100][:100])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument('file', nargs='?')  # position args
    parser.add_argument('-o', '--out', type=str, required=True, help="out file name")
    parser.add_argument('-w', '--width', type=int, default=256, help="width")
    parser.add_argument('-h', '--height', type=int, default=256, help="height")
    parser.add_argument('-d', '--depth', type=int, default=256, help="depth")
    parser.add_argument('-t', '--type', type=str, default="byte", help="data type, byte, float")
    parser.add_argument('-f', '--factor', type=int, default=4, help="downsample factor")
    args = parser.parse_args()
    
    main(args.file, args.out, args.depth, args.height, args.width, args.factor,  np.uint8 if args.type=="byte" else np.float32)


    # py .\rawdownsample.py D:/data/dataset/scivis/foot_256x256x256_uint8.raw -o  D:/data/dataset/scivis/foot_64x64x64_uint8.raw

