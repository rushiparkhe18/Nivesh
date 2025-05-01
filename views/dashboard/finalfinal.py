from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

# Load and clean the stock dataset
def load_stock_model():
    stock_data = pd.read_csv("stock_data.csv")
    stock_data.columns = stock_data.columns.str.replace('*', '', regex=False).str.strip()

    for col in ['Close', 'Open', 'High', 'Low', 'Adj Close', 'Volume']:
        stock_data[col] = stock_data[col].str.replace(',', '').astype(float)

    stock_data['MA_5'] = stock_data['Close'].rolling(window=5).mean()
    stock_data['MA_20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['MA_50'] = stock_data['Close'].rolling(window=50).mean()
    stock_data['EMA_12'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
    stock_data['EMA_26'] = stock_data['Close'].ewm(span=26, adjust=False).mean()

    def calculate_rsi(data, window=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    stock_data['RSI'] = calculate_rsi(stock_data['Close'])
    stock_data.dropna(inplace=True)

    stock_features = ['Open', 'High', 'Low', 'MA_5', 'MA_20', 'MA_50', 'EMA_12', 'EMA_26', 'RSI']
    X_stock = stock_data[stock_features]
    y_stock = stock_data['Close']

    X_stock_train, X_stock_test, y_stock_train, y_stock_test = train_test_split(X_stock, y_stock, test_size=0.2, random_state=42, shuffle=False)

    stock_model = RandomForestRegressor(n_estimators=100, random_state=42)
    stock_model.fit(X_stock_train, y_stock_train)

    return stock_model, X_stock_test, y_stock_test

# Load and clean the gold dataset
def load_gold_model():
    gold_data = pd.read_csv('gold.csv')
    gold_data['Date'] = pd.to_datetime(gold_data['Date'])
    gold_data.set_index('Date', inplace=True)

    gold_features = ['Open', 'High', 'Low', 'Volume']
    gold_data_cleaned = gold_data[gold_features + ['Close']].dropna()

    X_gold = gold_data_cleaned[gold_features]
    y_gold = gold_data_cleaned['Close']

    X_gold_train, X_gold_test, y_gold_train, y_gold_test = train_test_split(X_gold, y_gold, test_size=0.2, random_state=42, shuffle=False)

    gold_model = RandomForestRegressor(n_estimators=100, random_state=42)
    gold_model.fit(X_gold_train, y_gold_train)

    return gold_model, X_gold_test, y_gold_test

# Load models
stock_model, X_stock_test, y_stock_test = load_stock_model()
gold_model, X_gold_test, y_gold_test = load_gold_model()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
            .card {
                background-color: #006d5b; /* Dark green */
                color: white;
                border: none;
                transition: transform 0.2s;
            }
            .card:hover {
                transform: scale(1.05);
                background-color: #FFB000; /* Yellow */
            }
            .results-container {
                display: flex;
                flex-wrap: nowrap; /* Prevent wrapping */
                justify-content: space-between; /* Space out cards evenly */
            }
            .result-card {
                margin: 15px;
                flex: 1; /* Make all cards the same size */
                max-width: 18%; /* Set a maximum width for cards */
            }
            h1, h2 {
                text-align: center;
            }
        </style>
        <title>Investment Prediction Tool</title>
    </head>
    <body>
        <div class="container mt-5">
            <h1>Investment Prediction Tool</h1>
            <form id="prediction-form" onsubmit="return submitForm(event)">
                <div class="form-group">
                    <label for="investment">Investment Amount (₹):</label>
                    <input type="number" id="investment" name="investment" min="1" required class="form-control">
                </div>
                <div class="form-group">
                    <label for="risk-tolerance">Risk Tolerance:</label>
                    <select id="risk-tolerance" name="risk-tolerance" required class="form-control">
                        <option value="aggressive">Aggressive</option>
                        <option value="balanced">Balanced</option>
                        <option value="conservative">Conservative</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Predict</button>
            </form>
            <div id="results" class="mt-4">
                <h2>Investment Recommendations:</h2>
                <div class="results-container" id="results-container"></div>
            </div>
        </div>
        <script>
            async function submitForm(event) {
                event.preventDefault();
                const investment = document.getElementById('investment').value;
                const riskTolerance = document.getElementById('risk-tolerance').value;

                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: investment=${investment}&risk_tolerance=${riskTolerance}
                });

                const results = await response.json();
                const resultsContainer = document.getElementById('results-container');
                resultsContainer.innerHTML = ''; // Clear previous results

                results.forEach(result => {
                    const card = document.createElement('div');
                    card.className = 'card result-card';
                    card.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${result.investment_type}</h5>
                            <p class="card-text">Stock Investment: ₹${result.stock_investment.toFixed(2)}</p>
                            <p class="card-text">Gold Investment: ₹${result.gold_investment.toFixed(2)}</p>
                            <p class="card-text">Profit Percentage: ${result.profit_percentage.toFixed(2)}%</p>
                        </div>
                    `;
                    resultsContainer.appendChild(card);
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/predict', methods=['POST'])
def predict():
    investment = request.form.get('investment', type=float)
    risk_tolerance = request.form.get('risk_tolerance', type=str)

    # Investment proportions based on risk tolerance
    if risk_tolerance == 'aggressive':
        ratios = [(0.75, 0.25), (0.70, 0.30), (0.80, 0.20), (0.60, 0.40), (0.65, 0.35)]
    elif risk_tolerance == 'balanced':
        ratios = [(0.50, 0.50), (0.55, 0.45), (0.45, 0.55), (0.40, 0.60), (0.35, 0.65)]
    else:  # conservative
        ratios = [(0.30, 0.70), (0.25, 0.75), (0.20, 0.80), (0.15, 0.85), (0.10, 0.90)]

    investment_results = []

    for stock_ratio, gold_ratio in ratios:
        stock_investment = investment * stock_ratio
        gold_investment = investment * gold_ratio

        # Predict returns
        stock_price_prediction = stock_model.predict([X_stock_test.iloc[-1]])[0]
        gold_price_prediction = gold_model.predict([X_gold_test.iloc[-1]])[0]

        # Calculate expected returns
        stock_return = stock_price_prediction
        gold_return = gold_price_prediction

        # Calculate profit and profit percentage
        stock_profit = abs(stock_return - stock_investment)
        gold_profit = abs(gold_return - gold_investment)

        total_profit = stock_profit + gold_profit
        profit_percentage = (total_profit / investment) * 100

        investment_results.append({
            'investment_type': 'Aggressive' if risk_tolerance == 'aggressive' else 'Balanced' if risk_tolerance == 'balanced' else 'Conservative',
            'stock_investment': stock_investment,
            'gold_investment': gold_investment,
            'profit_percentage': profit_percentage
        })

    return jsonify(investment_results)

if __name__ == '__main__':
    app.run(debug=True)
