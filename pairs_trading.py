import numpy as np

#schedule function
def initialize(context):
    schedule_function(check_pairs, date_rules.every_day(), time_rules.market_close(minutes=60))
    
    context.amair = sid(45971)
    context.ual = sid(28051)
    
    #Flags, or checks
    context.long_on_spread = False
    context.shorting_spread = False
    
    
#check pairs
def check_pairs(context,data):
    aa = context.amair
    ual = context.ual
    prices = data.history([aa,ual], 'price', 30, '1d')
    short_prices = prices.iloc[-1:]
    
    #Spread
    mavg30 = np.mean(prices[aa] - prices[ual]) #moving avg 30 days
    std30 = np.std(prices[aa] - prices[ual])
    mavg1 = np.mean(short_prices[aa] - short_prices[ual])
    
    if std30 > 0: #if i have 30 days of info
        zscore = (mavg1 - mavg30) / std30
        #Note the 1 below is arbitrary
        if zscore > 0.3 and not context.shorting_spread:
            #AA is overvalued and will regress back to the mean
            order_target_percent(aa, -0.5) #short AA
            order_target_percent(ual, 0.5) #long UAL
            context.shorting_spread = True
            context.long_on_spread = False
        elif zscore < -0.3 and not context.long_on_spread:
            #UAL is overvalued and will regress back to the mean
            order_target_percent(aa, 0.5) #long AA
            order_target_percent(ual, -0.5) #short UAL
            context.shorting_spread = False
            context.long_on_spread = True
        elif abs(zscore) < 0.1:
            #sell all cuz we're near the mean
            order_target_percent(aa, 0)
            order_target_percent(ual, 0)
            context.shorting_spread = False
            context.long_on_spread = False
        record(z_score = zscore)
