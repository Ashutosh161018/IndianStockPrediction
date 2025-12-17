from flask import Flask, request, jsonify, send_from_directory
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend, avoids Tkinter warnings
import matplotlib.pyplot as plt
import os
import pandas as pd
import wikipediaapi

app = Flask(__name__, static_folder="../Frontend", static_url_path="")

# ---------------- SETUP ---------------- #

charts_folder = "charts"
os.makedirs(charts_folder, exist_ok=True)

companies_df = pd.read_csv("companies.csv")

# ---------------- HELPER FUNCTIONS ---------------- #

def get_company_from_message(message):
    message = message.lower()
    for _, row in companies_df.iterrows():
        if row['name'].lower() in message:
            return row
    return None

def get_stock_price(ticker):
    try:
        data = yf.download(ticker, period="60d", auto_adjust=True, progress=False)
        if data.empty:
            return None, None

        plt.figure(figsize=(6, 3))
        data['Close'].plot(title=f"{ticker} - Last 60 Days")
        chart_path = f"{charts_folder}/{ticker}.png"
        plt.savefig(chart_path)
        plt.close()

        price = round(float(data['Close'].iloc[-1]), 2)
        chart_url = f"http://127.0.0.1:5000/charts/{ticker}.png"
        return price, chart_url
    except Exception as e:
        print("Stock error:", e)
        return None, None

def get_company_info(wiki_name):
    try:
        wiki = wikipediaapi.Wikipedia(
            language="en",
            user_agent="StockTalkAI/1.0"
        )
        page = wiki.page(wiki_name)

        if page.exists() and page.summary:
            return page.summary[:500]
        else:
            return "Sorry, I couldn't find company information."
    except Exception as e:
        print("Wiki error:", e)
        return "Error fetching company information."

# ---------------- API ---------------- #

@app.route("/ask", methods=["POST"])
def ask():
    message = request.json.get("message", "").strip().lower()
    print("User:", message)

    company = get_company_from_message(message)

    if company is None:
        return jsonify({
            "reply": "I couldn't identify the company. Please ask about an NSE company.",
            "chart_url": None
        })

    company_name = company['name']
    ticker = company['ticker']
    wiki_name = company['wiki_name']

    # STOCK PRICE REQUEST
    if any(word in message for word in ["price", "stock", "share", "predict"]):
        price, chart_url = get_stock_price(ticker)
        if price:
            return jsonify({
                "reply": f"{company_name} latest stock price is ₹{price}",
                "chart_url": chart_url
            })
        else:
            return jsonify({
                "reply": "Unable to fetch stock price right now.",
                "chart_url": None
            })

    # COMPANY INFO REQUEST
    if any(word in message for word in ["about", "who", "what", "tell"]):
        info = get_company_info(wiki_name)
        return jsonify({
            "reply": info,
            "chart_url": None
        })

    # DEFAULT SMART RESPONSE
    return jsonify({
        "reply": f"Do you want the stock price or company information about {company_name}?",
        "chart_url": None
    })

# ---------------- STATIC FILES ---------------- #

@app.route("/charts/<path:filename>")
def charts(filename):
    return send_from_directory(charts_folder, filename)

@app.route("/")
def index():
    return app.send_static_file("index.html")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    print("🚀 StockTalk AI running...")
    app.run(debug=True)
