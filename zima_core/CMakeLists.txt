cmake_minimum_required(VERSION 3.5)
project(zima_core)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_BUILD_TYPE Release)

find_package(ament_cmake REQUIRED)
find_package(Protobuf REQUIRED)
find_package(gflags REQUIRED)
find_package(glog REQUIRED)
find_package(zima_base REQUIRED)

get_filename_component(WORKSPACE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
set(ZIMA_BASE_PROTO_DIR "${WORKSPACE_DIR}/zima_base/zima/proto")

include_directories(
    ${PROJECT_SOURCE_DIR}
    ${PROJECT_SOURCE_DIR}/zima
    ${ZIMA_BASE_PROTO_DIR}
    ${PROTOBUF_INCLUDE_DIRS}
    ${CMAKE_CURRENT_BINARY_DIR}
)

file(GLOB_RECURSE COMPONENT_SRCS
    "${PROJECT_SOURCE_DIR}/zima/*.cpp"
    "${PROJECT_SOURCE_DIR}/zima/*.cc"
    "${PROJECT_SOURCE_DIR}/zima/*.c"
)

add_library(zima_core SHARED ${COMPONENT_SRCS})

target_link_libraries(zima_core
    zima_base
    protobuf::libprotobuf
    gflags
    glog
    pthread
)

if(EXISTS "${PROJECT_SOURCE_DIR}/src/main.cpp")
    add_executable(zima_core_main src/main.cpp)
    target_link_libraries(zima_core_main
        zima_core
        glog
        pthread
    )
    install(TARGETS zima_core_main RUNTIME DESTINATION bin)
endif()

install(TARGETS zima_core
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)
install(DIRECTORY zima/
    DESTINATION include/zima
    FILES_MATCHING PATTERN "*.h"
)
install(DIRECTORY zima/proto/
    DESTINATION include/zima/proto
    FILES_MATCHING PATTERN "*.proto"
)
install(DIRECTORY ${ZIMA_BASE_PROTO_DIR}/
    DESTINATION include/zima/proto
    FILES_MATCHING PATTERN "*.pb.h"
    PATTERN "*.proto"
)

ament_package()