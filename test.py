import time

from requests import get, post
from pyuseragents import random as random_useragent
from eth_account import Account


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

    r = post('https://mint.fun/api/mintfun/submit-tx', headers=headers, json=json_data).json()

    return r


if __name__ == '__main__':
    private = ["34c0df06cb17726584d389829a51a6c46e2747ba57903489b4f5045e1c4b7bcb",
                "b54b0938a4d3c0f5d6219f60bb60effc3761015dcc1e8f75485f7891252de945",
                "8245640ef1519221f04bc7ee98f23bb5a876aaf97a6361776df645b65e4a84ac",
                "4afad88ced41ff0807379471194e35223d3730feba45aff46a9003fd7cbadc33",
                "66b38521b5ebbe759b6935cc5551a5125e1028656d0057f1d86351ca30b54121"]
    for prv in private:
        address = Account.from_key(prv).address

        header = {
                   'User-Agent': random_useragent()}
        nft = get(f'https://explorer.zora.energy/api/v2/addresses/{address}/transactions', headers=header).json()
        for i in nft["items"]:
            if address.lower() != i["to"]["hash"].lower():
                res = add_point(address, i['hash'], i["to"]["hash"])
                print(f'{address} -> {i["to"]["hash"]} -> {res}')
                time.sleep(3)

