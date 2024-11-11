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

    # Define the parameters for the ellipsoidal shape
    a, b, c = 1.0, 0.8, 0.6  # Semi-principal axes of the ellipsoid
    
    # Calculate squared distances to avoid unnecessary sqrt initially
    dist_sq = ((z - center[1])/c)**2 + ((y - center[1])/b)**2 + ((x - center[0])/a)**2
    dist_sq = np.sqrt(dist_sq)
    
    # Initialize the 3D array with zeros
    # distance_array = dist_sq

    # Compute the radius and avoid division by zero
    r = np.sqrt((x - center[1])**2 + (y - center[1])**2 + (z - center[0])**2) + 1e-10

    # # Calculate the angle of latitude (phi) and angle of longitude (theta)
    phi = np.arcsin((z - center[2]) / r)  # Latitude angle
    theta = np.arctan2(y - center[1], x - center[0])  # Longitude angle
    phi *= 10
    theta *= 5

    # # Compute the value for each point in the grid
    # grid_values = distance_array + 500 * np.sin(theta) # 20 * np.cos(phi) + 30 * np.sin(theta)
    # grid_values = dist_sq + 0.1 * np.sin(phi) + 0.5 * np.sinc(theta)
    grid_values = 4 * (dist_sq + 2 * np.sin(phi) * 2 * np.sinc(theta))
    
    # Apply ceiling and cast to uint8, then assign to the distance_array
    # if dtype == np.uint8:
    #     distance_array = np.floor(distance_array).astype(np.uint8)
    
    return grid_values

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
    parser.add_argument('-t', '--type', type=str, default="float", help="data type, byte, float")
    args = parser.parse_args()
    
    main(args.out, args.depth, args.height, args.width, np.uint8 if args.type=="byte" else np.float32)

    #  py .\sincsphere.py -o sincsphere_8x8x8_float32.raw -d 8 -h 8 -w 8 -t float
    #  py .\rawtotec.py -d 8 -h 8 -w 8 -t float .\sincsphere_8x8x8_float32.raw
    #  .\rawtoplt.exe -d 8 -h 8 -w 8 -t float32 .\sincsphere_8x8x8_float32.raw

    # py .\rawsphere.py -o sphere_64x64x64_uint8.raw
    # py .\rawtotec.py -d 64 -h 64 -w 64 .\sphere_64x64x64_uint8.raw
    # .\rawtoplt.exe -d 64 -h 64 -w 64 -t uint8 .\sphere_64x64x64_uint8.raw

    #  py .\rawsphere.py -o sphere_128x128x128_uint8.raw -d 128 -h 128 -w 128
    #  py .\rawtotec.py -d 128 -h 128 -w 128 .\sphere_128x128x128_uint8.raw
    #  .\rawtoplt.exe -d 128 -h 128 -w 128 -t uint8 .\sphere_128x128x128_uint8.raw

    #  py .\sincsphere.py -o sincsphere_128x128x128_float32.raw -d 128 -h 128 -w 128 -t float
    #  py .\rawtotec.py -d 128 -h 128 -w 128 -t float .\sincsphere_128x128x128_float32.raw
    #  .\rawtoplt.exe -d 128 -h 128 -w 128 -t float32 .\sincsphere_128x128x128_float32.raw