import numpy as np
import pandas as pd
import os

class trading_strategy:
    def __init__(self,initial_cash):
        self.shares = 0
        self.current_market_value = 0
        self.cash = initial_cash
        self.price = 0
        
        self.enter_price = 0
        self.trailing_low = 0
        self.trailing_high = 0
        
        self.history_price = np.array([])
    
    def balance(self):
        return self.cash + self.current_market_value
        
    def update_price(self,price):
        self.price = price
        self.current_market_value = self.shares*price
        
    def adjust_positions_to(self,shares):
        self.close_position()
        self.shares = shares
        self.cash = self.cash - self.shares*self.price
        self.update_price(self.price)
        
    def close_position(self):
        self.cash = self.balance()
        self.current_market_value = 0
        self.shares = 0
    
    def empty_history_price(self):
        self.history_price = np.array([self.history_price[-1]])
        
    def __str__(self):
        return """
                shares = %s
                current_market_value = %s
                cash = %s
                price = %s
                balance = %s
                """ % ( self.shares,
                        self.current_market_value,
                        self.cash,
                        self.price,
                        self.balance())


class trend_following_strategy(trading_strategy):
    def new_day(self,new_price,scale=0.01):
        self.history_price = np.append(self.history_price,new_price)
        self.update_price(new_price)
        if (new_price >= self.history_price.min()*(1+scale)) and (self.history_price[-1] >= self.history_price.min()*(1+scale)):
            self.empty_history_price()
            self.adjust_positions_to(int(self.balance()*0.7/new_price))
        elif (new_price <= self.history_price.max()*(1-scale)) and (self.history_price[-1] <= self.history_price.max()*(1-scale)):
            self.empty_history_price()
            self.adjust_positions_to(int(-self.balance()*0.5/new_price))
        return self.balance()
        
            

class mean_reverse_strategy(trading_strategy):
    pass


def run(data):    
    trend = trend_following_strategy(10000)
    for index,row in data[::-1].iterrows():
        res = trend.new_day(row['price'])
        if index%100 == 0:
            print(res)
        
        
if __name__ == '__main__':
    data = pd.read_csv(os.getcwd() + '\\goldData.csv')
    run(data)
    
    