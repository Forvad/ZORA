import random
import time

from web3 import Web3
from Utils.EVMutils import EVM
from Abi.abi import open_abi
from config import RETRY


def holograph(private_key: str, retry=0) -> None:
    address_contract = Web3.to_checksum_address('0x052790f7f5B15F9a2FA684fd3eCD657e3CD9029c')
    web3 = EVM.web3('zora')
    contract = web3.eth.contract(address=address_contract, abi=open_abi()['Holograph_abi'])
    wallet = web3.eth.account.from_key(private_key).address
    module_str = f'Mint Holograph Chain -> Zora, address -> {wallet}'
    value = {'zora': EVM.DecimalFrom(0.000042000000000001, 18)}

    tx = contract.functions.purchase(1).build_transaction({
                                                    'from': wallet,
                                                    'value': value['zora'],
                                                    'chainId': web3.eth.chain_id,
                                                    'gasPrice': Web3.to_wei(0.005, 'gwei'),
                                                    'nonce': web3.eth.get_transaction_count(wallet),
                                                    'gas': 0
                                                    })
    tx_hash = EVM.sending_tx(web3, tx, 'zora', private_key, retry, module_str)
    if not tx_hash:
        if retry < RETRY:
            time.sleep(15)
            return holograph(private_key, retry+1)
    else:
        return

def mint_(private_key):
    EVM.delay_start()
    holograph(private_key)