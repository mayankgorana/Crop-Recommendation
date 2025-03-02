from flask import Flask, request, render_template, jsonify
import numpy as np
import logging
import pickle
import requests
import os
import urllib.parse                                   
from flask_pymongo import PyMongo            
from flask_cors import CORS
from dotenv import load_dotenv


# Loading env file
load_dotenv()

# Dynamically get the current directory of app.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the finalized_model.sav file
filename = os.path.join(current_dir, 'finalized_model.sav')

# Load the model
model = pickle.load(open(filename, 'rb'))

# Flask app setup
app = Flask(__name__)

# -------------------------------------------------------------------

CORS(app)

# Contact Us Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/crop_database"
mongo = PyMongo(app)

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()  # Ensure we receive JSON data
        print("Received Data:", data)  # Debugging

        # Validate required fields
        if not all(key in data and data[key].strip() for key in ["name", "email", "subject", "message"]):
            return jsonify({"error": "All fields are required"}), 400

        # Insert into MongoDB
        mongo.db.contact_data.insert_one(data)

        return jsonify({"message": "Form submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error message


# Load the NewsAPI key from environment variable
API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://newsapi.org/v2/everything")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/blog')
def blog():
    page = request.args.get("page", 1, type=int)  # Get page number, default is 1
    per_page = 6  # Show 6 blogs per page

    blog_collection = mongo.db.blogs
    total_blogs = blog_collection.count_documents({})
    paginated_blogs = list(blog_collection.find().skip((page - 1) * per_page).limit(per_page))

    has_next = (page * per_page) < total_blogs
    has_previous = page > 1

    return render_template("blog.html", blogs=paginated_blogs, page=page, has_next=has_next, has_previous=has_previous)


@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/crop')
def crop():
    return render_template("crop.html")

@app.route('/donation')
def donation():
    return render_template("donation.html")

@app.route('/quote')
def quote():
    return render_template("quote.html")

@app.route('/help')
def help():
    return render_template("help.html")

# Prediction
@app.route("/predict", methods=['POST'])
def predict():
    N = float(request.form.get('Nitrogen', 0))
    P = float(request.form.get('Phosphorus', 0))
    K = float(request.form.get('Potassium', 0))
    temp = float(request.form.get('Temperature', 0))
    humidity = float(request.form.get('Humidity', 0))
    ph = float(request.form.get('pH', 0))
    rainfall = float(request.form.get('Rainfall', 0))

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    prediction = model.predict([feature_list])
    result = prediction[0]
    
    crop_data = mongo.db.crop_images.find_one({"crop_name": result})
    image_url = crop_data["image_url"] if crop_data else "https://via.placeholder.com/300?text=No+Image+Available"

    return render_template('crop.html', result=result, image_url=image_url)


@app.route("/news", methods=['GET'])
def news():
    page = request.args.get("page", 1, type=int)  # Get page number, default is 1
    
    # Ensuring max 3 pages
    if page > 3:
        return redirect(url_for('news', page=3))  # Redirect to page 3 if exceeded

    query = "agriculture OR crops"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "relevancy",
        "page": page,
        "pageSize": 6,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        news_data = response.json()

        articles = news_data.get("articles", [])
        total_results = news_data.get("totalResults", 0)

        # Pagination logic: Limit to 3 pages only
        has_next = page < 3
        has_previous = page > 1

        return render_template(
            "news.html",
            articles=articles,
            page=page,
            has_next=has_next,
            has_previous=has_previous
        )

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


# Run the Flask app
if __name__ == "__main__":
     # Suppress Flask's default request logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Only show errors, suppress other logs

    app.run(debug=True)


# App running on a http://127.0.0.1:5000/   