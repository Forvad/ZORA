from multiprocessing.dummy import Pool

from Bridge.Holo_bridge import BridgeHolograph
from Utils.EVMutils import EVM
from config import CHECK_GWEI, THREAD


def main():
    private = EVM.open_private()
    private = private[4:]
    if CHECK_GWEI:
        EVM.check_gwei()

    with Pool(THREAD) as pols:
        pols.map(lambda prv: BridgeHolograph(prv), private)


if __name__ == "__main__":
    main()