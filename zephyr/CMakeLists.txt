cmake_minimum_required(VERSION 3.22.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

set(REMOTE_ZEPHYR_DIR ${CMAKE_CURRENT_BINARY_DIR}/../remote/zephyr)

project(lightRemote)

FILE(GLOB app_sources src/*.c)
target_sources(app PRIVATE ${app_sources})
