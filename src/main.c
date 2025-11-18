#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>

// Settings
static const int32_t sleep_time_ms = 500;
static const struct gpio_dt_spec red_led = GPIO_DT_SPEC_GET(DT_ALIAS(my_red_led), gpios);
static const struct gpio_dt_spec green_led = GPIO_DT_SPEC_GET(DT_ALIAS(my_green_led), gpios);

int main(void)
{
    int ret;
    int state = 0;

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

    // Do forever
    while (1) {
        // Change the state of the pin and print
        state = !state;
        printk("LED state: %d\r\n", state);

        // Set pin state
        ret = gpio_pin_set_dt(&red_led, state);
        if (ret < 0) {
            return 0;
        }
        ret = gpio_pin_set_dt(&green_led, !state);
        if (ret < 0) {
            return 0;
        }

        // Sleep
        k_msleep(sleep_time_ms);
    }

    return 0;
}
