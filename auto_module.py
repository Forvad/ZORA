import time

from main import WorkZora
from Abi.abi import open_abi
from Utils.EVMutils import EVM
import config as cng
from Exchange.OKX import okx_withdraw
from MintFun.Activation import auth
from MintFun.Pass_NFT import mint, mint_season
from multiprocessing.dummy import Pool


class AutoWork(WorkZora):
    def get_mint_pass(self):
        web3 = EVM.web3('ethereum')
        contract_address = web3.to_checksum_address('0x0000000000664ceffed39244a8312bD895470803')
        contract = web3.eth.contract(address=contract_address, abi=open_abi()['abi_Mint_Fun'])
        num = contract.functions.balanceOf(self.address).call()
        if not num:
            print(f'Acc {self.address} no mint mint fun')
            balance, _ = EVM.check_balance(self.private_key, 'ethereum', '')
            if balance < EVM.DecimalTO(5 / EVM.prices_network('ethereum'), 18):
                value = EVM.uniform_(cng.OKX_ETH)
                okx_withdraw(['ethereum'], self.address, value)
                EVM.waiting_coin(self.private_key, 'ethereum', '', value)
            mint(self.private_key)
            for _ in range(10):
                num = contract.functions.balanceOf(self.address).call()
                if num:
                    break
                else:
                    time.sleep(10)
            auth(self.private_key)

    def get_zora(self):
        balance_zora, _ = EVM.check_balance(self.private_key, 'zora', '')
        if not balance_zora:
            balance_eth, _ = EVM.check_balance(self.private_key, 'ethereum', '')
            if balance_eth < EVM.DecimalTO(cng.Value_bridge[0], 18):
                value = EVM.uniform_(cng.OKX_ETH)
                okx_withdraw(['ethereum'], self.address, value)
                EVM.waiting_coin(self.private_key, 'ethereum', '', value)
            self.zora_bridge()
        self.zora_nft()

    def work(self):
        EVM.delay_start()
        self.get_mint_pass()
        self.get_zora()


def main():
    private = EVM.open_private()
    if cng.CHECK_GWEI:
        EVM.check_gwei()

    def work(private_key):
        EVM.delay_start()
        start = AutoWork(private_key)
        start.work()
    # try:
    with Pool(cng.THREAD) as pols:
        pols.map(lambda func: work(func), private)
    # except BaseException as error:
    #     log().error(error)


if __name__ == '__main__':
    main()
