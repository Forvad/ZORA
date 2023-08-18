import datetime
import time

from eth_account import Account
from pyuseragents import random as random_useragent
from requests import get, Session
from config import proxy
from Utils.EVMutils import EVM
from NFT_Zora.Mint import mint_zora
from Log.Loging import inv_log


def chek_tx(private_key):
    address = Account.from_key(private_key).address

    header = {
               'User-Agent': random_useragent()}
    if proxy:
        session = Session()
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        session.proxies.update(proxies)
        session.headers.update(header)
        nft = session.get(f'https://explorer.zora.energy/api/v2/addresses/{address}/transactions').json()

    else:
        nft = get(f'https://explorer.zora.energy/api/v2/addresses/{address}/transactions', headers=header).json()
    time_last = nft["items"][0]["timestamp"].split("T")[0]
    time_ = str(datetime.datetime.today().strftime("%Y-%m-%d"))
    return time_last == time_


def main():
    inv_log().success('start auto module')
    while True:
        num = 0
        private_key = EVM.open_private()
        for prv in private_key:
            if not chek_tx(prv):
                EVM.check_gwei()
                mint_zora(prv)
            time.sleep(EVM.randint_([60, 120]))
            num += 1
        inv_log().info(f"For this pass , it worked {num}/{len(private_key)} wallets")
        time.sleep(21_600)


if __name__ == "__main__":
    main()
