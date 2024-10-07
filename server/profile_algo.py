import algorithm
import cProfile
import params

config = params.Config(
    delta=(1.0 / 2000.0),
    num_pixels=4000,
    scaling_root=2.0,
)

algo = algorithm.Algorithm(config, params.Params())


def main():
    cProfile.run("algo.update()")


if __name__ == "__main__":
    main()
