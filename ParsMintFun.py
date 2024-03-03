from requests import get
from Log.Loging import log
import json


def call_json(results):
    outfile = 'nft_mint'
    with open(f"{outfile}.json", "w") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    nft = get('https://mint.fun/api/mintfun/feed/trending?range=12h').json()
    add_json = {}
    for data_nft in nft['collections']:
        if'7777777' in data_nft['contract']:
            if 'maxSupply' in data_nft:
                if int(data_nft['totalMints']) < int(data_nft['maxSupply']):
                    add_json[data_nft['name']] = data_nft['contract'].replace('7777777:', '')
                else:
                    add_json[data_nft['name']] = data_nft['contract'].replace('7777777:', '')
    call_json(add_json)

            # flag = True
            # for contract in NFT:
            #     if contract[0] == data_nft['contract'].replace("7777777:", ""):
            #         flag = False
            # if flag:
            #     log().info(f"address: {data_nft['contract'].replace('7777777:', '')} name: {data_nft['name']}")
