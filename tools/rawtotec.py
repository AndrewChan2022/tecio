import os, sys, time
import numpy as np
import struct
import argparse

def load_uint8_raw_to_array(file, d, h, w):
    element_count = w * h * d
    size = element_count
    with open(file, mode='rb') as file: # b for binary read
        file_content = file.read(size) # bytes like array
        byte_array = struct.unpack("B" * element_count, file_content) # unpack to parse binary to uint8 array
    return byte_array

def load_raw_to_np(file, d, h, w, dtype = np.uint8):
    element_count = w * h * d
    size = element_count * np.dtype(dtype).itemsize
    data_array = np.fromfile(file, dtype, element_count)
    data_array = data_array.reshape((d, h, w))
    print(f'load data shape: {data_array.shape}, dtype: {data_array.dtype}')
    return data_array

def _get_out_file_name(in_file:str, ext:str):
    # path = os.path(in_file)
    path = in_file
    dir_name = os.path.dirname(path)
    file_name_ext = os.path.basename(path)
    file_name, _ = os.path.splitext(file_name_ext)
    return os.path.join(dir_name, f'{file_name}.{ext}')

def write_np_to_tec_ascii(values, file_path:str, target_ndim:int, block:bool):

    # 3d: z, y, x
    # 2d: y, x
    # 1d: x
    ndim = values.ndim
    downsample = False
    element_count = int(values.size / 64) if downsample else values.size     # = np.prod(values.ndim)
    step = 4 if downsample else 1
    
    print(f'write to file:{file_path}')
    with open(file_path, "w") as f:
        # write header
        f.write(f'TITLE = "tecplot 1d ordered"\n')
        f.write(f'VARIABLES = "X", "Y", "Z", "PHI"\n')

        
        # zone.header
        if (target_ndim == 3 and ndim == 3):
            d, h, w = values.shape
            if downsample:
                d /= 4
                h /= 4
                w /= 4
            f.write(f'ZONE I={w} J={h} K={d} DATAPACKING={"BLOCK" if block else "POINT"}, \n')
        else:
            f.write(f'ZONE I={element_count} DATAPACKING={"BLOCK" if block else "POINT"}, \n')
        
        # zone.data
        if ndim == 1:
            w, = values.shape
            for x in range(w):
                # xyz φ
                f.write(f'{x} 0 0 {values[x]}\n')
        elif ndim == 2:
            h, w, = values.shape
            xarr = []
            yarr = []
            zarr = []
            parr = []
            for y in range(h):
                for x in range(w):
                    # xyz φ
                    if not block:
                        f.write(f'{x} {y} 0 {values[y][x]}\n')
                    else:
                        xarr.append(x)
                        yarr.append(y)
                        zarr.append(0)
                        parr.append(values[y][x])
            #
            if block:
                newline = "\n"
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(xarr)]
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(yarr)]
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(zarr)]
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(parr)]

        elif ndim == 3:
            ncount = 0
            d, h, w = values.shape
            xarr = []
            yarr = []
            zarr = []
            parr = []
            for z in range(0, d, step):
                for y in range(0, h, step):
                    for x in range(0, w, step):
                        # xyz φ
                        if not block:
                            f.write(f'{x} {y} {z} {values[z][y][x]}\n')
                        else:
                            xarr.append(x)
                            yarr.append(y)
                            zarr.append(z)
                            parr.append(values[z][y][x])
                        ncount += 1
            #
            if block:
                newline = "\n"
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(xarr)]
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(yarr)]
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(zarr)]
                [f.write(f'{e}{newline if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(parr)]
                # [f.write(f'{e}{"\n" if (i + 1) % 6 == 0 else " "}') for i, e in enumerate(parr)]
            
            #
            print(f'ncount:{ncount}, element_count:{element_count}')
        else:
            assert(f'dim not known:{ndim}, must be 1 or 2 or 3')

def write_np_to_ply_ascii(values, file_path, target_ndim:int, block:bool):
    # 3d: z, y, x
    # 2d: y, x
    # 1d: x
    ndim = values.ndim
    downsample = False
    element_count = int(values.size / 64) if downsample else values.size     # = np.prod(values.ndim)
    step = 4 if downsample else 1
    
    print(f'write to file:{file_path}')
    with open(file_path, "w") as f:
        # write header
        f.write(f'ply\n')
        f.write(f'format ascii 1.0\n')
        f.write(f'comment 3d point cloud\n')
        f.write(f'element vertex {element_count}\n')     # vertex count, point cloud no face
        f.write(f'property float x\n')
        f.write(f'property float y\n')
        f.write(f'property float z\n')
        f.write(f'property float c\n')
        f.write(f'end_header\n')

        # data {x y z c}
        if ndim == 1:
            w, = values.shape
            for x in range(w):
                # xyz φ
                f.write(f'{x} 0 0 {values[x]}\n')
        elif ndim == 2:
            h, w, = values.shape
            for y in range(h):
                for x in range(w):
                    # xyz φ
                    f.write(f'{x} {y} 0 {values[y][x]}\n')
        elif ndim == 3:
            # d, h, w = values.shape
            # for z in range(d):
            #     for y in range(h):
            #         for x in range(w):
            #             # xyz φ
            #             f.write(f'{x} {y} {z} {values[z][y][x]}\n')

            ncount = 0
            d, h, w = values.shape
            for z in range(0, d, step):
                for y in range(0, h, step):
                    for x in range(0, w, step):
                        # xyz φ
                        f.write(f'{x} {y} {z} {values[z][y][x]}\n')
                        ncount += 1
            print(f'ncount:{ncount}, element_count:{element_count}')
        else:
            assert(f'dim not known:{ndim}, must be 1 or 2 or 3')

def main(file, d, h, w, format, target_ndim, dtype = np.uint8, block:bool = True):
    # a = load_raw_to_np("D:/data/dataset/scivis/foot_256x256x256_uint8.raw", 256, 256, 256)
    # print(a[:1000])
    values = load_raw_to_np(file, d, h, w, dtype)
    # print(values[:100][:100])
    if format == "tec":
        write_np_to_tec_ascii(values, _get_out_file_name(file, format), target_ndim, block)
    elif format == "ply":
        write_np_to_ply_ascii(values, _get_out_file_name(file, format), target_ndim, block)
    else:
        assert(f'format not known:{format}, must be plt or ply')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument('file', nargs='?')  # position args
    parser.add_argument('-w', '--width', type=int, default=256, help="width")
    parser.add_argument('-h', '--height', type=int, default=256, help="height")         # override help
    parser.add_argument('-d', '--depth', type=int, default=256, help="depth")
    parser.add_argument('-t', '--type', type=str, default="byte", help="data type, byte, float")
    parser.add_argument('-f', '--format', type=str, default="tec", help="tecplot tec ascii or ply point cloud")
    parser.add_argument('-b', '--block', action="store_true", default=False, help="datapacking block or point")
    parser.add_argument('--dim', type=int, default=3, help="1 2 3 for 1d 2d 3d grid")   # no -d
    args = parser.parse_args()
    
    main(args.file, 
        d=args.depth, h=args.height, w=args.width, 
        format=args.format,  target_ndim=args.dim, 
        dtype=np.uint8 if args.type=="byte" else np.float32,
        block=args.block)

    # py .\rawtotec.py -d 64 -h 64 -w 64 D:/data/dataset/scivis/foot_64x64x64_uint8.raw --format ply
    # py .\rawtotec.py -d 64 -h 64 -w 64 D:/data/dataset/scivis/foot_64x64x64_uint8.raw