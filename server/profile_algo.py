from rich import print
import algorithm
import cProfile
import params
import timeit

config = params.Config(
    delta=(1.0 / 2000.0),
    num_pixels=13398,
    scaling_root=2.0,
)

params = params.Params(
    h=1.0,
    s=0.5,
    v=0.8,
    dh=0.05,
    ds=0.0,
    dv=0.0,
    t=0.5,
)


algo = algorithm.Algorithm(config, params)

# cProfile.run("algo.update()")

repeat = 10
time = timeit.timeit(algo.update, number=repeat)
print(f"{time} / {repeat} = {time/repeat} seconds per update")
