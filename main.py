import time

from MintFun.Pass_NFT import mint
from Utils.EVMutils import EVM
from NFT_Zora.Mint import mint_zora
from Bridge.Zora_bridge import ZoraBridge
from MintFun.Activation import auth
from Exchange.OKX import okx_withdraw
import config as cng
from multiprocessing.dummy import Pool
from Log.Loging import log


class WorkZora:
    def __init__(self, private_key):
        self.name_func = {'OKX': self.okx_withdraw, 'Mint_Fun': self.min_fun, 'Zora_Bridge': self.zora_bridge,
                          'Zora_NFT': self.zora_nft}
        self.private_key = private_key
        self.route = [self.name_func[func] for func in cng.Route]
        self.web3 = EVM.web3('zora')
        self.address = self.web3.eth.account.from_key(self.private_key).address
        self.start_work()

    def okx_withdraw(self):
        value = EVM.uniform_(cng.OKX_ETH)
        okx_withdraw(['ethereum'], self.address, value)
        EVM.waiting_coin(self.private_key, 'ethereum', '', value)

    def min_fun(self):
        mint(self.private_key)
        time.sleep(10)
        auth(self.private_key)

    def zora_bridge(self):
        value = EVM.uniform_(cng.Value_bridge)
        bridges = ZoraBridge(self.private_key, value)
        bridges.bridge()
        EVM.waiting_coin(self.private_key, 'zora', '', value)

    def zora_nft(self):
        mint_zora(self.private_key)

    def start_work(self):
        EVM.delay_start()
        for func in self.route:
            func()


def main():
    private = EVM.open_private()
    if cng.CHECK_GWEI:
        EVM.check_gwei()
    try:
        with Pool(cng.THREAD) as pols:
            pols.map(lambda func: WorkZora(func), private)
    except BaseException as error:
        log().error(error)


if __name__ == '__main__':
    main()






