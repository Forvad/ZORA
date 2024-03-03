import time
import json

from web3 import Web3
from Utils.EVMutils import EVM
from Abi.abi import open_abi
from config import amount, RETRY
from MintFun.Activation import add_point
from requests import get
from random import shuffle
from web3.exceptions import ContractLogicError
from Log.Loging import inv_log


def mint_nft(private_key: str, nft_adr: str, numb: list, name: str,  retry=0) -> None:

        address_contract = Web3.to_checksum_address(nft_adr)
        web3 = EVM.web3('zora')
        contract = web3.eth.contract(address=address_contract, abi=open_abi()['abi_NFT_allure'])
        wallet = web3.eth.account.from_key(private_key).address
        module_str = f'Mint {name} -> {wallet}'
        # try:
        #     value = check_fee_nft(address_contract)
        #     tx = contract.functions.mint(value).build_transaction({
        #         'from': wallet,
        #         'chainId': web3.eth.chain_id,
        #         'gasPrice': Web3.to_wei(0.005, 'gwei'),  # web3.eth.gas_price,
        #         'nonce': web3.eth.get_transaction_count(wallet),
        #         'gas': 0
        #     })
        #     tx_hash = EVM.sending_tx(web3, tx, 'zora', private_key, retry, module_str, numb=numb)
        #     if not tx_hash:
        #         if retry < RETRY:
        #             time.sleep(15)
        #             return mint_nft(private_key, nft_adr, numb, retry + 1)
        #     else:
        #         time.sleep(5)
        #         add_point(wallet, tx_hash, nft_adr)
        # except ContractLogicError as error:
        #     inv_log().error(f'error: {error}, contract: {nft_adr}')
        tx = {
            'data': '0xa0712d68000000000000000000000000000000000000000000000000000000000000000a0021fb3f',
            'from': wallet,
            'to': Web3.to_checksum_address(nft_adr),
            'chainId': web3.eth.chain_id,
            'gasPrice': Web3.to_wei(0.005, 'gwei'),  # web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
            'gas': 0
        }
        tx_hash = EVM.sending_tx(web3, tx, 'zora', private_key, retry, module_str, numb=numb)
        if not tx_hash:
            if retry < RETRY:
                time.sleep(15)
                return mint_nft(private_key, nft_adr, numb, retry + 1)
        else:
            time.sleep(5)
            add_point(wallet, tx_hash, nft_adr)




def check_fee_nft(address):
    address_contract = Web3.to_checksum_address(address)
    web3 = EVM.web3('zora')
    contract = web3.eth.contract(address=address_contract, abi=open_abi()['abi_NFT_allure'])
    fee_amount = contract.functions.FREE_SUPPLY().call()
    return int(fee_amount)


def call_json(results):
    outfile = 'nft_mint'
    with open(f"{outfile}.json", "w") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)


def mint_nft_json() -> dict:
    with open('nft_mint.json', 'r') as file:
        return json.loads(file.read())


def pars_nft():
    nft = get('https://mint.fun/api/mintfun/feed/trending?range=12h').json()
    add_json = {}
    for data_nft in nft['collections']:
        if '7777777' in data_nft['contract']:
            if 'maxSupply' in data_nft:
                if int(data_nft['totalMints']) < int(data_nft['maxSupply']):
                    add_json[data_nft['name']] = data_nft['contract'].replace('7777777:', '')
                else:
                    add_json[data_nft['name']] = data_nft['contract'].replace('7777777:', '')
    call_json(add_json)


def chek_nft(private_key):
    pars_nft()
    web3 = EVM.web3('zora')
    nft_dict = mint_nft_json()
    list_nft = []
    if nft_dict:
        for name_nft, address_nft in nft_dict.items():
            address = web3.eth.account.from_key(private_key).address
            contract_address = web3.to_checksum_address(address_nft)
            contract = web3.eth.contract(address=contract_address, abi=open_abi()['abi_NFT_allure'])
            num = contract.functions.balanceOf(address).call()
            if not num:
                list_nft.append([address_nft, name_nft])
        return list_nft


def mint_zora(private_key):
    work_list = chek_nft(private_key)
    if work_list:
        shuffle(work_list)
        if amount < len(work_list):
            work_list = work_list[:amount]

        for i, adr in enumerate(work_list):
            mint_nft(private_key, adr[0], [i+1, len(work_list)], adr[1])
            time.sleep(EVM.randint_([10, 15]))
