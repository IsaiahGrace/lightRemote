#include <zephyr/drivers/mbox.h>
#include <zephyr/kernel.h>

#include <stdbool.h>

volatile bool recvd = false;

static void callback(const struct device* dev,
                     mbox_channel_id_t channel_id,
                     void* user_data,
                     struct mbox_msg* data)

{
    recvd = true;
}

int main(void)
{
    int ret;

    const struct mbox_dt_spec rx_channel = MBOX_DT_SPEC_GET(DT_PATH(mbox_consumer), rx);
    const struct mbox_dt_spec tx_channel = MBOX_DT_SPEC_GET(DT_PATH(mbox_consumer), tx);

    ret = mbox_register_callback_dt(&rx_channel, callback, NULL);
    if (ret < 0) {
        return 0;
    }

    ret = mbox_set_enabled_dt(&rx_channel, true);
    if (ret < 0) {
        return 0;
    }

    while (1) {
        k_msleep(532);

        if (recvd) {
            recvd = false;
            ret = mbox_send_dt(&tx_channel, NULL);
            if (ret < 0) {
                return 0;
            }
        }
    }
    return 0;
}
