cmake_minimum_required(VERSION 3.10)

project(lsmy-hello LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_library(lsmy-hello SHARED
    src/lsmy_hello.c
)

target_include_directories(lsmy-hello
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(lsmy-hello PROPERTIES
    OUTPUT_NAME lsmy_hello
    VERSION 1.0.0
    SOVERSION 1
)

install(TARGETS lsmy-hello
    LIBRARY DESTINATION lib
)

install(DIRECTORY include/
    DESTINATION include
)
