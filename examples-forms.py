from flask import Flask, render_template, request
from flask_wtf import Form
from datetime import datetime
import requests
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'




@app.route('/data.html', methods=['GET', 'POST'])
def data_retrieve():
    mydata= {'lst' : []}
    error = ""
    if request.method == 'POST':
        ticker = request.form['ticker']
        datedeb = request.form['datedeb']
        dateEnd = request.form['dateend']
        xperiod = int(request.form['xperiod'])
        #print(xperiod)
    #TODO can test if data are
        mydata = getData(ticker,xperiod, datedeb,dateEnd)
        
    if not mydata:
        error = "Les données ne sont pas disponibles à la periode choisie!!!"
        
            
      #  print(mydata)
    #render the data retrieve page
    return render_template('data.html', message=error,data=mydata)


def getData(ticker, xperiod, datedeb, dateEnd):
    api_url = "https://www.sikafinance.com/api/general/GetHistos"
    headers = {
        "accept": "*/*",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "cookie": "_ga=GA1.2.803303644.1660530733; __gads=ID=4ebb5b4b4bc3835e:T=1660530733:S=ALNI_MYFKapHKqM5T0wn5xOUyezL5xFUHA; _gid=GA1.2.2040239953.1661115998; __gpi=UID=00000a839193b21b:T=1660530733:RT=1661115997:S=ALNI_MZzCOONMVTB12hYB66TJDO1paWuqQ; _gat=1",
        "pragma": "no-cache",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36"
    }
    
    if xperiod in [0, 7]:
        end_date = datetime.strptime(dateEnd, "%Y-%m-%d")
        first_date = datetime.strptime(datedeb, "%Y-%m-%d")
        diff = end_date - first_date
        diff = diff.days
        print(diff)
        
        if diff <= 89 : 
            payload = {
            "ticker": ticker,
            "datedeb": datedeb,
            "datefin": dateEnd,
            "xperiod": str(xperiod)
            }
            response = requests.request("POST", api_url, json=payload, headers=headers)
            response = response.json()
            response1 = response['lst']
        
            #print(response1)
            #df = pd.DataFrame(response1)
            
        else :
            response1 = []
            
            for date in pd.date_range(end = datedeb, start = dateEnd, freq='-3M'):
                to_date = date.strftime('%Y-%m-%d')
                print(to_date)
                
                from_date = (date - pd.DateOffset(days=89)).strftime('%Y-%m-%d')            
                print(from_date)
                payload = {
                    "ticker": ticker,
                    "datedeb": from_date,
                    "datefin": to_date,
                    "xperiod": str(xperiod)
                }

                response = requests.post(api_url, json=payload, headers=headers)
                response = response.json()
                if response['error'] == 'nodata':
                    print("Les données ne sont pas disponibles à cette periode choisie!!!")
                    
                else :
                    response1.extend(response['lst'])
                    #print(response1)

                    #df = pd.DataFrame(response1) 
            print(response1)               
    else:
        payload = {
            "ticker": ticker,
            "xperiod": str(xperiod)
        }
        
        response = requests.request("POST", api_url, json=payload, headers=headers)
        response = response.json()
        response1 = response['lst']        
        #print(response1)
        #df = pd.DataFrame(response1)
    
    previous_close = None  # Variable pour stocker la valeur de clôture précédente

    for item in response1:
        date_str = item['Date']
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        item['Date'] = date_obj.strftime('%Y/%m/%d')
        
        close = item['Close']
        
        if previous_close is not None:
            variation = ((close - previous_close) / previous_close) * 100
            item['Variation'] = round(variation, 2)
        else:
            item['Variation'] = ''
        
        previous_close = close
        
    
    print(response1)
    return response1

if __name__ == "__main__":
    app.run(debug=True, port=8001)
