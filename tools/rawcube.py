import time
import numpy as np
import struct
import argparse

import numpy as np

import numpy as np

def gen_cube_isosurface_to_np(d, h, w, max_distance, center, dtype=np.uint8):
    """
    Generate a 3D numpy array where the value at the center is max_distance
    and values decrease linearly along x, y, z directions, forming a cube isosurface.
    The resulting array is floored and cast to uint8.

    Parameters:
    - d, h, w: Dimensions of the 3D array.
    - max_distance: Value at the center of the cube.
    - center: A tuple (z, y, x) representing the center of the cube.

    Returns:
    - A 3D numpy array of type uint8, with values floored.
    """
    # Create coordinate grids for z, y, x
    z = np.arange(d)[:, None, None]
    y = np.arange(h)[None, :, None]
    x = np.arange(w)[None, None, :]
    
    # Calculate distances from the center in each direction
    distance_x = max_distance - np.abs(x - center[2])
    distance_y = max_distance - np.abs(y - center[1])
    distance_z = max_distance - np.abs(z - center[0])
    
    # Calculate the minimum distance to create the isosurface effect
    distance_array = np.minimum(np.minimum(distance_x, distance_y), distance_z)
    
    # Floor and convert to uint8
    if dtype == np.uint8:
        distance_array = np.floor(distance_array).astype(np.uint8)
    else:
        distance_array = distance_array
    
    return distance_array



# 0.9ms
def write_np_to_raw_fast2(file, data, factor, dtype=np.uint8):
    d, h, w = data.shape
    newarray = data[::factor, ::factor, ::factor]
    with open(file,'wb') as f:
        byteArray = bytearray(newarray)
        f.write(byteArray)

def main(out, d, h, w, dtype = np.uint8):

    factor = 1
    values = gen_cube_isosurface_to_np(d, h, w, int(w/4), (int(w/2), int(h/2), int(d/2)))
    tic = time.time()
    write_np_to_raw_fast2(out, values, factor, dtype)
    toc = time.time()
    print(f'Time:{(toc-tic)*1000} ms')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument('-o', '--out', type=str, required=True, help="out file name")
    parser.add_argument('-w', '--width', type=int, default=64, help="width")
    parser.add_argument('-h', '--height', type=int, default=64, help="height")
    parser.add_argument('-d', '--depth', type=int, default=64, help="depth")
    parser.add_argument('-t', '--type', type=str, default="byte", help="data type, byte, float")
    args = parser.parse_args()
    
    main(args.out, args.depth, args.height, args.width, np.uint8 if args.type=="byte" else np.float32)


    # py .\rawcube.py -o cube_64x64x64_uint8.raw
    # py .\rawtotec.py -d 64 -h 64 -w 64 .\cube_64x64x64_uint8.raw
    # .\rawtoplt.exe -d 64 -h 64 -w 64 -t uint8 .\cube_64x64x64_uint8.raw

    #  py .\rawcube.py -o cube_128x128x128_uint8.raw -d 128 -h 128 -w 128
    #  py .\rawtotec.py -d 128 -h 128 -w 128 .\cube_128x128x128_uint8.raw
    #  .\rawtoplt.exe -d 128 -h 128 -w 128 -t uint8 .\cube_128x128x128_uint8.raw