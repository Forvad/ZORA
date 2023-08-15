import time

from web3 import Web3
from Utils.EVMutils import EVM
from Abi.abi import open_abi
from config import NFT, Amount_nft, amount
from MintFun.Activation import add_point


def mint_nft(private_key: str, nft_adr: str, value: str, numb: list,  retry=0) -> None:
    address_contract = Web3.to_checksum_address(nft_adr)
    web3 = EVM.web3('zora')
    contract = web3.eth.contract(address=address_contract, abi=open_abi()['abi_NFT_allure'])
    wallet = web3.eth.account.from_key(private_key).address
    module_str = f'Mint NFT address -> {wallet}'

    tx = contract.functions.mint(value).build_transaction({
                                                    'from': wallet,
                                                    'chainId': web3.eth.chain_id,
                                                    'gasPrice': Web3.to_wei(0.005, 'gwei'), #web3.eth.gas_price,
                                                    'nonce': web3.eth.get_transaction_count(wallet),
                                                    'gas': 0
                                                    })
    tx_hash = EVM.sending_tx(web3, tx, 'zora', private_key, retry, module_str, numb=numb)
    if not tx_hash:
        time.sleep(15)
        return mint_nft(private_key, nft_adr, value, numb, retry+1)
    time.sleep(5)
    add_point(wallet, tx_hash, nft_adr)


def mint_zora(private_key):
    work_list = NFT.copy()
    if Amount_nft:
        if amount > 0:
            work_list = work_list[:amount]
        else:
            work_list = work_list[amount:]
    for i, adr in enumerate(work_list):
        mint_nft(private_key, adr[0], adr[1], [i+1, len(work_list)])
        time.sleep(EVM.randint_([10, 15]))
