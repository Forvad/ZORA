from requests import Session, post
from Log.Loging import log
from pyuseragents import random as random_useragent
import time
from eth_account.messages import encode_defunct
from web3.auto import w3
from eth_account import Account


def auth(private_key):
    time_ = int(time.time())
    address = Account.from_key(private_key).address
    data_sing = f'mint.fun uses this cryptographic signature to verify your ownership of this wallet. Timestamp: {time_}'

    sign = w3.eth.account.sign_message(encode_defunct(text=data_sing), private_key=private_key).signature.hex()
    session = Session()
    session.headers.update({
        'user-agent': random_useragent()})
    json_data = {
                'address': address,
                'message': data_sing,
                'payload': {
                    'timestamp': str(time_)
                },
                'provider': 'MetaMask',
                'signature': sign
                }
    auth_ = session.post('https://mint.fun/api/mintfun/auth', json=json_data).json()
    if "success" in auth_:
        log().success(auth_)
    else:
        log().error(f'error{auth_}')
    session.get(f'https://mint.fun/api/mintfun/fundrop/pass?address={address}')
    time.sleep(1)
    session.get('https://mint.fun/api/mintfun/account')
    time.sleep(1)
    pass_activation(session, address)


def pass_activation(session, address):
    session.get(f'https://mint.fun/api/mintfun/fundrop/pass?address={address}')
    time.sleep(1)
    nonce = session.get('https://mint.fun/api/mintfun/fundrop/fd-extension/nonce').json()["nonce"]
    time.sleep(2)
    json_data = {'nonce': nonce, 'address': address}
    verify = session.post('https://mint.fun/api/mintfun/fundrop/fd-extension/verify-install', json=json_data).json()
    if 'pointsApplied' in verify:
        time.sleep(3)
        info = session.get(f'https://mint.fun/api/mintfun/fundrop/points?address={address}').json()
        log().success(f'Success Activation {info["points"]} potion')
    else:
        log().error(f'error: {verify}')


def add_point(address, hash_tx, contract):
    headers = {
        'authority': 'mint.fun',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,ru-BY;q=0.8,ru-RU;q=0.7,en-US;q=0.6',
        'content-type': 'application/json',
        # 'cookie': 'session=mftok_nRsm5ob2Tq3uB0zQT1a7kFbERZ6kENZy7AU22hLdnVIAcfY5b6N93fW8kOLL',
        'origin': 'https://mint.fun',
        'referer': f'https://mint.fun/zora/{contract}',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': random_useragent(),
    }

    json_data = {
        'address': address,
        'hash': hash_tx,
        'isAllowlist': False,
        'chainId': 7777777,
        'source': 'projectPage',
    }

    post('https://mint.fun/api/mintfun/submit-tx', headers=headers, json=json_data).json()


if __name__ == '__main__':
    pass

