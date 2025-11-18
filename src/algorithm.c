#include "algorithm.h"

#include <stdint.h>
#include <zephyr/random/random.h>

#include "params.h"

void algorithm_init(Algorithm* algorithm, Config* config, Params* params)
{
    algorithm->config = config;
    algorithm->params = params;

    for (size_t i = 0; i < NUM_PIXELS; i++) {
        algorithm->force[i] = 1.0;
        algorithm->hueVel[i] = 0.0;
        algorithm->linearSatVel[i] = 0.0;
        algorithm->linearValVel[i] = 0.0;
        algorithm->linearSat[i] = 0.0;
        algorithm->linearVal[i] = 0.0;
        algorithm->hue[i] = sys_rand32_get() / (float)UINT32_MAX;
        algorithm->sat[i] = 0.0;
        algorithm->val[i] = 0.0;
    }
}

void algorithm_update_inner(Algorithm* algorithm, float* position, float* velocity, float target, float tolerance, int wraps)
{
    // Sometimes the fastest way to get to the target is to decrement
    // the hue, and wrap around from 0 -> 1. The "inverse target" is
    // the opposite point on the hue circle. By adding or subtracting
    // 1, we make the comparisons below simpler. Because we wrap the
    // values at the end of this function, the offset here doesn't
    // effect the final value.
    if (wraps) {
        float inverse_target = target + 0.5f;
        if (target > 1.0f) {
            target -= 1.0f;
        }

        if (inverse_target > target) {
            for (size_t i = 0; i < NUM_PIXELS; i++) {
                if (position[i] > inverse_target) {
                    position[i] -= 1.0f;
                }
            }
        } else {
            for (size_t i = 0; i < NUM_PIXELS; i++) {
                if (position[i] < inverse_target) {
                    position[i] += 1.0f;
                }
            }
        }
    }

    // Calculate random forces on the pixel due to temperature
    for (size_t i = 0; i < NUM_PIXELS; i++) {
        algorithm->force[i] = sys_rand32_get() / (float)UINT32_MAX;

        algorithm->force[i] -= algorithm->params->temp;

        if (algorithm->force[i] > 0.0f) {
            algorithm->force[i] = 0.0;
        } else {
            algorithm->force[i] += algorithm->params->temp / 2.0f;
        }

        if (algorithm->force[i] < 0.0f) {
            algorithm->force[i] = -1.0;
        } else if (algorithm->force[i] > 0.0f) {
            algorithm->force[i] = 1.0;
        }

        algorithm->force[i] *= algorithm->config->delta;
    }

    // Apply restoring forces
    float restoring_delta = algorithm->config->delta * algorithm->config->restoringForce;
    if (wraps || target == 0.0f) {
        for (size_t i = 0; i < NUM_PIXELS; i++) {
            if (position[i] > target + tolerance) {
                algorithm->force[i] -= restoring_delta;
            }
        }
    }

    for (size_t i = 0; i < NUM_PIXELS; i++) {
        if (position[i] < target - tolerance) {
            algorithm->force[i] += restoring_delta;
        }
    }

    // Acceleration = Force / Mass
    for (size_t i = 0; i < NUM_PIXELS; i++) {
        algorithm->force[i] /= algorithm->config->mass;
    }

    // Velocity += Acceleration
    for (size_t i = 0; i < NUM_PIXELS; i++) {
        velocity[i] += algorithm->force[i];
    }

    // Position += Velocity
    for (size_t i = 0; i < NUM_PIXELS; i++) {
        position[i] += velocity[i];
    }

    // Velocity *= friction
    for (size_t i = 0; i < NUM_PIXELS; i++) {
        velocity[i] *= algorithm->config->friction;
    }

    if (wraps) {
        for (size_t i = 0; i < NUM_PIXELS; i++) {
            if (position[i] < 0.0f) {
                position[i] += 1.0f;
            } else if (position[i] > 1.0f) {
                position[i] -= 1.0f;
            }
        }
    } else {
        for (size_t i = 0; i < NUM_PIXELS; i++) {
            if (position[i] < 0.0f) {
                position[i] = 0.0f;
            } else if (position[i] > 1.0f) {
                position[i] = 1.0f;
            }
        }
    }
}

void algorithm_update(Algorithm* algorithm)
{
    algorithm_update_inner(algorithm, algorithm->hue, algorithm->hueVel, algorithm->params->hue, algorithm->params->dh, 1);
    algorithm_update_inner(algorithm, algorithm->linearSat, algorithm->linearSatVel, algorithm->params->sat, algorithm->params->ds, 0);
    algorithm_update_inner(algorithm, algorithm->linearVal, algorithm->linearValVel, algorithm->params->val, algorithm->params->dv, 0);

    // This is where we raise it to the power of 1 / 1.2, to bend it above y=x
    // But that's expensive, so I just wont do it.
    for (size_t i = 0; i < NUM_PIXELS; i++) {
        algorithm->sat[i] = algorithm->linearSat[i];
        algorithm->val[i] = algorithm->linearVal[i];
    }
}
