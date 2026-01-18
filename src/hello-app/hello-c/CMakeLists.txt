cmake_minimum_required(VERSION 3.10)

project(hello-c LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_executable(hello-c
    src/main.c
    src/hello.c
)

target_include_directories(hello-c
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

install(TARGETS hello-c
    RUNTIME DESTINATION bin
)