from flask import Flask, render_template, request
import os.path
import pandas as pd
import plotly.express as px
import plotly
import json 

app = Flask(__name__)


roi = 0.09  # annual rate of return 5%
cpi = 0.025
year_birth = 1967
life = 90 
cpp_payment = {
    60: 397.50, 
    65: 621.10, 
    70: 889.96
} # monthly payment from CPP when starting benefit at age 60, 65, 70
std_cpp = 621.10

# Sample data (replace with your actual data)
data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 1, 5, 3]}
df = pd.DataFrame(data)

@app.route('/')
def index():
    global life
    global roi
    global cpi
    if request.args.get('life_expectancy') is not None:
        life = int(request.args.get('life_expectancy'))
        
    if request.args.get('appreciation_rate') is not None:
        roi = float(request.args.get('appreciation_rate')) / 100

    if request.args.get('cpi') is not None:
        cpi = float(request.args.get('cpi')) / 100

    labels = [None] * ((life-60)*12+1)
    values1 = [None] * ((life-60)*12+1)
    values2 = [None] * ((life-60)*12+1)
    if life > 70:
        rg = 121
    else:
        rg = (life - 60) * 12+1
    for i in range(rg):
        labels[i] = str(60+ int(i/12)) + "." + str(i%12)
        values1[i] = benefit(i, roi)
        values2[i] = benefit(i, cpi)
        
    data = {
        'x' : labels,
        'Value with investment return' : values1,
        'CPI indexed value' :  values2
    }
    df = pd.DataFrame(data)
    fig = px.line(df, x='x', y=['Value with investment return','CPI indexed value'], labels={'x': 'Retirement age', 'value': 'Lifetime Benefit'}, title='CPP benefit chart')

    # Convert the plotly figure to JSON
    graphJSON = json.dumps(fig, cls= plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graphJSON=graphJSON,appreciation_rate=roi*100,life_expectancy=life, cpi=cpi*100)

@app.route('/update_chart', methods=['POST'])
def update_chart():
    # Get user input (example: filter data based on user input)
    selected_value = request.form.get('selected_value') 

    # Filter data based on user input (example: filter based on 'x' values)
    filtered_df = df[df['x'] > int(selected_value)] 

    # Create the updated chart
    fig = px.line(filtered_df, x='x', y='y', title='Updated Chart')
    plot_html = fig.to_html(full_html=False)

    return plot_html

# def contribution():
#     df = pd.read_excel("/home/robert/Documents/Family/Documents/CPP contributions.ods", engine='odf')    
#     total = 0
#     for row in range(0, 21):
#         year = df.loc[row,'year']
#         contribution = df.loc[row,'contribution']
#         company = df.loc[row,'company']
#         val_at_end = round((contribution+company)*(1+roi)**(life-year+year_birth),2)
#         total += val_at_end
#         total = round(total,2)
#     print(total)
    
def benefit(month, appreciation): # time to take benefit after the number of month after age 60
    total = 0
    if month < 60 : # before age 65
        monthly_benefit = std_cpp * ( 1 - 0.006* (60- month))
    elif month >60 and month <= 120:
        monthly_benefit = std_cpp * (1 + 0.007 * (month - 60))
    elif month>120:
        monthly_benefit = std_cpp * 1.42
    else:
        monthly_benefit = std_cpp
    monthly_benefit = round(monthly_benefit,2)
    for i in range (month, (life-60)*12):           
        val_at_end = round(monthly_benefit*(1+appreciation/12)**((life-60)*12-i),2)
        total = round(val_at_end + total,2)
    # print ("monthly payment: " + str(monthly_benefit) + " accumulated in " + str((life-60)*12-month) + " months. end value is: " + str(total))
    return total


if __name__ == '__main__':
    app.run(debug=True)