# Importing flask module in the project is mandatory
from flask import Flask, request, jsonify
from itertools import groupby
from datetime import date
import pandas as pd

# Flask constructor takes the name of 
app = Flask(__name__)


def season_of_date(mouth, day, year):
    date_now = date( int("20"+year), int(mouth), int(day))
    if not isinstance(date_now, date):
        return "No date"
    year = str(date_now.year)
    date_now = str(date_now)
    seasons = {
            'spring': pd.date_range(start='19/03/'+year,  end='19/06/'+year),
            'summer': pd.date_range(start='20/06/'+year,  end='21/09/'+year),
            'fall':   pd.date_range(start='22/09/'+year,  end='20/12/'+year)
            }

    if date_now in seasons['spring']:
        return 'spring'
    if date_now in seasons['summer']:
        return 'summer'
    if date_now in seasons['fall']:
        return 'fall'
    else:
        return 'winter'


@app.route('/weather',  methods = ['POST'])
def detecting_change():
    data = request.get_json()
    response = [ item for index, item in enumerate(data) if (
            item['was_rainy'] == True and data[index -1]['was_rainy'] == False)
                ]

    return jsonify(response)


@app.route('/seasons',  methods = ['POST'])
def detecting_seasons():
    data = request.get_json()
    response = []
    for item in data:
        date = item['ORD_DT'].split("/")
        mouth, day, year = date
        result = season_of_date(mouth, day, year)
        response.append({ "ORD_ID": item["ORD_ID"], "SEASON": result })
    
    return jsonify(response)


@app.route('/orders',  methods = ['POST'])
def ordes_status():
    data = request.get_json()
    response = []
    for number, orders in groupby(data, key=lambda x: x.get('order_number')):
        count_shipped = 0 
        count_pending = 0
        count_cancelled = 0
        status = ""
        for order in orders:
            if "SHIPPED" == order['status']:
                count_shipped += 1
            elif "PENDING" == order['status']:
                count_pending += 1
            else:
                count_cancelled += 1

        if count_pending > 0:
            status = "PENDING"
        elif count_shipped > 0 and count_pending == 0:
            status = "SHIPPED"
        elif count_cancelled > 0 and count_pending == 0 and count_shipped == 0:
            status = "CANCELLED"

        response.append({"order_number": number, "status":status})

    return jsonify(response)

if __name__ == '__main__':
    # run() method of Flask class runs the application 
    app.run()