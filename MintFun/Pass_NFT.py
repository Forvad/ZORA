import json

import requests
from Utils.EVMutils import EVM
from Abi.abi import open_abi
from pyuseragents import random as random_useragent
from Log.Loging import log
from config import Refferel
from MintFun.Activation import signatures, add_point


def get_sign(main_address: str, referrer: str):
    while True:
        try:
            url = f'https://mint.fun/api/mintfun/fundrop/mint?address={main_address}&referrer={referrer}'

            headers ={
                'User-Agent': random_useragent(),
                'Referer': f'https://mint.fun/fundrop?ref={referrer}',
            }

            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                a = json.loads(resp.text)
                sign = a['signature']
                return sign
        except Exception:
            log().info("Shit go wrong")


def mint_season(private_key):

    web3 = EVM.web3('ethereum')
    address = web3.eth.account.from_key(private_key).address
    contract_address = web3.to_checksum_address('0xfFFffffFB9059A7285849baFddf324e2c308c164')
    contract = web3.eth.contract(address=contract_address, abi=open_abi()['abi_Season_Nft'])

    # Fetch a link but don't increment the counter yet

    data = signatures(private_key)
    base_fee = web3.eth.fee_history(web3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1]
    priority_max = web3.to_wei(0.6, 'gwei')
    # print(data['tokens'], data['amounts'], data['round'])
    tx = contract.functions.mint(data['tokens'], data['amounts'], data['round'], data['signature']).\
        build_transaction({
                            'from': address,
                            'nonce': web3.eth.get_transaction_count(address),
                            # 'gasPrice': web3.eth.gas_price,
                            # 'gas': 0,
                            # 'maxFeePerGas': base_fee + priority_max,
                            # 'maxPriorityFeePerGas': priority_max,
                        })
    module_str = 'Mint Season NFT'
    tx = EVM.get_gas_prices('ethereum', tx)
    print(tx)
    tx = EVM.sending_tx(web3, tx, 'ethereum', private_key, 0, module_str)
    if not tx:
        mint(private_key)
    else:
        add_point(address, tx, contract_address)
        return


def mint(private_key):
    web3 = EVM.web3('ethereum')
    address = web3.eth.account.from_key(private_key).address
    contract_address = web3.to_checksum_address('0x0000000000664ceffed39244a8312bD895470803')
    contract = web3.eth.contract(address=contract_address, abi=open_abi()['abi_Mint_Fun'])

    # Fetch a link but don't increment the counter yet

    referrer = web3.to_checksum_address(Refferel)
    signature = get_sign(address, referrer)
    # base_fee = web3.eth.fee_history(web3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1]
    # priority_max = web3.to_wei(0.6, 'gwei')

    tx = contract.functions.mint(referrer, signature).build_transaction({
        'from': address,
        'nonce': web3.eth.get_transaction_count(address),
        'gasPrice': web3.eth.gas_price,
        'gas': 0
        # 'maxFeePerGas': base_fee + priority_max,
        # 'maxPriorityFeePerGas': priority_max,
    })
    module_str = 'Mint FunPass'
    tx = EVM.get_gas_prices('ethereum', tx)
    tx = EVM.sending_tx(web3, tx, 'ethereum', private_key, 0, module_str)
    if not tx:
        mint(private_key)
    else:
        return

