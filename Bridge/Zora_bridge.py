import time

from Utils.EVMutils import EVM
from web3 import Web3
from Abi.abi import open_abi


class ZoraBridge:
    def __init__(self, private_key, amount):
        self.private_key = private_key
        self.amount = amount
        self.retry = 0

    def bridge(self):
        web3 = EVM.web3('ethereum')
        contract = web3.eth.contract(address=Web3.to_checksum_address('0x1a0ad011913A150f69f6A19DF447A0CfD9551054'),
                                     abi=open_abi()['abi_Zora_Bridge'])
        wallet = web3.eth.account.from_key(self.private_key).address
        module_str = f'Zora Bridge | {wallet} | Ethereum -> Zora'
        l2_value = EVM.DecimalFrom(self.amount, 18)
        base_fee = web3.eth.fee_history(web3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1]
        priority_max = web3.to_wei(0.6, 'gwei')
        tx = contract.functions.depositTransaction(
            wallet,
            l2_value,
            100000,
            False,
            "0x",
        ).build_transaction({
            "value": l2_value,
            'from': wallet,
            # 'gas': 0,
            # 'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
            # 'maxFeePerGas': base_fee + priority_max,
            # 'maxPriorityFeePerGas': priority_max
        })
        tx = EVM.get_gas_prices('ethereum', tx)
        tx_bool = EVM.sending_tx(web3, tx, 'ethereum', self.private_key, self.retry, module_str, sell_add=l2_value)
        if not tx_bool:
            self.retry += 1
            time.sleep(15)
            return self.bridge()
        else:
            return True
