# train_models.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import pickle

# Function to train stock model
def train_stock_model():
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

    X_stock_train, _, y_stock_train, _ = train_test_split(X_stock, y_stock, test_size=0.2, random_state=42, shuffle=False)

    stock_model = RandomForestRegressor(n_estimators=100, random_state=42)
    stock_model.fit(X_stock_train, y_stock_train)

    # Save model to disk
    with open('models\stock_model.pkl', 'wb') as f:
        pickle.dump(stock_model, f)

# Function to train gold model
def train_gold_model():
    gold_data = pd.read_csv('gold.csv')
    gold_data['Date'] = pd.to_datetime(gold_data['Date'])
    gold_data.set_index('Date', inplace=True)

    gold_features = ['Open', 'High', 'Low', 'Volume']
    gold_data_cleaned = gold_data[gold_features + ['Close']].dropna()

    X_gold = gold_data_cleaned[gold_features]
    y_gold = gold_data_cleaned['Close']

    X_gold_train, _, y_gold_train, _ = train_test_split(X_gold, y_gold, test_size=0.2, random_state=42, shuffle=False)

    gold_model = RandomForestRegressor(n_estimators=100, random_state=42)
    gold_model.fit(X_gold_train, y_gold_train)

    # Save model to disk
    with open('models\gold_model.pkl', 'wb') as f:
        pickle.dump(gold_model, f)

if __name__ == '__main__':
    train_stock_model()
    train_gold_model()
    print("Models trained and saved!")
