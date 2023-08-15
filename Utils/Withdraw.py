import time
import random
from web3 import Web3
from time import sleep


from Log.Loging import log
from random import choice


def search_steable(chain, privat_key):
    if chain == 'bsc':
        balance_BUSD = us.check_balance(privat_key, chain, us.BUSD_CONTRACT)
    else:
        balance_BUSD = 0
    if chain in ['bsc', 'polygon', 'avalanche', 'arbitrum', 'optimism']:
        balance_BTC = us.check_balance(privat_key, chain, us.ADRES_BTC_b[chain])
    else:
        balance_BTC = 0
    balance_USDC = us.check_balance(privat_key, chain, us.USDC_CONTRACTS[chain])
    balance_USDT = us.check_balance(privat_key, chain, us.USDT_CONTRACTS[chain])
    return balance_USDC, balance_USDT, balance_BUSD, balance_BTC


def calculation_value(token_name, private_key, chain, contact):
    if Withdraw_steable and token_name and chain in Network_remainder:
        keep_value = round(random.uniform(Value_Withdraw_steable[0], Value_Withdraw_steable[1]), 2)
    elif Withdraw_native and not token_name and chain in Network_remainder:
        keep_value = round(random.uniform(Value_Withdraw_native[0], Value_Withdraw_native[1]), 2)
    elif token_name == 'stg':
        keep_value = random.randint(STG_token_value[0], STG_token_value[1])
    else:
        keep_value = 0
    value = us.check_balance(private_key, chain, contact[token_name])
    if token_name:
        if keep_value:
            _, decimal, _ = us.check_data_token(chain, contact[token_name])
            keep_value = us.intToDecimal(keep_value, decimal)
        if keep_value < value:
            value = int(value - keep_value)
            return value
        else:
            return False
    else:
        keep_value = us.intToDecimal(keep_value / us.get_prices(chain), 18)
        if keep_value < value:
            value = int(value - keep_value)
            if chain == 'coredao':
                if value > us.intToDecimal(0.1 / 0.8, 18):
                    return int(value - us.intToDecimal(us.uniform_([0.05, 0.07]), 18))
                else:
                    return False
            elif value > us.intToDecimal(0.1 / us.get_prices(chain), 18):
                return value
            else:
                return False
        else:
            return False


def execution_order(private_key: str, networks: list) -> None:
    no_native = []
    for network in networks:
        limit = us.intToDecimal(0.3 / us.get_prices(network), 18)
        balance_network = us.check_balance(private_key, network, '')
        if balance_network < limit:
            balance_USDC, balance_USDT, balance_BUSD, balance_BTC = search_steable(network, private_key)
            _, decimal_steab, _ = us.check_data_token(network, us.USDT_CONTRACTS[network])
            limit_steable = us.intToDecimal(0.5, decimal_steab)
            limit_btc = us.intToDecimal(0.5 / us.get_prices('btc'), 8)
            if network in ['polygon', 'avalanche', 'fantom']:
                _, decimal_MIM, _ = us.check_data_token(network, us.MIM_CONTARCT[network])
                limit_MIM = us.intToDecimal(0.5, decimal_MIM)
                balance_MIM = us.check_balance(private_key, network, us.MIM_CONTARCT[network])
            else:
                balance_MIM = 0
                limit_MIM = 0
            if balance_MIM > limit_MIM or balance_BTC > limit_btc or balance_BUSD > limit_steable or \
               balance_USDC > limit_steable or balance_USDT > limit_steable:
                no_native.append(network)
    if no_native:
        Bung.witdraw_bridge(private_key, no_native)
        while no_native:
            for chain in no_native:
                balance_native = us.check_balance(private_key, chain, '')
                if balance_native > us.intToDecimal(1 / us.get_prices(chain), 18):
                    no_native.remove(chain)
            sleep(5)


def sell_btc(private_key, chain):
    balance_btc = us.check_balance(private_key, chain, us.ADRES_BTC_b[chain])
    if balance_btc > us.intToDecimal(0.1 / us.get_prices('btc'), 8):
        balance_btc = us.decimalToInt(balance_btc, 8)
        if chain != 'avalanche':
            bridge = BtcBridge(private_key, chain, 'avalanche', balance_btc)
            bridge.bridge()
            us.waiting_coin(private_key, 'avalanche', us.ADRES_BTC_b['avalanche'], balance_btc)
        coin = choice(['usdt', 'usdc'])
        Swap_BTC.swap_btc(balance_btc, private_key, coin)
        waiting_balance = balance_btc * us.get_prices('btc')
        us.waiting_coin(private_key,
                        'avalanche',
                        us.USDT_CONTRACTS['avalanche'] if coin == 'usdt' else us.USDC_CONTRACTS['avalanche'],
                        waiting_balance)


def swap_steable_natyve(private_key, chain, name_token):
    def search_(coin: (str, list)) -> str or list:
        token_adress = {'usdt': us.USDT_CONTRACTS[chain],
                        'busd': us.BUSD_CONTRACT,
                        'busdH': '0x1aa1f7815103c0700b98f24138581b88d4cf9769',
                        'mim': us.MIM_CONTARCT[chain],
                        'usdc': us.USDC_CONTRACTS[chain],
                        '': '',
                        'one': us.ONE_BSC}
        if isinstance(coin, list):
            balance = []
            for i in coin:
                if not i:
                    decimal = 18
                else:
                    _, decimal, _ = us.check_data_token(chain, token_adress[i])
                balance_ = us.check_balance(private_key, chain, token_adress[i])
                balance.append(us.decimalToInt(balance_, decimal))
            return balance
        else:
            if not coin:
                decimal = 18
            else:
                _, decimal, _ = us.check_data_token(chain, token_adress[coin])
            balance_ = us.check_balance(private_key, chain, token_adress[coin])
            return us.decimalToInt(balance_, decimal)

    balance_steable = search_(name_token) - 0.01
    balance_native = search_('')
    if balance_steable > 0.1:
        swap = SwapX0(private_key, chain, name_token, "", balance_steable, 'w')
        balance_serach = balance_native + balance_steable / us.get_prices(chain)
        swap.swap()
        us.waiting_coin(private_key, chain, '', balance_serach)


def withdrawal_token(privatekey: str, to_address: str, numb: int, mode_stg=False, mode_core=False, retry=0) -> None:
    us.delay_start()
    web3 = us.get_web3('bsc')
    wallet = web3.eth.account.from_key(privatekey).address
    log().info(f'>>>>> Withdrawal of wallet tokens {wallet} № {numb} <<<<<')
    if mode_core:
        NET_Withdraw = ['bsc', 'coredao']
    else:
        NET_Withdraw = NETWORK_Withdraw.copy()
    if NET_Withdraw and not mode_core:
        execution_order(privatekey, NETWORK_Withdraw)
        random.shuffle(NET_Withdraw)
    if 'avalanche' in NET_Withdraw:
        NET_Withdraw.remove('avalanche')
        NET_Withdraw.append('avalanche')
    for chain in NET_Withdraw:
        try:
            web3 = us.get_web3(chain)
            tokens = {'polygon': ['stg', 'mim', 'btc', 'usdc', 'usdt', ''],
                      'bsc': ['stg', 'btc', 'busd', 'usdt', ''],
                      'arbitrum': ['stg', 'btc', 'usdc', 'usdt', ''],
                      'optimism': ['stg', 'btc', 'usdc', 'usdt', ''],
                      'avalanche': ['stg', 'mim', 'btc', 'usdc', 'usdt',  ''],
                      'fantom': ['stg', 'mim', 'usdc', 'usdt',  ''],
                      'coredao': ['']}

            contact = {'': '',
                       'usdc': us.USDC_CONTRACTS[chain],
                       'usdt': us.USDT_CONTRACTS[chain],
                       'busd': us.BUSD_CONTRACT,
                       'btc': us.ADRES_BTC_b[chain],
                       'stg': us.STG_token_contract[chain]
                       }

            for token in tokens[chain]:
                if token == 'btc':
                    sell_btc(privatekey, chain)
                elif token == 'stg' and mode_stg:
                    pass
                elif token == 'mim':
                    swap_steable_natyve(privatekey, chain, token)
                elif chain in ['bsc', 'fantom'] and token in ['busd', 'usdt', 'usdc'] and not config.Hard_Module and\
                        not mode_core:
                    swap_steable_natyve(privatekey, chain, token)
                else:
                    value = calculation_value(token, privatekey, chain, contact)
                    if chain == 'bsc' or not token or token == 'stg':
                        decimal = 18
                    else:
                        decimal = 6
                    if token:
                        limit = us.intToDecimal(0.2, decimal)
                    else:
                        limit = us.intToDecimal(0.2 / us.get_prices(chain), decimal)
                    if value > limit:

                        def transfer_token(web3, values):
                            if not token:
                                contract_txn = {
                                    'from': wallet,
                                    'chainId': web3.eth.chain_id,
                                    'gasPrice': web3.eth.gas_price,
                                    'nonce': web3.eth.get_transaction_count(wallet),
                                    'gas': 0,
                                    'to': Web3.to_checksum_address(to_address),
                                    'value': 0
                                }
                                contract_txn = us.add_gas_limit(web3, contract_txn, privatekey, 'w')
                                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                                if chain in ['arbitrum']:
                                    gas_gas = int(gas_gas + us.intToDecimal(random.uniform(0.07, 0.15)
                                                                            / us.get_prices(chain), 18))
                                elif chain in ['optimism']:
                                    gas_gas = int(gas_gas + us.intToDecimal(random.uniform(0.1, 0.15) /
                                                  us.get_prices(chain), 18))
                                else:
                                    gas_gas = int((contract_txn['gas'] * random.uniform(1.3, 2))
                                                  * contract_txn['gasPrice'])
                                contract_txn['value'] = int(values - gas_gas)
                                contract_txn = us.add_gas_limit(web3, contract_txn, privatekey, "w")
                                symbol = us.DATA[chain]['token']

                            else:

                                token_contract, decimals, symbol = us.check_data_token(chain, contact[token])
                                tx = {
                                    'from': wallet,
                                    'chainId': web3.eth.chain_id,
                                    'gasPrice': web3.eth.gas_price,
                                    'gas': 0,
                                    'nonce': web3.eth.get_transaction_count(wallet),
                                    'value': 0
                                }
                                contract_txn = token_contract.functions.transfer(
                                    Web3.to_checksum_address(to_address),
                                    values
                                ).build_transaction(tx)
                            contract_txn = us.add_gas_limit(web3, contract_txn, privatekey, 'w')
                            if not contract_txn:
                                return withdrawal_token(to_address, privatekey, numb, mode_stg, retry=retry + 1)
                            if CHECK_GASS:
                                total_fee = int(contract_txn['gas'] * contract_txn['gasPrice'])
                                is_fee = us.checker_total_fee(chain, total_fee)
                                if not is_fee:
                                    us.sleeping(30, 30)
                                    return withdrawal_token(to_address, privatekey, numb,  mode_stg, retry=retry + 1)

                            tx_hash = us.sign_tx(web3, contract_txn, privatekey, 'w')
                            if not tx_hash:
                                web3 = us.get_web3(chain)
                                contract_txn['nonce'] = web3.eth.get_transaction_count(wallet)
                                tx_hash = us.sign_tx(web3, contract_txn, privatekey, 'w')
                            tx_link = f'{us.DATA[chain]["scan"]}/{tx_hash}'

                            module_str = f'transfer {wallet} {symbol} => {to_address}'

                            status = us.check_status_tx(chain, tx_hash)
                            if status == 1:
                                log().success(f'{module_str} | {tx_link}')
                                with open(f'Withdraw.txt', 'a', encoding='utf-8') as file:
                                    save = f'{wallet} | {to_address} | {f"Native {chain}" if not token else token}'
                                    file.write(f'{save}\n')
                                return

                            else:
                                if retry < RETRY:
                                    log().error(f'{module_str} | tx is failed, try again in 10 sec | {tx_link}')
                                    us.sleeping(15, 15)
                                    transfer_token(web3, value)
                                else:
                                    log().error(f'{module_str} | tx is failed | {tx_link}')
                        transfer_token(web3, value)
                        sleep(7)

                        balance = us.check_balance(privatekey, chain, contact[token])
                        if token != 'stg':
                            if token:
                                if not Withdraw_steable and balance > us.intToDecimal(0.2, 6):
                                    transfer_token(web3, balance)
                            else:
                                if not Withdraw_native and balance > us.intToDecimal(0.2 / us.get_prices(chain), 18):
                                    transfer_token(web3, balance)
                                elif Withdraw_native and chain in Network_remainder and \
                                        balance > us.intToDecimal(Value_Withdraw_native[1] / us.get_prices(chain), 18):
                                    keep = us.intToDecimal(random.uniform(Value_Withdraw_native[0],
                                                                          Value_Withdraw_native[1])
                                                           / us.get_prices(chain), 18)
                                    balance = balance - keep
                                    transfer_token(web3, balance)

        except ValueError as errors:
            if errors == 'The private kev must be exactly 32 bytes long. instead of 42 bvtes.':
                log().error('Private key error')
                if retry < RETRY:
                    time.sleep(15)
                    return withdrawal_token(to_address, privatekey, retry + 1)
        except WithdrawTokensMM as error:
            log().error(f'An error occurred when withdrawing coins from the EVM address | {error}')
