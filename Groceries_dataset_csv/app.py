import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from collections import Counter

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Dummy credentials (replace with a proper database in production)
USER_CREDENTIALS = {
    "admin": "password123",
    "user": "testpass"
}

# Ensure 'static' directory exists
if not os.path.exists("static"):
    os.makedirs("static")

# Load dataset
df = pd.read_csv("Groceries_dataset.csv")

# Convert dataset into list of transactions per customer
transactions = df.groupby("Member_number")["itemDescription"].apply(list).tolist()

# Count occurrences of each item
item_counts = Counter(item for transaction in transactions for item in transaction)

# Extract the top 20 most frequently purchased items
top_20_items = [item[0] for item in item_counts.most_common(20)]

# Initialize co-occurrence matrix
co_occurrence_matrix = pd.DataFrame(0, index=top_20_items, columns=top_20_items)

# Populate co-occurrence matrix
for transaction in transactions:
    filtered_transaction = [item for item in transaction if item in top_20_items]
    for item1 in filtered_transaction:
        for item2 in filtered_transaction:
            if item1 != item2:
                co_occurrence_matrix.loc[item1, item2] += 1

# ---  Generate & Save Heatmap ---
plt.figure(figsize=(12, 8))
sns.heatmap(co_occurrence_matrix, cmap="coolwarm", annot=True, fmt="g", linewidths=0.5)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.title("Heatmap of Top 20 Co-occurring Items")
plt.savefig("static/heatmap.png")
plt.close()

# ---  Bar Chart (Top 10 Most Purchased Items) ---
top_10_items = df["itemDescription"].value_counts().head(10)
plt.figure(figsize=(8, 5))
top_10_items.plot(kind="bar", color=sns.color_palette("bright"))
plt.xlabel("Items")
plt.ylabel("Frequency")
plt.title("Top 10 Most Purchased Items")
plt.xticks(rotation=45)
plt.savefig("static/top_10_bar.png")
plt.close()

# ---  Pie Chart (with Vibrant Colors) ---
plt.figure(figsize=(8, 6))
plt.pie(
    top_10_items.values,
    labels=top_10_items.index,
    autopct='%1.1f%%',
    colors=sns.color_palette("bright"),
    wedgeprops={'edgecolor': 'black'}  # Adds a black border for better visibility
)
plt.title("Top 10 Most Purchased Items (Pie Chart)")
plt.savefig("static/top_10_pie.png")
plt.close()

# --- Scatter Plot ---
plt.figure(figsize=(8, 6))
sns.scatterplot(x=top_10_items.index, y=top_10_items.values, color="blue", s=100, edgecolor="black")
plt.xlabel("Items")
plt.ylabel("Frequency")
plt.title("Scatter Plot of Top 10 Items")
plt.xticks(rotation=45)
plt.savefig("static/scatterplot.png")
plt.close()

#  Generate Offers Based on Frequently Bought Items
def generate_offers():
    offers = []
    for item, count in item_counts.most_common(5):  # Get top 5 most purchased items
        offers.append(f"Buy 2 {item} and get 1 free!")
        offers.append(f"Special discount on {item}: Buy more, save more!")
    return offers

# Flask Routes
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('index'))  # Redirect to index.html if logged in
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['user'] = username  # Store user in session
            return redirect(url_for('index'))
        else:
            return "Invalid credentials! Try again."

    return render_template('login.html')

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))  # Prevent access without login
    return render_template("index.html")  # Load your graph chart page

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('login'))

@app.route('/offers')
def offers():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("offers.html", offers=generate_offers())

@app.route('/get-visualizations')
def get_visualizations():
    return jsonify({
        "bar_chart": "/static/top_10_bar.png",
        "pie_chart": "/static/top_10_pie.png",
        "scatterplot": "/static/scatterplot.png",
        "heatmap": "/static/heatmap.png"
    })

if __name__ == "__main__":
    app.run(debug=True)
