from flask import Flask, render_template, request
from app.data import list_of_tickers
from app.modules import Stock


app = Flask(__name__)

stock = Stock()
metric_list = stock.generate_random_ticker() # random stock list to show in overview


# get the stock data
@app.route("/")
@app.route('/stock_overview')
def stock_overview_page():
    return render_template('stock_overview.html',color_overview='overview', metrics=metric_list, ticker_show='hide') # not index but stock_overview.html

# get the historical data
@app.route('/historical_data', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        ticker = request.form.get(key='form-selector',default='AAPL')
        start_date = request.form.get(key='start-date',default=stock.DEFAULT_START_DATE,type=str)
        end_date = request.form.get(key='end-date',default=stock.DEFAULT_END_DATE,type=str)
        page_size = request.form.get(key='row_number',default=stock.PAGE_SIZE,type=int)
        status_code = 201
    elif request.method == 'GET':
        ticker = 'AAPL'
        start_date = stock.DEFAULT_START_DATE
        end_date = stock.DEFAULT_END_DATE
        page_size =stock.PAGE_SIZE
        status_code = 200

    is_start_greater = stock.check_date(start_date=start_date,end_date=end_date) # check if the start date is greater than the end date --> to avoid bugs
    chart = stock.create_chart(ticker, start_date=start_date,end_date=end_date)
    new_stock = stock.fetch_data_to_dict(ticker,startDate=start_date,endDate=end_date) # stock data will be actualized based on the selected stock 
    company_symbol,company_name,currency = stock.info_company(ticker=ticker) # get company name of selected stock symbol
 
    data = {"company_name": company_name,
            "currency" : currency,
            "list_of_tickers":list_of_tickers,
            "selected_stock":ticker,
            "all_keys":new_stock.keys(),
            "dict_value_length":range(page_size),
            "dict_keys":new_stock.values(),
            "startDate":start_date,
            "endDate":end_date,
            "is_date_correct":is_start_greater,
            "page_size":page_size,
            "plot_macd":chart,
            "color_historical":'historical'
                 }
    return render_template('historical_data.html',**data, ticker_show='show'), status_code

#get statistical data
@app.route('/statistics' , methods=['GET','POST'])
def statistics_page():
    if request.method == 'POST':
        ticker = request.form.get(key='form-selector',default='AAPL')
        status_code = 201       # status code for successful post request
    elif request.method == 'GET':
        ticker = 'AAPL'
        status_code = 200   # status code for successful get request
    metrics_dict = stock.finance_metrics(ticker)
    company_symbol,company_name,currency = stock.info_company(ticker=ticker)
    data = { "selected_stock":ticker,
            "list_of_tickers":list_of_tickers,
            'currency':currency}
    return render_template('statistics.html',**data, metrics=metrics_dict, ticker_show='show'), status_code

#get profile data of company leading staff
@app.route('/profile' , methods=['GET','POST'])
def profile_page():
    if request.method == 'POST':
        ticker = request.form.get(key='form-selector',default='AAPL')
        status_code = 201   # status code for successful post request
    elif request.method == 'GET':
        ticker = 'AAPL'
        status_code = 200   # status code for successful get request
    company = stock.get_ticker(ticker).info 
    company_symbol,company_name,currency = stock.info_company(ticker=ticker)
    data = {"color_profile":'profile',
            "selected_stock":ticker,
            "list_of_tickers":list_of_tickers,
            'company_name': company_name}
    return render_template('profile.html', company_info = company['companyOfficers'], **data, ticker_show='show'), status_code


if __name__ == '__main__':
    app.run(port=5000,debug=True)