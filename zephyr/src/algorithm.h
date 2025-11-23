#pragma once

#include "params.h"

typedef struct {
    Config* config;
    Params* params;

    float force[NUM_PIXELS];

    float hueVel[NUM_PIXELS];

    float linearSatVel[NUM_PIXELS];
    float linearValVel[NUM_PIXELS];

    float linearSat[NUM_PIXELS];
    float linearVal[NUM_PIXELS];

    float hue[NUM_PIXELS];
    float sat[NUM_PIXELS];
    float val[NUM_PIXELS];
} Algorithm;

void algorithm_init(Algorithm* algorithm, Config* config, Params* params);

void algorithm_update(Algorithm* algorithm);
