# app.py

from flask import Flask, request, jsonify, render_template
import pandas as pd
import pickle

app = Flask(__name__)

# Load the pre-trained models
with open('models\stock_model.pkl', 'rb') as f:
    stock_model = pickle.load(f)

with open('models\gold_model.pkl', 'rb') as f:
    gold_model = pickle.load(f)

# Load some test data to use for predictions (this should match what was used in training)
stock_data = pd.read_csv('stock_data.csv')
gold_data = pd.read_csv('gold.csv')

@app.route('/')
def index():
    return render_template('index.html')  # Correct reference to the file in 'templates/'


@app.route('/predict', methods=['POST'])
def predict():
    investment = float(request.form['investment'])
    risk_tolerance = request.form['risk-tolerance']

    # Investment ratios for different risk profiles
    if risk_tolerance == 'aggressive':
        ratios = [(0.75, 0.25), (0.70, 0.30), (0.80, 0.20)]
    elif risk_tolerance == 'balanced':
        ratios = [(0.50, 0.50), (0.55, 0.45), (0.45, 0.55)]
    else:
        ratios = [(0.30, 0.70), (0.25, 0.75), (0.20, 0.80)]

    results = []

    for stock_ratio, gold_ratio in ratios:
        stock_investment = investment * stock_ratio
        gold_investment = investment * gold_ratio

        # Make predictions
        stock_price_pred = stock_model.predict([stock_data.iloc[-1]])[0]
        gold_price_pred = gold_model.predict([gold_data.iloc[-1]])[0]

        stock_return = stock_price_pred * stock_investment
        gold_return = gold_price_pred * gold_investment

        total_return = stock_return + gold_return
        profit_percentage = ((total_return - investment) / investment) * 100

        results.append({
            'investment_type': f'{int(stock_ratio * 100)}% Stock, {int(gold_ratio * 100)}% Gold',
            'profit_percentage': profit_percentage
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
