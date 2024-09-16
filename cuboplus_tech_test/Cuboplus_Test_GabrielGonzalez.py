import streamlit as st
import requests
from datetime import datetime, timedelta
#import pandas as pd

# CHECK TX
def validate_address(address):
    url = f"https://mempool.space/api/v1/validate-address/{address}"
    response = requests.get(url)
    data = response.json()
    return data['isvalid']

# ADDRESS TX
def get_transactions(address):
    url = f"https://mempool.space/api/address/{address}/txs"
    response = requests.get(url)
    return response.json()

##### 

def get_balancesMOC(address):
    url = f"https://mempool.space/api/address/{address}"
    response = requests.get(url)
    data = response.json()
    
    # On-chain balance
    on_chain_balance = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
    
    # Mempool balance
    mempool_balance = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
    
    return on_chain_balance, mempool_balance


####


# FILTER TX
def filter_confirmed_transactions(transactions):
    return [tx for tx in transactions if tx['status']['confirmed']]

# GET TX
def filter_transactions_by_time(transactions, days):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    return [tx for tx in transactions if start_time <= datetime.fromtimestamp(tx['status']['block_time']) <= end_time]

# NET BALANCE
def calcular_balance_net(transacciones, address):
    balance_recibido = 0
    balance_gastado = 0

    for tx in transacciones:
        # CHECK (vout) 
        for vout in tx['vout']:
            if vout.get('scriptpubkey_address') == address:
                balance_recibido += vout['value']  

        # CHECK (vin) 
        for vin in tx['vin']:
            if 'prevout' in vin and vin['prevout'].get('scriptpubkey_address') == address:
                balance_gastado += vin['prevout']['value']  # 

    # NET BALANCE 
    balance_neto = balance_recibido - balance_gastado  # Satoshis
    return balance_neto

# FE
st.title("MEMPOOLS REQUEST")
address = st.text_input("BTC ADDRESS:")

if st.button("GO"):
    if address:
        if validate_address(address):
            all_transactions = get_transactions(address)
            confirmed_transactions = filter_confirmed_transactions(all_transactions)
            
            # FILTER TX
            transactions_30_days = filter_transactions_by_time(confirmed_transactions, 30)
            transactions_7_days = filter_transactions_by_time(confirmed_transactions, 7)
            
           
            # CALCULATE BALANCE 30 DAYS
            if transactions_30_days:
                balance_variation_30_days = calcular_balance_net(transactions_30_days, address)
                total_vin_30_days = sum(vin['prevout']['value'] for tx in transactions_30_days for vin in tx['vin'])
                total_vout_30_days = sum(vout['value'] for tx in transactions_30_days for vout in tx['vout'])
                total_vout_same_address_30_days = sum(vout['value'] for tx in transactions_30_days for vout in tx['vout'] if vout.get('scriptpubkey_address') == address)
                total_vout_different_30_days = total_vout_30_days - total_vout_same_address_30_days
                total_fees_30_days = sum(tx['fee'] for tx in transactions_30_days)

            # ONCHAIN AND MEMPOOL
                on_chain_balance, mempool_balance = get_balancesMOC(address)
                
                container = st.container()
                container.subheader("Balance", divider=True)
                container.write(f"On-chain: {on_chain_balance}")
                container.write(f"Mempool: {mempool_balance}")
                
                # Columns
                
                col1, col2 = st.columns(2)
            
                with col1:
                    st.subheader("LAST 30 DAYS:", divider=True)
                    st.write(f"Balance variation: {balance_variation_30_days} SATS")
                    st.write(f"Total VIN: {total_vin_30_days} SATS")
                    st.write(f"Total VOUT: {total_vout_30_days} SATS")
                    st.write(f"Total VOUT to same address: {total_vout_same_address_30_days} SATS")
                    st.write(f"Total VOUT to different address: {total_vout_different_30_days} SATS")
                    st.write(f"Total Fees: {total_fees_30_days} SATS")

                # CALCULATE BALANCE 7 DAYS
            if transactions_7_days:
                balance_variation_7_days = calcular_balance_net(transactions_7_days, address)
                total_vin_7_days = sum(vin['prevout']['value'] for tx in transactions_7_days for vin in tx['vin'])
                total_vout_7_days = sum(vout['value'] for tx in transactions_7_days for vout in tx['vout'])
                total_vout_same_address_7_days = sum(vout['value'] for tx in transactions_7_days for vout in tx['vout'] if vout.get('scriptpubkey_address') == address)
                total_vout_different_7_days = total_vout_7_days - total_vout_same_address_7_days
                total_fees_7_days = sum(tx['fee'] for tx in transactions_7_days)
               
                with col2: 
                    st.subheader("LAST 7 DAYS", divider=True)
                    st.write(f"Balance variation: {balance_variation_7_days} SATS")
                    st.write(f"Total VIN: {total_vin_7_days} SATS")
                    st.write(f"Total VOUT: {total_vout_7_days} SATS")
                    st.write(f"Total VOUT to same address: {total_vout_same_address_7_days} SATS")
                    st.write(f"Total VOUT to different address: {total_vout_different_7_days} SATS")
                    st.write(f"Total Fees: {total_fees_7_days} SATS")
                
                # TX TABLE LAST 30 DAYS
                
                latest_transactions_30_days = transactions_30_days[:50]
                if latest_transactions_30_days:
                    st.write("LAST 30 DAYS:")
                    transaction_data_30_days = []
                    for tx in latest_transactions_30_days:
                        total_vout_tx = sum(vout['value'] for vout in tx['vout'])
                        total_vout_same_address_tx = sum(vout['value'] for vout in tx['vout'] if vout.get('scriptpubkey_address') == address)
                        total_vout_different_tx = total_vout_tx - total_vout_same_address_tx
                        if total_vout_same_address_tx == total_vout_tx:
                            total_vout_different_tx = 0
                        total_vin_tx = sum(vin['prevout']['value'] for vin in tx['vin'])
                        
                        tx_data = {
                            "txid": tx['txid'],
                            "fee": tx['fee'],
                            "block_time": datetime.fromtimestamp(tx['status']['block_time']).strftime('%Y-%m-%d %H:%M:%S'),
                            "Total Vout": total_vout_tx,
                            "Total Vout same address": total_vout_same_address_tx,
                            "Total Vout different": total_vout_different_tx,
                            "Total Vin": total_vin_tx
                        }
                        transaction_data_30_days.append(tx_data)
                    
                    st.table(transaction_data_30_days)
                
               
        else:
            st.write("Invalid address")
    else:
        st.write("Please enter a Bitcoin address")

