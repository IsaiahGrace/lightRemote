#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

#include "algorithm.h"
#include "params.h"

// Settings
static const struct gpio_dt_spec red_led = GPIO_DT_SPEC_GET(DT_ALIAS(my_red_led), gpios);
static const struct gpio_dt_spec green_led = GPIO_DT_SPEC_GET(DT_ALIAS(my_green_led), gpios);

Config TheConfig = {
    .delta = 1.0 / 2000.0,
    .scalingRoot = 2.0,
    .restoringForce = 0.1,
    .mass = 5.0,
    .friction = 1 - 0.015,
};

Params TheParams = {
    .hue = 0.0,
    .sat = 0.0,
    .val = 0.0,
    .dh = 0.05,
    .ds = 0.0,
    .dv = 0.0,
    .temp = 0.15,
};

Algorithm TheAlgorithm;

int main(void)
{
    int ret;

    // Make sure that the GPIO was initialized
    if (!gpio_is_ready_dt(&red_led) || !gpio_is_ready_dt(&green_led)) {
        return 0;
    }

    // Set the GPIO as output
    ret = gpio_pin_configure_dt(&red_led, GPIO_OUTPUT);
    if (ret < 0) {
        return 0;
    }

    ret = gpio_pin_configure_dt(&green_led, GPIO_OUTPUT);
    if (ret < 0) {
        return 0;
    }

    algorithm_init(&TheAlgorithm, &TheConfig, &TheParams);

    // Do forever
    while (1) {
        gpio_pin_set_dt(&red_led, 1);
        gpio_pin_set_dt(&green_led, 0);

        algorithm_update(&TheAlgorithm);

        gpio_pin_set_dt(&red_led, 0);
        // gpio_pin_set_dt(&green_led, 1);

        // Sleep
        k_msleep(500);
    }

    return 0;
}
