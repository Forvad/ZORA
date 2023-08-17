import json

import requests
from Utils.EVMutils import EVM
from Abi.abi import open_abi
from pyuseragents import random as random_useragent
from Log.Loging import log
from config import Refferel


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


def mint(private_key):

    web3 = EVM.web3('ethereum')
    address = web3.eth.account.from_key(private_key).address
    contract_address = web3.to_checksum_address('0x0000000000664ceffed39244a8312bD895470803')
    contract = web3.eth.contract(address=contract_address, abi=open_abi()['abi_Mint_Fun'])

    # Fetch a link but don't increment the counter yet

    referrer = web3.to_checksum_address(Refferel)
    signature = get_sign(address, referrer)

    tx = contract.functions.mint(referrer, signature).build_transaction({
        'from': address,
        'nonce': web3.eth.get_transaction_count(address),
        'gasPrice': web3.eth.gas_price,
        'gas': 0
    })
    module_str = 'Mint FunPass'
    EVM.sending_tx(web3, tx, 'ethereum', private_key, 0, module_str)
