import pandas as pd

def trend_following_strategy(data):
    low_price = data['price'].iloc[-1]
    high_price = data['price'].iloc[-1]
    current_price = data['price'].iloc[-1]
    
    current_price = row['price']
    if current_price > high_price:
        high_price = current_price


def run(data):
    for index,row in data[::-1].iterrows():
        trend_following_strategy(row['price'])