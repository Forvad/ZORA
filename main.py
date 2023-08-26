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
from NFT_Zora.Collection import AddCollection


class WorkZora:
    def __init__(self, private_key):
        self.name_func = {'OKX': self.okx_withdraw, 'Mint_Fun': self.min_fun, 'Zora_Bridge': self.zora_bridge,
                          'Zora_NFT': self.zora_nft, 'Create_Collection': self.create_collection}
        self.private_key = private_key
        self.route = [self.name_func[func] for func in cng.Route]
        self.web3 = EVM.web3('zora')
        self.address = self.web3.eth.account.from_key(self.private_key).address

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
        balance, _ = EVM.check_balance(self.private_key, 'zora', '')
        if balance >= EVM.DecimalFrom(0.5 / EVM.prices_network('zora'), 18):
            mint_zora(self.private_key)
        else:
            log().error(f'Ваш баланс мал {EVM.DecimalTO(balance, 18)} ETH -> {self.address}')

    def create_collection(self):
        add = AddCollection(self.private_key)
        add.create_collection()

    def start_work(self):
        for func in self.route:
            func()


def main():
    private = EVM.open_private()
    if cng.CHECK_GWEI:
        EVM.check_gwei()

    def work(private_key):
        EVM.delay_start()
        start = WorkZora(private_key)
        start.start_work()

    with Pool(cng.THREAD) as pols:
        pols.map(lambda func: work(func), private)


if __name__ == '__main__':
    main()






