import numpy as np
import pandas as pd
import os

class trading_strategy:
    def __init__(self,initial_cash):
        self.start = initial_cash
        self.shares = 0
        self.current_market_value = 0
        self.cash = initial_cash
        self.price = 0
        
        self.enter_price = 0
        self.trailing_low = 0
        self.trailing_high = 0
        
        self.prices = np.array([])
        self.history_balance = np.array([])
    
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
    def __init__(self,initial_cash):
        trading_strategy.__init__(self,initial_cash)
        self.days = np.array([])
        self.scale = np.array([])
        self.long_percent = np.array([])
        self.short_percent = np.array([])
        self.dates = np.array([])
        self.positions = np.array([])
        self.is_trade = np.array([])
        self.history_price = np.array([])

    
    def new_day(self,new_price,new_date,scale=0.03,days=3,long_percent=0.9,short_percent=0.9):
        self.history_price = np.append(self.history_price,new_price)
        self.update_price(new_price)
        #if (new_price >= self.history_price.min()*(1+scale)) and (self.history_price[-1] >= self.history_price.min()*(1+scale)):
        if len(self.history_price[-days:][self.history_price[-days:] > self.history_price.min() * (1 + scale)]) == 3:
            self.empty_history_price()
            self.adjust_positions_to(int(self.start*long_percent/new_price))
        elif len(self.history_price[-days:][self.history_price[-days:] < self.history_price.max() * (1 - scale)] == 3):
            self.empty_history_price()
            self.adjust_positions_to(int(-self.start*short_percent/new_price))
        
        self.run_stats(days,scale,long_percent,short_percent,new_date,new_price)
        
        return self.balance()
        
    def run_stats(self,days,scale,long_percent,short_percent,new_date,new_price):
        self.history_balance = np.append(self.history_balance,self.balance())
        self.days = np.append(self.days,days)
        self.scale = np.append(self.scale,scale)
        self.long_percent = np.append(self.long_percent,long_percent)
        self.short_percent = np.append(self.short_percent,short_percent)
        self.dates = np.append(self.dates,new_date)
        self.positions = np.append(self.positions,self.shares)
        self.prices = np.append(self.prices,new_price)
        if len(self.positions) >= 2:
            if self.positions[-1] == self.positions[-2]:
                self.is_trade = np.append(self.is_trade,0)
            else:
                self.is_trade = np.append(self.is_trade,1)
        else:
            self.is_trade = np.append(self.is_trade,0)
    
    def show_stats(self):
        biggest_drawdown = 0
        biggest_gain = 0
        for i in range(len(self.history_balance)):
            for j in range(i+1,len(self.history_balance)):
                diff = self.history_balance[j] - self.history_balance[i] 
                if diff > biggest_gain:
                    biggest_gain = diff
                elif diff < biggest_drawdown:
                    biggest_drawdown = diff
        
        return [self.dates[0],
                self.dates[-1],
                self.days.mean(),
                self.long_percent.mean(),
                self.short_percent.mean(),
                self.history_balance[-1]/self.history_balance[0],
                len(self.history_balance),
                biggest_drawdown,
                biggest_gain,
                self.is_trade.sum(),
                self.history_balance[0],
                self.history_balance[-1]]
        
    def save_stats(self):
        df = pd.DataFrame(self.dates,columns=['dates'])
        for i in [[self.prices,'prices'],
                  [self.positions,'positions'],
                  [self.is_trade,'is_trade'],
                  [self.history_balance,'history_balance']]:
            df = df.merge(pd.DataFrame(i[0],columns=[i[1]]),left_index=True,right_index=True)
        return df
            

class mean_reverse_strategy(trading_strategy):
    pass


def one_iteration(data,scale=0.01,days=3,long_percent=0.8,short_percent=0.8):  
    """
        outbreak_days,long_percent, short_percent, scale, return start_date,end_date,duration,trading_times,biggest_drawdown,biggest_gain,start_balance,end_balance
    """
    trend = trend_following_strategy(100000)
    for index,row in data[::-1].iterrows():
        res = trend.new_day(row['price'],row['date'],scale,days,long_percent,short_percent)
        if index%20 == 0:
            print(res)
    return trend
       
def run_window(data,duration=200):
    starting_index = 0
    ending_index = starting_index + duration
    while ending_index <= len(data):
        res = one_iteration(data[starting_index:ending_index])
        
        starting_index = starting_index + 10
        ending_index = ending_index + 10
        print(res.history_balance[-1])

    
 
        
if __name__ == '__main__':
    data = pd.read_csv(os.getcwd() + '\\goldData.csv')
    a = one_iteration(data[:700])
    
    df = a.save_stats()
    df.to_csv(os.getcwd() + '\one_iteration_stats.csv',index=False)
#    run_window(data)
    
    