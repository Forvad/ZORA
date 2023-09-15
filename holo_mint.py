from multiprocessing.dummy import Pool

from NFT_Zora.Holograph import mint_
from Utils.EVMutils import EVM
from config import CHECK_GWEI, THREAD


def main():
    private = EVM.open_private()
    if CHECK_GWEI:
        EVM.check_gwei()

    with Pool(THREAD) as pols:
        pols.map(lambda prv: mint_(prv), private)


if __name__ == "__main__":
    main()