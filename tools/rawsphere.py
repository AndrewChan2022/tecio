import time
import numpy as np
import struct
import argparse

import numpy as np

def gen_sphere_to_np(d, h, w, radius, center, dtype=np.uint8):
    """
    Generate a 3D numpy array where each element's value represents
    the distance to the given center, decreasing towards zero at the center.
    Values are rounded up and outside the radius are set to zero.

    Parameters:
    - d, h, w: Dimensions of the 3D array.
    - radius: Maximum radius of the sphere.
    - center: A tuple (z, y, x) representing the center of the sphere.

    Returns:
    - A 3D numpy array of type uint8, with values rounded up.
    """
    # Create coordinate grids for z, y, x
    z = np.arange(d, dtype=np.float32)[:, None, None]
    y = np.arange(h, dtype=np.float32)[None, :, None]
    x = np.arange(w, dtype=np.float32)[None, None, :]
    
    # Calculate squared distances to avoid unnecessary sqrt initially
    dist_sq = (z - center[0])**2 + (y - center[1])**2 + (x - center[2])**2
    
    # Initialize the 3D array with zeros
    distance_array = np.zeros((d, h, w), dtype=dtype)
    
    # Calculate distances within the radius and scale appropriately
    mask_within_radius = dist_sq <= radius**2
    # distance_values = radius - np.sqrt(dist_sq[mask_within_radius])
    distance_values = np.where(mask_within_radius, radius - np.sqrt(dist_sq), 0)
    
    # Apply ceiling and cast to uint8, then assign to the distance_array
    if dtype == np.uint8:
        distance_array[mask_within_radius] = np.floor(distance_values).astype(np.uint8)
    else:
        distance_array = distance_values
    
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
    values = gen_sphere_to_np(d, h, w, int(w/4), (int(w/2), int(h/2), int(d/2)), dtype)
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


    # py .\rawsphere.py -o sphere_64x64x64_uint8.raw
    # py .\rawtotec.py -d 64 -h 64 -w 64 .\sphere_64x64x64_uint8.raw
    # .\rawtoplt.exe -d 64 -h 64 -w 64 -t uint8 .\sphere_64x64x64_uint8.raw

    #  py .\rawsphere.py -o sphere_128x128x128_uint8.raw -d 128 -h 128 -w 128
    #  py .\rawtotec.py -d 128 -h 128 -w 128 .\sphere_128x128x128_uint8.raw
    #  .\rawtoplt.exe -d 128 -h 128 -w 128 -t uint8 .\sphere_128x128x128_uint8.raw

    #  py .\rawsphere.py -o sphere_128x128x128_float32.raw -d 128 -h 128 -w 128 -t float
    #  py .\rawtotec.py -d 128 -h 128 -w 128 -t float .\sphere_128x128x128_float32.raw
    #  .\rawtoplt.exe -d 128 -h 128 -w 128 -t float32 .\sphere_128x128x128_float32.raw