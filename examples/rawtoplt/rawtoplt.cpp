/* This example creates a simple set of IJ-ordered zones */
/* DOCSTART:ij_ordered.txt*/


// Internal testing flags
// RUNFLAGS:none
// RUNFLAGS:--szl


#include "TECIO.h"
#include "MASTER.h" /* for defintion of NULL */
#include <string>
#include <filesystem>
#include <fstream>
#include <vector>
#include <iostream>
#include <type_traits>
#include "cxxopts.hpp"

enum class VoxelDType {
    // UINT8,
    // UINT16,
    // UINT32,
    FLOAT32,
    FLOAT64
};

template <VoxelDType T> struct VoxelDTypeTraits;
// template <> struct VoxelDTypeTraits<VoxelDType::UINT8> { using type = uint8_t; };
// template <> struct VoxelDTypeTraits<VoxelDType::UINT16> { using type = uint16_t; };
// template <> struct VoxelDTypeTraits<VoxelDType::UINT32> { using type = uint32_t; };
template <> struct VoxelDTypeTraits<VoxelDType::FLOAT32> { using type = float; };
template <> struct VoxelDTypeTraits<VoxelDType::FLOAT64> { using type = double; };

template<typename RAWT, typename T>
bool loadRawFileInternal(const std::string& fileName, int32_t d, int32_t h, int32_t w, std::vector<T>& buffer) {
    std::ifstream file(fileName, std::ios::binary);
    if (!file) {
        std::cerr << "Error: Could not open the file " << fileName << std::endl;
        return false;
    }

    // resize target buffer
    uint64_t elementCount = w * h * d;
    buffer.resize(elementCount);

    // read file to buffer and temp buffer then copy to buffer
    uint64_t fileSize = elementCount * sizeof(RAWT);
    if(std::is_same<RAWT, T>::value) {
        file.read(reinterpret_cast<char*>(buffer.data()), fileSize);
    } else {
        std::vector<RAWT> readBuffer(elementCount);    
        file.read(reinterpret_cast<char*>(readBuffer.data()), fileSize);
        for (size_t i = 0; i < elementCount; ++i) {
            buffer[i] = static_cast<T>(readBuffer[i]);
        }
    }

    return true;
}

template<typename ElementType>
bool loadRawFile(const std::string& fileName, int32_t d, int32_t h, int32_t w, std::vector<ElementType>& buffer, const std::string& rawType) {
    if (rawType == "uint8") {
        loadRawFileInternal<uint8_t, ElementType>(fileName, d, h, w, buffer);
    } else if (rawType == "uint16") {
        loadRawFileInternal<uint16_t, ElementType>(fileName, d, h, w, buffer);
    } else if (rawType == "uint32") {
        loadRawFileInternal<uint32_t, ElementType>(fileName, d, h, w, buffer);
    } else if (rawType == "float32") {
        loadRawFileInternal<float, ElementType>(fileName, d, h, w, buffer);
    } else if (rawType == "float64") {
        loadRawFileInternal<double, ElementType>(fileName, d, h, w, buffer);
    }
    printf("load data shape whd {%d, %d, %d}", w, h, d);

    return true;
}

std::string getOutFileName(const std::string& in_file, const std::string& ext) {

    std::filesystem::path path(in_file);
    std::string dir_name = path.parent_path().string();
    std::string file_name = path.stem().string();
    std::string file_ext = path.extension().string();

    std::string out_file = dir_name + "/" + file_name + "." + ext;

    return out_file;
}

template<typename ElementType>
std::vector<ElementType> downSampleData(
    int32_t d, int32_t h, int32_t w, 
    int32_t newd, int32_t newh, int32_t neww, 
    std::vector<ElementType>& buffer, int step
    ) {

    newd = d / step;
    newh = h / step;
    neww = w / step;
    newd = newd ==0 ? 1 : newd;
    newh = newh ==0 ? 1 : newh;
    neww = neww ==0 ? 1 : neww;

    size_t newSize = newd * newh * neww;

    std::vector<ElementType> newbuffer(newSize);

    size_t i = 0;
    for (int z = 0; z < d; z += step) {
        for (int y = 0; y < h; y += step) {
            for (int x = 0; x < w; x += step) {
                newbuffer[i] = buffer[z * h * w + y * w + x];
                i++;
            }
        }
    }
    return newbuffer;
}


/// @brief old api to plt, write float/double sgrid plus xyz to plt
/// @tparam T float or double
/// 
/// @notes: 
///     1. old api write both plt and szplt
///     2. packing is block
///     3. data type is float or double, no other types
template<typename ElementType>
void writeScalarToPlt(const std::string& outFilePath, int32_t d, int32_t h, int32_t w, std::vector<ElementType>& buffer, int32_t step) {

    // std::filesystem::path path(outFilePath);
    // std::string outFileName = path.filename().string();
    // std::string dirName = path.parent_path().string();


    INTEGER4 Debug      = 1;
    INTEGER4 VIsDouble  = 0;
    INTEGER4 FileType   = 0;
    INTEGER4 fileFormat = 0; // 0 == PLT, 1 == SZPLT
    // if (argc == 2 && strncmp(argv[1],"--szl",5) == 0)
    //     fileFormat = 1; 
    // else
    //     fileFormat = 0; 

    INTEGER4 I          = 0; /* Used to track return codes */

    /*
     * Open the file and write the tecplot datafile
     * header information
     */
    // api version 142, binary version 112, define at TecplotVersion.h
    // after this version only support block packing
    I = TECINI142((char*)"IJK Ordered Zones", /* Name of the entire
                                              * dataset.
                                              */
                  (char*)"X Y Z P",  /* Defines the variables for the data
                                    * file. Each zone must contain each of
                                    * the variables listed here. The order
                                    * of the variables in the list is used
                                    * to define the variable number (e.g.
                                    * X is Var 1).
                                    */
                  (char*)outFilePath.c_str(),
                  (char*)".",      /* Scratch Directory */
                  &fileFormat,
                  &FileType,
                  &Debug,
                  &VIsDouble);

    INTEGER4 ICellMax                 = 0;
    INTEGER4 JCellMax                 = 0;
    INTEGER4 KCellMax                 = 0;
    INTEGER4 DIsDouble                = 0;
    double   SolTime                  = 360.0;
    INTEGER4 StrandID                 = 0;      /* StaticZone */
    INTEGER4 ParentZn                 = 0;
    INTEGER4 IsBlock                  = 1;      /* Block */
    INTEGER4 NFConns                  = 0;
    INTEGER4 FNMode                   = 0;
    INTEGER4 TotalNumFaceNodes        = 0; // 1;
    INTEGER4 TotalNumBndryFaces       = 0; // 1;
    INTEGER4 TotalNumBndryConnections = 0; // 1;
    INTEGER4 ShrConn                  = 0;

    /*Ordered Zone Parameters*/
    INTEGER4 IMax = w;
    INTEGER4 JMax = h;
    INTEGER4 KMax = d;

    // fill data
    std::vector<ElementType> X1(w * h * d);
    std::vector<ElementType> Y1(w * h * d);
    std::vector<ElementType> Z1(w * h * d);
    std::vector<ElementType> P1(w * h * d);
    size_t i = 0;
    for (int z = 0; z < d; z += 1) {
        for (int y = 0; y < h; y += 1) {
            for (int x = 0; x < w; x += 1) {
                X1[i] = static_cast<ElementType>(x * step);
                Y1[i] = static_cast<ElementType>(y * step);
                Z1[i] = static_cast<ElementType>(z * step);
                P1[i] = buffer[i];
                i++;
            }
        }
    }


    /*  Ordered Zone */
    INTEGER4 ZoneType = ZONETYPE_ORDERED;
    I = TECZNE142((char*)"Ordered Zone",
                  &ZoneType,
                  &IMax,
                  &JMax,
                  &KMax,
                  &ICellMax,
                  &JCellMax,
                  &KCellMax,
                  &SolTime,
                  &StrandID,
                  &ParentZn,
                  &IsBlock,
                  &NFConns,
                  &FNMode,
                  &TotalNumFaceNodes,
                  &TotalNumBndryFaces,
                  &TotalNumBndryConnections,
                  NULL,
                  NULL,
                  NULL,
                  &ShrConn);
    INTEGER4 III = IMax * JMax * KMax;
    I   = TECDAT142(&III, X1.data(), &DIsDouble);
    I   = TECDAT142(&III, Y1.data(), &DIsDouble);
    I   = TECDAT142(&III, Z1.data(), &DIsDouble);
    I   = TECDAT142(&III, P1.data(), &DIsDouble);

    I = TECEND142();
    return;

}


/// @brief new api, write uint8/uint16/uint32/float/double sgrid plus xyz to plt
/// @tparam T float or double
template<VoxelDType T, typename ElementType = VoxelDTypeTraits<T>::type>
void writeScalarToSZL(const std::string& outFilePath, int32_t d, int32_t h, int32_t w, std::vector<ElementType>& buffer) {

    // void* fileHandle = NULL;
    // res = tecFileWriterOpen("outfile.szplt", "IJ Ordered Dataset", "X,Y,P", fileFormat, fileType, defaultDataType, NULL, fileHandle);
    // // Create a IJ-Ordered Zone
    // int32_t zoneHandle;
    // int varTypes[3] = {1,1,2}; // single, single, double
    // res = tecZoneCreateIJK(fileHandle, "IJ Ordered Zone", IMax, JMax, KMax, &varTypes[0], NULL, NULL, NULL, 0, 0, 0, &zoneHandle);
    // // Create X, Y, P array data...
    // int64_t numPoints = IMax*JMax;
    // res = tecZoneVarWriteFloatValues(fileHandle, zoneHandle, xVarNum, 0, numPoints , X);
    // tecZoneVarWriteUInt8Values
    // res = tecZoneVarWriteFloatValues(fileHandle, zoneHandle, yVarNum, 0, numPoints , Y);
    // res = tecZoneVarWriteDoubleValues(fileHandle, zoneHandle, pVarNum, 0, numPoints , P);
    // res = tecFileWriterClose(&fileHandle);

}

template<VoxelDType VDT, typename T = VoxelDTypeTraits<VDT>::type>
void rawtoplt(cxxopts::ParseResult& result) {
    int32_t w = result["width"].as<int32_t>();
    int32_t h = result["height"].as<int32_t>();
    int32_t d = result["depth"].as<int32_t>();
    int32_t downsample = result["downsample"].as<int32_t>();
    std::string fileName = result["file"].as<std::string>();
    VoxelDType dtype = VoxelDType::FLOAT32;
    std::string rawType = result["type"].as<std::string>();

    // load file
    std::vector<T> buffer;
    if(!loadRawFile<T>(fileName, d, h, w, buffer, rawType)) {
        printf("error load raw file");
    }

    // downsample
    if (downsample != 1) {
        buffer = downSampleData<T>(d, h, w, d, h, w, buffer, downsample);
    }

    // write
    std::string outfile = getOutFileName(fileName, "plt");
    writeScalarToPlt<T>(outfile, d, h, w, buffer, downsample);

    printf("finish write file:%s\n", outfile.c_str());

}


int main(int argc, const char *argv[]) {

    // parse cli
    cxxopts::Options options("rawtoplt", "convert raw file to plt file");
    options.add_options()
        ("file", "File name", cxxopts::value<std::string>())  // string argument
        ("w,width", "width", cxxopts::value<int32_t>()->default_value("1"))  // integer argument with default value
        ("h,height", "height", cxxopts::value<int32_t>()->default_value("1"))  // integer argument with default value
        ("d,depth", "depth", cxxopts::value<int32_t>()->default_value("1"))  // integer argument with default value
        ("t,type", "raw data type uint8 float32 float64", cxxopts::value<std::string>()->default_value("uint8"))  // integer argument with default value
        ("downsample", "downsample factor", cxxopts::value<int32_t>()->default_value("1"))  // boolean flag
        // ("test", "flag no value", cxxopts::value<bool>()->default_value("false"))  // boolean flag
        ("help", "Print usage");

    // define position
    options.parse_positional({"file"});

    // parse
    cxxopts::ParseResult result;
    try {
        result = options.parse(argc, argv);
    } catch(cxxopts::exceptions::parsing& e) {
        printf("exception: %s\n", e.what());
        return 0;
    }

    // check para
    if (result.count("help")) {
        std::cout << options.help() << std::endl;
        return 0;
    }
    if (!result.count("file")) {
        printf("no file");
        return 0;
    }

    
    // convert
    VoxelDType dtype = VoxelDType::FLOAT32;
    if (dtype == VoxelDType::FLOAT32) {
        rawtoplt<VoxelDType::FLOAT32>(result);
    } else if (dtype == VoxelDType::FLOAT64) {
        rawtoplt<VoxelDType::FLOAT64>(result);
    }
    return 0;
}
/* DOCEND */


// uint8 to float32 plt
// ./rawtoplt.exe -d 64 -h 64 -w 64 -t uint8 D:\data\dataset\scivis\foot_64x64x64_uint8.raw
