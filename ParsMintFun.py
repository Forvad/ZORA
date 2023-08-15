from requests import get
from Log.Loging import log
from config import NFT


if __name__ == '__main__':
    nft = get('https://mint.fun/api/mintfun/feed/trending?range=12h').json()
    for data_nft in nft['collections']:
        if'7777777' in data_nft['contract']:
            flag = True
            for contract in NFT:
                if contract[0] == data_nft['contract'].replace("7777777:", ""):
                    flag = False
            if flag:
                log().info(f"address: {data_nft['contract'].replace('7777777:', '')} name: {data_nft['name']}")
