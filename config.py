# ======================================================================================#
# =================| Общие настройки модулей |==========================================#
# ======================================================================================#

RETRY = 3  # кол-во попыток при ошибках/фейлах
THREAD = 3  # кол-во потоков

# если газ за транзу с этой сети будет выше в $, тогда скрипт будет спать 30с и пробовать снова
CHECK_GASS = True

MAX_GAS_CHARGE = {
    'ethereum': 5,
    'zora': 1

}

CHECK_GWEI = True  # перед работай чекает GWEI, если выше ожидаем GWEI

GWEI = 30

# ======================================================================================#
# =================|  Creating a route |========================================================#
# ======================================================================================#
# Составление маршрута скрипта
# Все настройки ниже

# OKX - вывод ETH с OKX

# Mint_Fun - Минт Passa и дальнейшая авторизая на сайте для создания очков (https://mint.fun/)

# Zora_Bridge - Основной бридж сети Zora (https://bridge.zora.energy/)

# Zora_NFT - Минт нфт зора по мере их появления будут добавляться(которые мы минтим на данный момент ниже в конифге)

Route = ['Zora_NFT']






# ======================================================================================#
# =================|  Mint_Fun |========================================================#
# ======================================================================================#

Refferel = ''  # address referal


# ======================================================================================#
# =================|  OKX |========================================================#
# ======================================================================================#


OKX_api_key = ''
OKX_secret_key = ''
OKX_password = ''

OKX_ETH = [0.017, 0.018]  # Вывод ETH в сеть эфира( ETH ERC20 min 0.01 ETH)


# ======================================================================================#
# =================| Zora_Bridge |========================================================#
# ======================================================================================#

Value_bridge = [0.014, 0.014]  # объём бриджа в эфире (всё не выводим оствляем на комсу)


# ======================================================================================#
# =================| Zora_NFT |========================================================#
# ======================================================================================#
Amount_nft = True
amount = -2


# Allure, A Great Day, Munris NFT', Fla
# [contract, value]
NFT = [['0x53cb0B849491590CaB2cc44AF8c20e68e21fc36D', 3], ['0x4de73D198598C3B4942E95657a12cBc399E4aDB5', 1],
       ["0xDcFB6cB9512E50dC54160cB98E5a00B3383F6A53", 100], ["0x9eAE90902a68584E93a83D7638D3a95ac67FC446", 3],
       ["0x266b7E8Df0368Dd4006bE5469DD4EE13EA53d3a4", 3], ["0xCc4FF6BB314055846e46490B966745E869546B4a", 100],
       ["0x12B93dA6865B035AE7151067C8d264Af2ae4be8E", 10], ["0x4073a52A3fc328D489534Ab908347eC1FcB18f7f", 3],
       ["0xC47ADb3e5dC59FC3B41d92205ABa356830b44a93", 2], ["0xca5F4088c11B51c5D2B9FE5e5Bc11F1aff2C4dA7", 2]]


