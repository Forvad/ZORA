import random
import string
import time

import requests
import io

from eth_account import Account

from config import proxy
from requests_toolbelt import MultipartEncoder
from Utils.EVMutils import EVM
from Abi.abi import open_abi
from web3 import Web3
from Log.Loging import log


class AddCollection:
    http_proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy} if proxy != '' else {}

    def __init__(self, private_key):
        self.private_key = private_key
        self.address = Account.from_key(private_key).address
        self.retry = 0

    def upload_ipfs(self, filename, data, ext):
        fields = {
            'file': (filename, io.BytesIO(data), ext),
        }
        boundary = '------WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        m = MultipartEncoder(fields=fields, boundary=boundary)
        resp = requests.post('https://ipfs-uploader.zora.co/api/v0/add?'
                             'stream-channels=true&cid-version=1&progress=false',
                             data=m, headers={'content-type': m.content_type}, proxies=self.http_proxies, timeout=60)
        if resp.status_code != 200:
            raise Exception(f'status_code = {resp.status_code}, response = {resp.text}')
        try:
            return resp.json()['Hash']
        except Exception:
            raise Exception(f'status_code = {resp.status_code}, response = {resp.text}')

    def upload_image_ipfs(self, name):
        img_szs = [i for i in range(500, 1001, 50)]
        url = f'https://picsum.photos/{random.choice(img_szs)}/{random.choice(img_szs)}'
        resp = requests.get(url, proxies=self.http_proxies, timeout=60)
        if resp.status_code != 200:
            raise Exception(f'Get random image failed, status_code = {resp.status_code}, response = {resp.text}')
        filename = name.replace(' ', '_').lower() + '.jpg'
        return self.upload_ipfs(filename, resp.content, 'image/jpg')

    @staticmethod
    def generate_name():
        api_url = 'https://api.api-ninjas.com/v1/randomword'
        response = requests.get(api_url, headers={'X-Api-Key': 'Fy+Q8+jgyEkR5DYAvYJb9A==KxPgXK2WbNlE0zOl'})
        if response.status_code == requests.codes.ok:
            res = response.json()['word'].title() + random.choice(['!', '&', '?', '@', '$'])
            return res
        else:
            raise ValueError(f"Error: {response.status_code}, {response.text}")

    @staticmethod
    def generate_description():
        api_url = 'https://api.api-ninjas.com/v1/riddles'
        response = requests.get(api_url, headers={'X-Api-Key': 'Fy+Q8+jgyEkR5DYAvYJb9A==KxPgXK2WbNlE0zOl'})
        if response.status_code == requests.codes.ok:
            return response.json()[0]["question"]
        else:
            raise ValueError(f"Error: {response.status_code}, {response.text}")

    def get_image_uri(self, name):
        return 'ipfs://' + self.upload_image_ipfs(name)

    @staticmethod
    def to_bytes(hex_str):
        return Web3.to_bytes(hexstr=hex_str)

    def create_collection(self):
        web3 = EVM.web3('zora')
        contract = web3.eth.contract('0xA2c2A96A232113Dd4993E8b048EEbc3371AE8d85', abi=open_abi()['abi_Create_Collection'])
        name = self.generate_name()
        symbol = name[:3].upper()
        description = self.generate_description()
        price = 0
        edition_size = 2 ** 64 - 1
        royalty = 0
        merkle_root = '0x0000000000000000000000000000000000000000000000000000000000000000'
        sale_config = (price, 2 ** 32 - 1, int(time.time()), 2 ** 64 - 1, 0, 0, self.to_bytes(merkle_root))
        image_uri = self.get_image_uri(name)
        args = (
            name, symbol,
            edition_size, royalty,
            self.address, self.address,
            sale_config, description, '', image_uri
        )
        tx = contract.functions.createEdition(*args).build_transaction({
                                                        'from': self.address,
                                                        'chainId': web3.eth.chain_id,
                                                        'gasPrice': Web3.to_wei(0.005, 'gwei'),
                                                        'nonce': web3.eth.get_transaction_count(self.address),
                                                        'gas': 0
                                                        })
        module_str = f'Zora create collection | {self.address}'
        tx_bool = EVM.sending_tx(web3, tx, 'zora', self.private_key, self.retry, module_str)
        if not tx_bool:
            self.retry += 1
            time.sleep(15)
            return self.create_collection()
        else:
            try:
                collection_address = self.wait_recently_created_collection()
                self.admin_mint(web3, collection_address)
            except BaseException as error:
                log().error(f'{error}')
            return True

    def get_created_erc721_zora_collections(self, timestamp_from=None):
        body = {
            'operationName': 'userCollections',
            'query': 'query userCollections($admin: Bytes!, $offset: Int!, $limit: Int!, $contractStandards: [String!] = [\"ERC1155\", \"ERC721\"], $orderDirection: OrderDirection! = desc) {\n  zoraCreateContracts(\n    orderBy: createdAtBlock\n    orderDirection: $orderDirection\n    where: {permissions_: {user: $admin, isAdmin: true}, contractStandard_in: $contractStandards}\n    first: $limit\n    skip: $offset\n  ) {\n    ...Collection\n  }\n}\n\nfragment Collection on ZoraCreateContract {\n  id\n  address\n  name\n  symbol\n  owner\n  creator\n  contractURI\n  contractStandard\n  contractVersion\n  mintFeePerQuantity\n  timestamp\n  metadata {\n    ...Metadata\n  }\n  tokens {\n    ...Token\n  }\n  salesStrategies {\n    ...SalesStrategy\n  }\n  royalties {\n    ...Royalties\n  }\n  txn {\n    ...TxnInfo\n  }\n}\n\nfragment Metadata on MetadataInfo {\n  name\n  description\n  image\n  animationUrl\n  rawJson\n}\n\nfragment Token on ZoraCreateToken {\n  id\n  tokenId\n  address\n  uri\n  maxSupply\n  totalMinted\n  rendererContract\n  contract {\n    id\n    owner\n    creator\n    contractVersion\n    metadata {\n      ...Metadata\n    }\n  }\n  metadata {\n    ...Metadata\n  }\n  permissions {\n    user\n  }\n  salesStrategies {\n    ...SalesStrategy\n  }\n  royalties {\n    ...Royalties\n  }\n}\n\nfragment SalesStrategy on SalesStrategyConfig {\n  presale {\n    presaleStart\n    presaleEnd\n    merkleRoot\n    configAddress\n    fundsRecipient\n    txn {\n      timestamp\n    }\n  }\n  fixedPrice {\n    maxTokensPerAddress\n    saleStart\n    saleEnd\n    pricePerToken\n    configAddress\n    fundsRecipient\n    txn {\n      timestamp\n    }\n  }\n  redeemMinter {\n    configAddress\n    redeemsInstructionsHash\n    ethAmount\n    ethRecipient\n    isActive\n    saleEnd\n    saleStart\n    target\n    txn {\n      timestamp\n    }\n    redeemMintToken {\n      tokenId\n      tokenType\n      tokenContract\n      amount\n    }\n    redeemInstructions {\n      amount\n      tokenType\n      tokenIdStart\n      tokenIdEnd\n      burnFunction\n      tokenContract\n      transferRecipient\n    }\n  }\n}\n\nfragment Royalties on RoyaltyConfig {\n  royaltyBPS\n  royaltyRecipient\n  royaltyMintSchedule\n}\n\nfragment TxnInfo on TransactionInfo {\n  id\n  block\n  timestamp\n}\n',
            'variables': {
                'admin': self.address.lower(),
                'limit': 36,
                'offset': 0
            }
        }
        resp_raw = requests.post('https://api.goldsky.com/api/public/'
                                 'project_clhk16b61ay9t49vm6ntn4mkz/subgraphs/'
                                 'zora-create-zora-mainnet/stable/gn', json=body, proxies=self.http_proxies)
        if resp_raw.status_code != 200:
            raise Exception(f'status_code = {resp_raw.status_code}, response = {resp_raw.text}')
        try:
            created_list = resp_raw.json()['data']['zoraCreateContracts']
            eligible_addresses = []
            for created in created_list:
                if created['contractStandard'] != 'ERC721':
                    continue
                if timestamp_from and int(created['timestamp']) < timestamp_from:
                    continue
                eligible_addresses.append(created['address'])
            return eligible_addresses
        except Exception as e:
            raise Exception(f'status_code = {resp_raw.status_code}, response = {resp_raw.text}: {str(e)}')

    def wait_recently_created_collection(self):
        wait_time = 0

        while wait_time < 60:

            log().info(f'Create: Waiting for collection creating')
            time.sleep(5)
            wait_time += 5

            try:
                collection_addresses = self.get_created_erc721_zora_collections()
                collection_address = collection_addresses[0] if len(collection_addresses) > 0 else None
            except Exception as e:
                log().error(f'Create: Error getting created collection: {str(e)}')
                continue

            if collection_address:
                collection_link = f'https://zora.co/collect/zora:{collection_address}'
                log().success(f'Create: {collection_link}')
                return collection_address

        return False

    def admin_mint(self, web3, collection_address):
        collection_address = Web3.to_checksum_address(collection_address)
        contract = web3.eth.contract(collection_address, abi=open_abi()['abi_Zora_ERC721'])
        tx = contract.functions.adminMint(self.address, random.randint(1, 3)).build_transaction({
                                                        'from': self.address,
                                                        'chainId': web3.eth.chain_id,
                                                        'gasPrice': Web3.to_wei(0.005, 'gwei'),
                                                        'nonce': web3.eth.get_transaction_count(self.address),
                                                        'gas': 0
                                                        })
        module_str = f'Zora admin mint collection | {self.address}'
        tx_bool = EVM.sending_tx(web3, tx, 'zora', self.private_key, self.retry, module_str)
        if not tx_bool:
            self.retry += 1
            time.sleep(15)
            return self.create_collection()
        else:
            return True
