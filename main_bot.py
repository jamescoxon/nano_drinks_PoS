from sys import argv, exit
import json
import time
from nano25519 import ed25519_oop as ed25519
from jcnanolib import nano
import requests
import settings
import decimal
import logging

decimal.getcontext().prec = 32

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger()

#WHATSAPP
def send_whatsapp(destination_number, message):
    r = requests.post('http://localhost:3000/send-message', json={'number': destination_number, 'text' : message})
    result = r.json()
    logging.info(result)

#NANO
def process_pending(account, index_pos, wallet_seed):
    pending = nano.get_pending(str(account))
#    logging.info("Process Pending: {}".format(pending))
    previous = nano.get_previous(str(account))
#    logging.info(previous)
    if len(pending) > 0:
        pending = nano.get_pending(str(account))
       # try:
        if len(previous) == 0:
            logging.info("Opening Account")
            hash, balance = nano.open_xrb(int(index_pos), account, wallet_seed)
            previous = nano.get_previous(str(account))
        else:
            outcome = 'error'
            rx_attempt = 0
            while 'error' in outcome:
                rx_attempt = rx_attempt + 1
                hash, balance = nano.receive_xrb(int(index_pos), account, wallet_seed)
                if 'error' not in hash:
                    outcome = 'success'

                logging.info('Rx status: {} {}'.format(rx_attempt, outcome))
                time.sleep(1)

        logging.info("Reply {} {}".format(hash, balance))
       # except:
       #     logging.info("Error")
    else:
        return 0


def send_nano(xrb_address, raw_amount, index, dest_account):
    logging.info("Sending Nano...")
    process_pending(xrb_address, index, settings.wallet_seed)

    current_balance = nano.get_account_balance(xrb_address)
    logging.info('{} {}'.format(current_balance, raw_amount))

    if int(current_balance) > 0:
        outcome = 'error'
        send_attempt = 0
        while 'error' in outcome:
            send_attempt = send_attempt + 1
            return_block = nano.send_xrb(dest_account, int(raw_amount), xrb_address, int(index), settings.wallet_seed)

            if 'error' not in return_block:
                outcome = 'success'

            logging.info('Send status: {} {}'.format(send_attempt, outcome))
            time.sleep(1)

        logging.info(return_block)
        return(return_block)

def process_data_success(source_account):
    # Send message to host
    send_whatsapp(settings.host_number, 'BOT: Hi, Nano received, please give the customer the drink, sending your profit direct to your account')

    # Receive Nano
    process_pending(settings.nano_address, settings.index, settings.wallet_seed)

    #Send Nano to host
    logging.info('Sending profit to host')
    raw_amount = 100000000000000000000000000000
    block = send_nano(settings.nano_address, raw_amount, settings.index, settings.host_nano_address)
    logging.info(block)
    if 'error' in block:
        send_whatsapp(settings.debug_number, 'Error Host Send: {}'.format(block))
    else:
        send_whatsapp(settings.host_number, 'BOT: Here is your profit: https://nanolooker.com/block/{}'.format(block['hash']))

    # Send message to rep
    logging.info('Sending cost to rept')
    raw_amount = 100000000000000000000000000000
    block = send_nano(settings.nano_address, raw_amount, settings.index, settings.rep_nano_address)
    logging.info(block)
    if 'error' in block:
        send_whatsapp(settings.debug_number, 'Error Rep Send: {}'.format(block))
    else:
        send_whatsapp(settings.rep_number, 'BOT: Drinks Transaction Complete: https://nanolooker.com/block/{}'.format(block['hash']))

    leftover_balance = decimal.Decimal(nano.get_account_balance(settings.nano_address)) - decimal.Decimal(10000000000)
    logging.info('Remaining Balance: {}'.format(leftover_balance))

    if decimal.Decimal(leftover_balance) > 0:
        logging.info('Returning Spare Funds')
        block = send_nano(settings.nano_address, '{}'.format(leftover_balance), settings.index, source_account)
        logging.info(block)
        if 'error' in block:
            send_whatsapp(settings.debug_number, 'Error Refund: {}'.format(block))

def process_data_failed(amount_raw, source_account):
    # Send message to host
    send_whatsapp(settings.host_number, 'BOT: Not enough Nano for a drink, bot will refund the customer and please get them to try again with the correct amount')

    # Return Nano to sender
    logging.info('Returning funds')
    block = send_nano(settings.nano_address, amount_raw, settings.index, source_account)
    logging.info(block)
    if 'error' in block:
        send_whatsapp(settings.debug_number, 'Error Refund: {}'.format(block))


def main():

    # Check there aren't any spare transactions that might get in the way.
    process_pending(settings.nano_address, settings.index, settings.wallet_seed)

    logging.info('Running...')
    while True:
        pending = nano.get_pending(str(settings.nano_address))
        if len(pending) > 0:
            logging.info(pending)
            process_pending(settings.nano_address, settings.index, settings.wallet_seed)
            block = list(pending)[0]
            logging.info('{}'.format(block))
            amount_raw = pending[block]['amount']
            source_account = pending[block]['source']


            if decimal.Decimal(amount_raw) >= decimal.Decimal(settings.cost_raw):
                process_data_success(source_account)
            else:
                process_data_failed(amount_raw, source_account)

            logging.info('Done')

        time.sleep(5)

if __name__ == "__main__":
    main()
