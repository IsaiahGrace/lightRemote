#pragma once

#include <zephyr/device.h>

#if DT_NODE_HAS_PROP(DT_ALIAS(led_strip), chain_length)
#define STRIP_NUM_PIXELS DT_PROP(DT_ALIAS(led_strip), chain_length)
#else
#error Unable to determine length of LED strip
#endif

#define NUM_PIXELS STRIP_NUM_PIXELS

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
