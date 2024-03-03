import random
import time

from Utils.EVMutils import EVM as us
from web3 import Web3
from eth_utils import to_hex
from eth_abi import encode
from Log.Loging import log
from config import RETRY
from Abi.abi import open_abi


class NotNFTWallet(BaseException):
    pass


class BridgeHolograph:
    holograph_id = {'polygon': 4,
                    'avalanche': 3,
                    'bsc': 2}

    gas = {'bsc': 4500000000,
           'avalanche': 37500000000,
           'polygon': 400000000000}

    gas_lim = 397539 #random.randint(390000, 500000)

    def __init__(self, private_key: str):
        self.retry = 0
        self.web3 = us.web3('zora')
        self.private_key = private_key
        self.address = self.web3.eth.account.from_key(self.private_key).address
        self.HolographBridgeAddress = Web3.to_checksum_address('0x8D5b1b160D33ce8B6CAFE2674A81916D33C6Ff0B')
        self.nft_address = Web3.to_checksum_address('0xe428212805d8957f62b1e7e9377152c58c1aad2c')
        self.fee_address = Web3.to_checksum_address('0xb6319cC6c8c27A8F5dAF0dD3DF91EA35C4720dd7')
        self.bridge_nft()

    def check_id_nft(self, chain):
        web3 = us.web3(chain)
        address_contract = web3.to_checksum_address(self.nft_address)
        contract = web3.eth.contract(address=address_contract, abi=open_abi()['Holograph_abi'])
        balance = contract.functions.balanceOf(self.address).call()
        if balance:
            id_nft = contract.functions.tokensOfOwner(self.address).call()[0]
            return id_nft
        else:
            return False

    def fee_nft_bridge(self, chain, to_chain):
        w3 = us.web3(chain)

        Fee = w3.eth.contract(address=self.fee_address, abi=open_abi()['Holo_fee_abi'])
        holo_adr = Web3.to_checksum_address('0x8D5b1b160D33ce8B6CAFE2674A81916D33C6Ff0B')
        lzFee = Fee.functions.estimateFees(us.LAYERZERO_CHAINS_ID[to_chain], holo_adr, '0x', False, '0x').call()[0]
        return int(lzFee * 2)

    def bridge_nft(self):
        us.delay_start()
        # try:
        network_work = ['zora']
        # to_network = ['polygon', 'base', 'mantle']
        random.shuffle(network_work)
        network_from = 'zora'
        nft_id = self.check_id_nft('zora')
        if not nft_id:
            log().error(f"Don't be naughty on the NFT balance - {self.address}")
            return
        network_work.remove(network_from)
        web3 = us.web3(network_from)
        balance, _ = us.check_balance(self.private_key, network_from, '')
        to_chain = 'polygon'

        contract = web3.eth.contract(address=self.HolographBridgeAddress, abi=open_abi()['Holo_abi'])
        to_id = self.holograph_id[to_chain]
        gas_price = self.gas[to_chain]
        payload = to_hex(encode(['address', 'address', 'uint256'], [self.address, self.address, nft_id]))
        fee = self.fee_nft_bridge(network_from, to_chain)
        if balance < us.DecimalTO(1 / us.prices_network(network_from), 18) + fee:
            return
        tx = contract.functions.bridgeOutRequest(to_id, self.nft_address, self.gas_lim, gas_price, payload).\
            build_transaction({
                               'from': self.address,
                               'nonce': web3.eth.get_transaction_count(self.address),
                               'chainId': web3.eth.chain_id,
                               'value': fee,
                               'gasPrice': Web3.to_wei(0.005, 'gwei'),
                               'gas': 0
                            })
        module_str = f'Holograph Bridge NFT from {network_from} to {to_chain} address - {self.address}'
        tx_hash = us.sending_tx(web3, tx, 'zora', self.private_key, self.retry, module_str, add_buy=True)
        if not tx_hash:
            if self.retry < RETRY:
                time.sleep(15)
                return self.bridge_nft()
        else:
            return
        # except Exception as error:
        #     log().error(f'Bridge NFT | error : {error}')
        #     if self.retry < RETRY:
        #         log().info(f'try again in 10 sec.')
        #         time.sleep(15)
        #         self.retry += 1
        #         self.bridge_nft()
