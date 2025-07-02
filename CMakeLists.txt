cmake_minimum_required(VERSION 3.5)
project(zima_base)

# 编译选项
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_BUILD_TYPE Release)

# ROS2 基础
find_package(ament_cmake REQUIRED)
find_package(Protobuf REQUIRED)
find_package(gflags REQUIRED)
find_package(glog REQUIRED)

# 生成 proto 文件
file(GLOB_RECURSE PROTOBUF_FILES "${PROJECT_SOURCE_DIR}/zima/*.proto")
set(PROTO_META_BASE_DIR ${CMAKE_CURRENT_BINARY_DIR})
list(APPEND PROTO_FLAGS -I${PROJECT_SOURCE_DIR})

foreach(FIL ${PROTOBUF_FILES})
    get_filename_component(FIL_WE ${FIL} NAME_WE)
    get_filename_component(FILE_PATH ${FIL} DIRECTORY)
    string(REGEX MATCH "(zima/proto.*)" OUT_PATH ${FILE_PATH})

    set(PROTO_SRC "${CMAKE_CURRENT_BINARY_DIR}/${OUT_PATH}/${FIL_WE}.pb.cc")
    set(PROTO_HDR "${CMAKE_CURRENT_BINARY_DIR}/${OUT_PATH}/${FIL_WE}.pb.h")

    execute_process(
        COMMAND ${Protobuf_PROTOC_EXECUTABLE} ${PROTO_FLAGS} --cpp_out=${PROTO_META_BASE_DIR} ${FIL}
    )
    file(COPY ${PROTO_SRC} DESTINATION ${FILE_PATH})
    file(COPY ${PROTO_HDR} DESTINATION ${FILE_PATH})
endforeach()

# 包含目录
include_directories(
    ${PROJECT_SOURCE_DIR}
    ${PROJECT_SOURCE_DIR}/zima
    ${PROTOBUF_INCLUDE_DIRS}
    ${CMAKE_CURRENT_BINARY_DIR}
)

# 源文件
file(GLOB_RECURSE COMPONENT_SRCS
    "${PROJECT_SOURCE_DIR}/zima/*.cpp"
    "${PROJECT_SOURCE_DIR}/zima/*.cc"
    "${PROJECT_SOURCE_DIR}/zima/*.c"
    "${PROJECT_SOURCE_DIR}/zima/*.pb.cc"
)

# 静态和动态库
add_library(zima_base SHARED ${COMPONENT_SRCS})
add_library(zima_base_static STATIC ${COMPONENT_SRCS})

# 依赖
ament_target_dependencies(zima_base protobuf gflags glog)

# 可执行程序
add_executable(zima_main src/main.cpp)
ament_target_dependencies(zima_base protobuf gflags glog)
target_link_libraries(zima_base protobuf::libprotobuf gflags glog pthread)

# 安装规则
install(TARGETS zima_base zima_base_static
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(TARGETS zima_main
  RUNTIME DESTINATION bin
)

install(DIRECTORY zima/
  DESTINATION include/zima
  FILES_MATCHING PATTERN "*.h"
)

# proto 文件可选安装
install(DIRECTORY zima/
  DESTINATION include/zima
  FILES_MATCHING PATTERN "*.proto"
)

ament_package()