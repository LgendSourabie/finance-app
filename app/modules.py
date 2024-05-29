import yfinance as yf
import pandas as pd
from datetime import date, datetime
import plotly.graph_objs as go
import plotly.io as pio
import random
from app.data import list_of_tickers


class Stock:
    """stock is a class which provides methods to import data from yahoo finance API, 
       calculate metrics, create chart, etc.
    """
    def __init__(self):
        self.DEFAULT_START_DATE = '2023-01-01'
        self.DEFAULT_END_DATE = date.today().strftime('%Y-%m-%d')
        self.PAGE_SIZE = 10
        self.DECIMAL = 3
        self.NUMBER_OF_ENTRY_overview = 15
        self.WINDOW = 20 
        self.NUM_OF_STD = 2
        self.ENVELOPE_PERCENTAGE = .05


    # fetch Ticker data
    def get_ticker(self,ticker):
        ticker_data = yf.Ticker(ticker)
        return ticker_data
    
    # download data and return a dictionary
    def fetch_data_to_dict(self,ticker, startDate=None,endDate=None):
        self.stock_data = yf.download(ticker,start=startDate,end=endDate)
        date_time = [val.date() for val in pd.Series(self.stock_data.index)]
        volume = [f"{volume:,}" for volume in self.stock_data['Volume'] ]
        return {
            "date": date_time,
            "open": self.stock_data['Open'].round(self.DECIMAL),
            "high": self.stock_data['High'].round(self.DECIMAL),
            "low": self.stock_data['Low'].round(self.DECIMAL),
            "close": self.stock_data['Close'].round(self.DECIMAL),
            "adj close": self.stock_data['Adj Close'].round(self.DECIMAL),
            "volume": volume
        }
    
    # fetch company infos (name- symbol - currency)
    def info_company(self,ticker):
        stock = self.get_ticker(ticker)
        name = stock.info.get('longName','Unknown')
        symbol = stock.info.get('symbol',ticker)
        currency = stock.info.get('currency','USD')
        return symbol,name,currency

    # Calculte the metrics 
    def finance_metrics(self,ticker):
        stock = self.get_ticker(ticker)
        symbol, name,currency = self.info_company(ticker) # return Unknown when keys not found 
        market_cap = stock.info.get('marketCap','Unknown') # return Unknown when key not found 
        turnover = stock.info.get('volume','Unknown') # return Unknown when key not found 
        forward_pe = stock.info.get('forwardPE','Unknown') # return Unknown when key not found 
        enterprise_value = stock.info.get('enterpriseValue','Unknown')
        trailing_pe = stock.info.get('trailingPE','Unknown')  
        peg_ratio  = stock.info.get('pegRatio','Unknown')
        price_sales = stock.info.get('priceToSalesTrailing12Months','Unknown')
        price_book = stock.info.get('priceToBook','Unknown')
        enterprise_revenue = stock.info.get('enterpriseToRevenue','Unknown')
        enterprise_ebitda = stock.info.get('enterpriseToEbitda','Unknown')

        return {
            "Symbol":symbol,
            "Name": name,
            "Market Cap": self.write_comma_separated(market_cap,Billion=True),
            "Turnover": self.write_comma_separated(turnover),
            "Forward P/E": self.write_comma_separated(forward_pe),
            'Trailing P/E':trailing_pe,
            'ENT. Value':self.write_comma_separated(enterprise_value, Billion=True),
            'PEG Ratio'  : peg_ratio,
            'Price Sales' : price_sales,
            'Price Book' : price_book,
            'ENT. Revenue' : enterprise_revenue,
            'ENT. EBITDA' : enterprise_ebitda
        }
    
    #format the ouput number
    def write_comma_separated(self,value,Billion=False):
        if not isinstance(value,str):
            return f"{value/1000000000:,.2f}B" if Billion else f"{value:,.2f}" # return in Billion format or comma separated
        else:
            return value # if the value is a string then return it to avoid bug in the division

    
    #random ticker selector (from list of stickers)
    def generate_random_ticker(self):
        random_tickers = random.sample(list_of_tickers,self.NUMBER_OF_ENTRY_overview)
        list_ticker = [self.finance_metrics(ticker) for ticker in random_tickers]
        return list_ticker

    # calculate the MACD
    def determine_macd(self,df):
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal

    # calculate the rsi
    def determine_rsi(self,data ):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.WINDOW).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.WINDOW).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    # calculate the moving average
    def determine_moving_average(self,dataset):
        moving_average = dataset['Close'].rolling(window=self.WINDOW).mean()
        return moving_average

    # calculate the moving average envelope
    def determine_moving_average_envelope(self,df):
        moving_average = self.determine_moving_average(df)
        upper_envelope = moving_average * (1 + self.ENVELOPE_PERCENTAGE)
        lower_envelope = moving_average * (1 - self.ENVELOPE_PERCENTAGE)
        return upper_envelope, lower_envelope

    # calculate the moving average envelope
    def determine_moving_average_deviation(self,df):
        moving_average = self.determine_moving_average(df)
        deviation = (df['Close'] - moving_average).abs().rolling(window=self.WINDOW).mean()
        return deviation
    
    # determine bollinger bands
    def determine_bollinger_bands(self,df):
        moving_average = self.determine_moving_average(df)
        rolling_std = df['Close'].rolling(window=self.WINDOW).std()
        upper_band = moving_average + (rolling_std * self.NUM_OF_STD)
        lower_band = moving_average - (rolling_std * self.NUM_OF_STD)
        return upper_band, lower_band

    #create entries of calculated indicator for plot
    def generate_plot_data(self,dataframe):
        dataframe['MACD'], dataframe['Signal']= self.determine_macd(dataframe)
        dataframe['RSI'] = self.determine_rsi(dataframe)
        dataframe['Moving_Average'] = self.determine_moving_average(dataframe)
        dataframe['Upper_Envelope'], dataframe['Lower_Envelope'] = self.determine_moving_average_envelope(dataframe)
        dataframe['Moving_Average_Deviation'] = self.determine_moving_average_deviation(dataframe)
        dataframe['Upper_Band'], dataframe['Lower_Band'] = self.determine_bollinger_bands(dataframe)
        return dataframe
    
    # plot cart
    def scatter_plot(self,dataframe):
        macd = go.Scatter(x=dataframe.index, y=dataframe['MACD'], mode='lines', name='MACD')
        signal = go.Scatter(x=dataframe.index, y=dataframe['Signal'], mode='lines', name='Signal')
        rsi = go.Scatter(x=dataframe.index, y=dataframe['RSI'], mode='lines', name='RSI')
        moving_average = go.Scatter(x=dataframe.index, y=dataframe['Moving_Average'], mode='lines', name='Moving Average')
        upper_envelope = go.Scatter(x=dataframe.index, y=dataframe['Upper_Envelope'], mode='lines', name='Upper Envelope')
        lower_envelope = go.Scatter(x=dataframe.index, y=dataframe['Lower_Envelope'], mode='lines', name='Lower Envelope')
        moving_average_deviation = go.Scatter(x=dataframe.index, y=dataframe['Moving_Average_Deviation'], mode='lines', name='Moving Average Deviation')
        upper_band = go.Scatter(x=dataframe.index, y=dataframe['Upper_Band'], mode='lines', name='Upper Band')
        lower_band = go.Scatter(x=dataframe.index, y=dataframe['Lower_Band'], mode='lines', name='Lower Band')
        layout = go.Layout(title='Chart of Financial Metrics', xaxis=dict(title='Date'), yaxis=dict(title='Value'))
        data = [macd,signal,rsi, moving_average,upper_envelope,lower_envelope,moving_average_deviation,upper_band,lower_band ]
        return data, layout

    #create the charts   
    def create_chart(self,ticker,start_date,end_date):
        df = yf.download(ticker, start=start_date, end=end_date)
        dataframe = self.generate_plot_data(df)
        data, layout = self.scatter_plot(dataframe)
        fig = go.Figure(data=data, layout=layout)
        return pio.to_html(fig, full_html=False)
    

    # check if the date chosen by the user is correct: start date must be greater
    def check_date(self,start_date,end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')  # parse the start date to make it comparable using math sign
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        return start_date > end_date
    