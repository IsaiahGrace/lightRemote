# Setup Zephyr workspace and build this project

```bash
mkdir zephyr
cd zephry
python -m venv venv
source venv/bin/activate
python -m pip install west
west init .
west update
west packages pip --install
git clone <lightRemote>
west build -p always -b frdm_mcxn947/mcxn947/cpu0 --sysbuild lightRemote/zephyr/cpu0
west flash
# west config build.sysbuild True
```
