from flask import Flask, request, jsonify, send_from_directory
import yfinance as yf
import matplotlib.pyplot as plt
import os
import pandas as pd

app = Flask(__name__, static_folder="../Frontend", static_url_path="")

# Ensure charts folder exists
charts_folder = "charts"
if not os.path.exists(charts_folder):
    os.makedirs(charts_folder)

# Load companies CSV
csv_path = "companies.csv"
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"{csv_path} not found in Backend folder!")

companies_df = pd.read_csv(csv_path)

def get_ticker(company_name):
    """Get NSE ticker from company name"""
    row = companies_df[companies_df['name'].str.lower() == company_name.lower()]
    if not row.empty:
        return row['ticker'].values[0]
    return None

def predict_stock_price(ticker):
    """Fetch last 60 days stock data and generate chart"""
    try:
        data = yf.download(ticker, period="60d", progress=False, auto_adjust=True)
        if data.empty:
            return None, None

        # Create chart
        plt.figure(figsize=(6,3))
        data['Close'].plot(title=f"{ticker} Last 60 Days Close")
        chart_path = os.path.join(charts_folder, f"{ticker}_chart.png")
        plt.savefig(chart_path)
        plt.close()

        latest_price = round(float(data['Close'].iloc[-1]), 2)
        chart_url = f"http://127.0.0.1:5000/charts/{ticker}_chart.png"
        return latest_price, chart_url
    except Exception as e:
        print("Error fetching stock data:", e)
        return None, None

# API to handle chat messages
@app.route("/ask", methods=["POST", "GET"])
def ask():
    if request.method == "GET":
        return jsonify({"reply":"Use POST with JSON: {\"message\":\"Predict price of TCS\"}"})

    data = request.get_json()
    message = data.get("message", "").strip()
    print("Received message:", message)

    if message.lower().startswith("predict price of "):
        company_name = message[17:].strip()
        ticker = get_ticker(company_name)
        print("Ticker found:", ticker)
        if ticker:
            price, chart_url = predict_stock_price(ticker)
            if price:
                return jsonify({"reply": f"{company_name} latest close price: ₹{price}", "chart_url": chart_url})
            else:
                return jsonify({"reply": "Error fetching stock data.", "chart_url": None})
        else:
            return jsonify({"reply": f"Company '{company_name}' not found in database.", "chart_url": None})
    else:
        return jsonify({"reply": "Hello! I am StockTalk AI. Ask me about NSE stocks like Infosys, TCS, Reliance.", "chart_url": None})

# Serve charts
@app.route("/charts/<path:filename>")
def serve_charts(filename):
    return send_from_directory(charts_folder, filename)

# Serve frontend
@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    print("Starting StockTalk AI backend...")
    app.run(debug=True)
