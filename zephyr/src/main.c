#include <stdio.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/led_strip.h>
#include <zephyr/drivers/mbox.h>
#include <zephyr/drivers/spi.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>

#define LOG_LEVEL 4
#include <zephyr/logging/log.h>
LOG_MODULE_REGISTER(main);

#include "algorithm.h"
#include "params.h"

static const struct gpio_dt_spec red_led = GPIO_DT_SPEC_GET(DT_ALIAS(red_led), gpios);
static const struct gpio_dt_spec green_led = GPIO_DT_SPEC_GET(DT_ALIAS(green_led), gpios);

#define STRIP_NODE DT_ALIAS(led_strip)

#if DT_NODE_HAS_PROP(DT_ALIAS(led_strip), chain_length)
#define STRIP_NUM_PIXELS DT_PROP(DT_ALIAS(led_strip), chain_length)
#else
#error Unable to determine length of LED strip
#endif

#define DELAY_TIME K_MSEC(CONFIG_SAMPLE_LED_UPDATE_DELAY)

static struct led_rgb pixels[STRIP_NUM_PIXELS];

static const struct device* const strip = DEVICE_DT_GET(STRIP_NODE);

static void callback(const struct device* dev,
                     mbox_channel_id_t channel_id,
                     void* user_data,
                     struct mbox_msg* data)
{
    gpio_pin_set_dt(&red_led, 0);
    // gpio_pin_toggle_dt(&green_led);
}

Config TheConfig = {
    .delta = 1.0 / 2000.0,
    .scalingRoot = 2.0,
    .restoringForce = 0.1,
    .mass = 5.0,
    .friction = 1 - 0.015,
};

Params TheParams = {
    .hue = 0.0,
    .sat = 1.0,
    .val = 1.0,
    .dh = 0.1,
    .ds = 0.1,
    .dv = 0.1,
    .temp = 0.15,
};

Algorithm TheAlgorithm;

float fract(float x)
{
    return x - (int)x;
}

float mix(float a, float b, float t)
{
    return a + (b - a) * t;
}

float step(float e, float x)
{
    return x < e ? 0.0 : 1.0;
}

float constrain(float x, float a, float b)
{
    if (x < a) {
        return a;
    } else if (x > b) {
        return b;
    } else {
        return x;
    }
}

float absf(float x)
{
    if (x < 0.0f) {
        return -x;
    } else {
        return x;
    }
}

int main(void)
{
    printk("CPU0 main()\n");

    int ret;

    if (!gpio_is_ready_dt(&red_led) || !gpio_is_ready_dt(&green_led)) {
        return 0;
    }

    ret = gpio_pin_configure_dt(&red_led, GPIO_OUTPUT);
    if (ret) {
        return 0;
    }

    ret = gpio_pin_configure_dt(&green_led, GPIO_OUTPUT);
    if (ret) {
        return 0;
    }

    ret = gpio_pin_set_dt(&green_led, 0);
    if (ret) {
        return 0;
    }

    if (!device_is_ready(strip)) {
        return 0;
    }

    const struct mbox_dt_spec rx_channel = MBOX_DT_SPEC_GET(DT_PATH(mbox_consumer), rx);
    const struct mbox_dt_spec tx_channel = MBOX_DT_SPEC_GET(DT_PATH(mbox_consumer), tx);

    printk("Maximum RX channels: %d\n", mbox_max_channels_get_dt(&rx_channel));

    ret = mbox_register_callback_dt(&rx_channel, callback, NULL);
    if (ret < 0) {
        return 0;
    }

    ret = mbox_set_enabled_dt(&rx_channel, true);
    if (ret < 0) {
        return 0;
    }

    printk("Maximum bytes of data in the TX message: %d\n", mbox_mtu_get_dt(&tx_channel));
    printk("Maximum TX channels: %d\n", mbox_max_channels_get_dt(&tx_channel));

    algorithm_init(&TheAlgorithm, &TheConfig, &TheParams);

    gpio_pin_set_dt(&red_led, 0);

    while (1) {
        algorithm_update(&TheAlgorithm);

        for (size_t i = 0; i < ARRAY_SIZE(pixels); i++) {
            float red = TheAlgorithm.val[i] * mix(1.0f, constrain(absf(fract(TheAlgorithm.hue[i] + 1.0f) * 6.0f - 3.0f) - 1.0f, 0.0f, 1.0f), TheAlgorithm.sat[i]);
            float grn = TheAlgorithm.val[i] * mix(1.0f, constrain(absf(fract(TheAlgorithm.hue[i] + 0.6666666f) * 6.0f - 3.0f) - 1.0f, 0.0f, 1.0f), TheAlgorithm.sat[i]);
            float blu = TheAlgorithm.val[i] * mix(1.0f, constrain(absf(fract(TheAlgorithm.hue[i] + 0.3333333f) * 6.0f - 3.0f) - 1.0f, 0.0f, 1.0f), TheAlgorithm.sat[i]);

            // When I scale all the way to 256, the pixels glitch out. Voltage drop? SPI timing?
            pixels[i].r = red * 100;
            pixels[i].g = grn * 100;
            pixels[i].b = blu * 100;
        }

        led_strip_update_rgb(strip, pixels, STRIP_NUM_PIXELS);

        ret = mbox_send_dt(&tx_channel, NULL);
        if (ret) {
            return 0;
        }
        gpio_pin_set_dt(&red_led, 1);

        k_msleep(2000);
    }

    return 0;
}
