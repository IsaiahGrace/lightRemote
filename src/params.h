#pragma once

#include <stdint.h>

#define NUM_PIXELS 400

typedef struct {
    float hue;
    float sat;
    float val;
    float dh;
    float ds;
    float dv;
    float temp;
} Params;

typedef struct {
    float delta;
    float scalingRoot;
    float restoringForce;
    float mass;
    float friction;
} Config;

