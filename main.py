import requests
from binance.client import Client
from binance.enums import *
import time
import numpy as np
import talib
import smtplib

#==========================================================================================
try:

    api_key = "Your API Key"
    api_secret = "You API Secret"
    client = Client(api_key, api_secret)

except:

    print("ERROR: Bot Couldnot get access to the Binance Account.")

#=====================================================================================
asset = "ADAUSDT"
pair_asset = "USDT"
time_rest = 3

address = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(asset)

#====================================================================================
candles_closing_list = []
precision= 6
roundup = 2
#==========================================================================================
try:
    receiver_email = "Receiver Email"
    email = "Your Email Address"
    password = "Your Email Password"
    mail = smtplib.SMTP('smtp.gmail.com')
    mail.ehlo()
    mail.starttls()
    mail.login(email,password)
    SUBJECT = "Binance-API"
except:
    print("ERROR: SMTP Service config line error")


#===================================================================================================
#klines = client.get_historical_klines("{}".format(asset), Client.KLINE_INTERVAL_1MINUTE, "27 MAY, 2021", )
#for k in klines:
#    close = float(k[4])
#    candles_closing_list.append(close)

#===================================================================================================
print("Running")

while True:
#=======================================================================================================
    try:
        klines = client.get_historical_klines("{}".format(asset), Client.KLINE_INTERVAL_1MINUTE, "27 MAY, 2021" )

        for k in klines:
            close = float(k[4])
            candles_closing_list.append(close)

    except:
        print("ERROR: Failed to Fetch Historical Data")


    #=========================================================================
    try:
        np_closes = np.array(candles_closing_list)
        rsi_list = talib.RSI(np_closes)
        rsi = 30#int(rsi_list[-1])
        print(rsi)
        candles_closing_list.clear()
    except:
        print("ERROR: RSI could not be Calculated")

    #==========================================================================

    try:
        balance_raw = client.get_asset_balance(asset='{}'.format(pair_asset))
        balance = 20 #balance_raw['free']
        raw_data = requests.get(address).json()
        price = float(raw_data["price"])
        buy_price = price
        sell_price = float(price + 10/100)
        asset_buy_quantity = float(round(balance / buy_price, roundup))
        print(asset_buy_quantity, type(asset_buy_quantity))
    except:
        print("ERROR: Balance, Buy_price, Sell_price Not excecuted.")
    
    #============================================================================

    try:
        status_raw = client.get_system_status()

        for stat, con in status_raw.items():
            connection_status = con
    except:
        print("ERROR: Failed to fetch System Status")

    #============================================================================


    if connection_status == "normal":
        

        #=========================================================================
        try:

            order_status_raw = client.get_open_orders(symbol=asset)
            

            if order_status_raw == [] :

                open_order_status = "null"
            else:
                
                for r in order_status_raw:
                    print(r["side"])
                    open_order_status =  r["side"]

        except:

            print("ERROR: Open_order_status not excecuted")
                    

        #==========================================================================

        if open_order_status == "BUY" or open_order_status == "SELL":
            
            time.sleep(time_rest)
        #=============================================================================

        elif open_order_status == "null":


            if rsi <= 33:
                #=======================================================================

                order = client.create_test_order(
                        symbol='{}'.format(asset),
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity= float(asset_buy_quantity),
                        price="{:0.0{}f}".format(buy_price, precision))
                
                print("{:0.0{}f}".format(buy_price, precision))


                    
                #=======================================================================

                try:

                    bought_quantity_usdt = balance
                    bought_quantity = asset_buy_quantity
                    bought_price = buy_price

                    text = "bought_quantity_usdt:{}\n bought_quantity:{}\n bought_price:{}\n RSI:{}".format(bought_quantity_usdt,bought_quantity, bought_price, rsi)
                    message = 'Subject: {}\n\n{}'.format(SUBJECT, text)
                    mail.sendmail(email,receiver_email,message)

                except :

                    print ("Error: There was an error in sending your BUY email.")
                    time.sleep(time_rest)
                
                #========================================================================

                

                order = client.create_test_order(
                        symbol='{}'.format(asset),
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=float(asset_buy_quantity),
                        price="{:0.0{}f}".format(sell_price, precision))
                

                
                #=======================================================================

                
                try:

                    sold_quantity_usdt = float(asset_buy_quantity * sell_price)
                    profit = float(asset_buy_quantity - (balance/sell_price))
                    sold_quantity = bought_quantity
                    sold_price = sell_price

                    text = "Got_usdt:{}\n sold_quantity:{}\n sold_price:{}\n Profit:{} ".format(sold_quantity_usdt,sold_quantity, sold_price, profit)
                    message = 'Subject: {}\n\n{}'.format(SUBJECT, text)
                    mail.sendmail(email,receiver_email,message)
                    time.sleep(time_rest)

                except :

                    print ("Error: There was an error in sending your SELL email.")
                    time.sleep(time_rest)


                #============================================================================

            else:

                time.sleep(time_rest)
            

        else:

            try:

                text= "ERROR: Open_order_status show no BUY no Sell no null"
                print(text)
                message = 'Subject: {}\n\n{}'.format(SUBJECT, text)
                mail.sendmail(email,receiver_email,message)
                time.sleep(time_rest)

            except:

                print ("Error: There was an error in sending your email.")
                time.sleep(time_rest)


    elif connection_status == "maintanance":

        try:

            text = "System is in Maintanance"
            message = 'Subject: {}\n\n{}'.format(SUBJECT, text)
            mail.sendmail(email,receiver_email,message)
            time.sleep(time_rest)

        except:

            print ("Error: There was an error in sending your email.")
            time.sleep(time_rest)