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

crop_images = {
    'rice': 'https://images.pexels.com/photos/96417/pexels-photo-96417.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'maize': 'https://images.pexels.com/photos/872483/pexels-photo-872483.jpeg?auto=compress&cs=tinysrgb&w=600',
    'jute': 'https://images.pexels.com/photos/17362930/pexels-photo-17362930/free-photo-of-green-tall-plants-on-field.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'cotton': ' https://images.pexels.com/photos/8730509/pexels-photo-8730509.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'coconut': ' https://images.pexels.com/photos/27497946/pexels-photo-27497946/free-photo-of-a-coconut-tree-with-green-fruit-on-it.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'papaya': ' https://images.pexels.com/photos/15556727/pexels-photo-15556727/free-photo-of-green-papaya-fruits-hanging-on-tree.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'orange': ' https://images.pexels.com/photos/2171374/pexels-photo-2171374.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'apple': ' https://images.pexels.com/photos/2821819/pexels-photo-2821819.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'muskmelon': 'https://images.pexels.com/photos/28454829/pexels-photo-28454829/free-photo-of-pile-of-fresh-striped-melons-at-market.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'watermelon': 'https://images.pexels.com/photos/12746880/pexels-photo-12746880.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'grapes': 'https://images.pexels.com/photos/225229/pexels-photo-225229.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'mango': 'https://images.pexels.com/photos/16003687/pexels-photo-16003687/free-photo-of-fruit-on-tree.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'banana': 'https://images.pexels.com/photos/6141487/pexels-photo-6141487.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'pomegranate': 'https://images.pexels.com/photos/5320089/pexels-photo-5320089.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
    'lentil': 'https://cdn.britannica.com/14/157214-050-3A82D9CD/kinds-lentils.jpg',
    'blackgram': 'https://agribee.in/wp-content/uploads/2020/01/blackgram.jpg',
    'mungbean': 'https://images.pexels.com/photos/7334141/pexels-photo-7334141.jpeg?auto=compress&cs=tinysrgb&w=600',
    'mothbeans': 'https://ooofarms.com/cdn/shop/products/MothBean1_whole.jpg?v=1672251298&width=3840',
    'pigeonpeas': 'https://gardenerspath.com/wp-content/uploads/2022/02/How-to-Grow-Pigeon-Peas-Feature.jpg',
    'kidneybeans': 'https://images-prod.healthline.com/hlcmsresource/images/AN_images/kidney-beans-1296x728-feature.jpg',
    'chickpea': 'https://img.feedstrategy.com/files/base/wattglobalmedia/all/image/2023/10/chickpeas.652d6f3ea08b0.png?auto=format%2Ccompress&q=70&w=880',
    'coffee': 'https://images.pexels.com/photos/2131720/pexels-photo-2131720.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

blogs =   [
    {
      "title": "Understanding Soil Nutrients: NPK Explained",
      "author": "Dr. Green",
      "date": "2025-02-04",
      "category": "Soil Science",
      "image": "https://images.pexels.com/photos/1301856/pexels-photo-1301856.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
      "excerpt": "Learn how Nitrogen (N), Phosphorus (P), and Potassium (K) affect soil fertility and crop yield.",
      "description": "This blog explains the importance of NPK (Nitrogen, Phosphorus, and Potassium) in soil and how they influence plant growth.",
      "link": "https://www.gardeningknowhow.com/garden-how-to/soil-fertilizers/fertilizer-numbers-npk.htm?utm_source=chatgpt.com"
    },
    {
      "title": "Best Crops for High Nitrogen Soil",
      "author": "AgriTech Insights",
      "date": "2025-01-28",
      "category": "Crop Recommendations",
      "image": "https://images.pexels.com/photos/2203683/pexels-photo-2203683.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Discover which crops thrive in nitrogen-rich soils and how to balance nutrients effectively.",
      "description": "Explore a list of crops that grow best in nitrogen-rich soils and how farmers can balance soil nutrients for optimal yield.",
      "link": "https://foodcycler.com/blogs/gardening/nitrogen-loving-plants-that-will-love-your-foodcycler-fertilizer?srsltid=AfmBOopSvYrN4E5bDPtPWO05JuqmUmsJt8AE-V8LezSSpofKCr9mZqpJ&utm_source=chatgpt.com"
    },
    {
      "title": "Soil Testing 101: Measuring NPK Levels",
      "author": "Farmers' Digest",
      "date": "2025-01-20",
      "category": "Farming Tips",
      "image": "https://images.pexels.com/photos/1251026/pexels-photo-1251026.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "A step-by-step guide to testing soil nutrient levels and improving crop productivity.",
      "description": "Learn how to conduct soil tests to measure nutrient levels and take corrective actions for better crop health.",
      "link": "https://extension.colostate.edu/topic-areas/yard-garden/vegetable-gardening-nitrogen-recommendations-7-247/?utm_source=chatgpt.com"
    },
    {
      "title": "Organic Fertilizers vs. Chemical Fertilizers",
      "author": "Sustainable Farming",
      "date": "2025-02-01",
      "category": "Sustainable Agriculture",
      "image": "https://images.pexels.com/photos/15671396/pexels-photo-15671396/free-photo-of-close-up-of-the-ground-on-a-horse-pasture.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Compare the benefits of organic and chemical fertilizers and their impact on soil health.",
      "description": "This article discusses the pros and cons of organic and chemical fertilizers, helping farmers make informed choices.",
      "link": "https://www.pennington.com/all-products/fertilizer/resources/fertilizer-labels-what-N-P-K-numbers-mean?utm_source=chatgpt.com"
    },
    {
      "title": "Top 5 Crops for Phosphorus-Deficient Soil",
      "author": "Agro Experts",
      "date": "2025-01-15",
      "category": "Crop Selection",
      "image": "https://images.pexels.com/photos/30504188/pexels-photo-30504188/free-photo-of-young-saplings-in-nursery-para-brazil.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Find out which crops can grow well in phosphorus-deficient conditions and how to amend soil.",
      "description": "Discover the best crops for phosphorus-deficient soil and techniques to improve phosphorus levels naturally.",
      "link": "https://www.reddit.com/r/vegetablegardening/comments/ote71z/plants_that_add_to_soil_health/?utm_source=chatgpt.com"
    },
    {
      "title": "The Role of Potassium in Plant Growth",
      "author": "Plant Nutrition Hub",
      "date": "2025-01-10",
      "category": "Plant Health",
      "image": "https://images.pexels.com/photos/2583755/pexels-photo-2583755.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Discover why potassium is essential for plant growth and how to maintain optimal soil levels.",
      "description": "This blog highlights the importance of potassium for plant health and methods to maintain adequate potassium levels in soil.",
      "link": "https://www.thespruce.com/what-does-npk-mean-for-a-fertilizer-2131094?utm_source=chatgpt.com"
    },
    {
      "title": "How to Improve Soil Structure Naturally",
      "author": "Eco Farmers",
      "date": "2025-02-02",
      "category": "Soil Health",
      "image": "https://images.pexels.com/photos/6104931/pexels-photo-6104931.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Explore natural ways to enhance soil structure for better water retention and root growth.",
      "description": "Learn various organic methods to improve soil structure, making it more fertile and resilient for farming.",
      "link": "https://www.theguardian.com/lifeandstyle/2024/dec/08/let-things-go-feral-how-to-do-carbon-positive-gardening-in-your-own-back-yard?utm_source=chatgpt.com"
    },
    {
      "title": "Composting: A Guide to Organic Waste Recycling",
      "author": "Green Earth",
      "date": "2025-01-25",
      "category": "Sustainable Practices",
      "image": "https://images.pexels.com/photos/5608056/pexels-photo-5608056.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Learn how composting transforms organic waste into nutrient-rich soil amendments.",
      "description": "A detailed guide on composting techniques and how they contribute to sustainable farming and waste reduction.",
      "link": "https://www.theaustralian.com.au/weekend-australian-magazine/coffee-is-the-secret-to-supercharging-your-soil/news-story/f0ea27da5b159ba84738086cd1f50588?utm_source=chatgpt.com"
    },
    {
      "title": "Essential Micro-Nutrients for Healthy Crops",
      "author": "Agriculture Today",
      "date": "2025-01-18",
      "category": "Crop Nutrition",
      "image": "https://images.pexels.com/photos/7232905/pexels-photo-7232905.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Understand the role of essential micro-nutrients in crop growth and yield optimization.",
      "description": "This article explains why micro-nutrients like zinc, iron, and magnesium are crucial for crop development.",
      "link": "https://en.wikipedia.org/wiki/Fertilizer?utm_source=chatgpt.com"
    },
    {
      "title": "How Climate Change Affects Soil Fertility",
      "author": "Climate Research Institute",
      "date": "2025-01-12",
      "category": "Environmental Impact",
      "image": "https://images.pexels.com/photos/264537/pexels-photo-264537.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Examine how shifting weather patterns influence soil nutrient balance and crop production.",
      "description": "An in-depth look at how climate change impacts soil quality and what farmers can do to adapt.",
      "link": "https://www.theatlantic.com/science/archive/2024/07/mass-extinction-species-humans-earth/678897/?utm_source=chatgpt.com"
    },
    {
      "title": "Water Management Techniques for Farmers",
      "author": "AgriTech Solutions",
      "date": "2025-01-08",
      "category": "Irrigation & Water",
      "image": "https://images.pexels.com/photos/20457262/pexels-photo-20457262/free-photo-of-farmers-in-india.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Explore effective water management techniques to conserve water and improve crop yield.",
      "description": "Learn about modern irrigation methods, water conservation techniques, and efficient farming strategies.",
      "link": "https://www.thespruce.com/winter-sowing-8769838?utm_source=chatgpt.com"
    },
    {
      "title": "Cover Crops: Benefits and Best Practices",
      "author": "Sustainable Farming",
      "date": "2025-01-05",
      "category": "Soil Conservation",
      "image": "https://images.pexels.com/photos/96715/pexels-photo-96715.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Learn how cover crops improve soil fertility, prevent erosion, and boost biodiversity.",
      "description": "A guide to selecting and using cover crops to protect soil and enhance agricultural sustainability.",
      "link": "https://en.wikipedia.org/wiki/Cover_crop?utm_source=chatgpt.com"
    },
    {
      "title": "Organic Pest Control Methods for Farmers",
      "author": "Eco Farmers",
      "date": "2025-01-02",
      "category": "Pest Management",
      "image": "https://images.pexels.com/photos/17903068/pexels-photo-17903068/free-photo-of-man-spraying-plants-in-a-vegetable-garden-using-a-sprayer.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Discover natural and eco-friendly ways to manage pests without harming beneficial insects.",
      "description": "Learn how to implement organic pest control techniques that reduce the need for harmful pesticides.",
      "link": "https://images.pexels.com/photos/17903068/pexels-photo-17903068/free-photo-of-man-spraying-plants-in-a-vegetable-garden-using-a-sprayer.jpeg?auto=compress&cs=tinysrgb&w=600"
    },
    {
      "title": "Top 10 High-Yield Crops for Small Farms",
      "author": "Farmers' Digest",
      "date": "2025-02-01",
      "category": "Agriculture Trends",
      "image": "https://images.pexels.com/photos/1595104/pexels-photo-1595104.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Find out which crops are most profitable and high-yielding for small-scale farming.",
      "description": "A ranking of the top 10 high-yield crops ideal for small farms, focusing on profitability and efficiency.",
      "link": "https://www.bhg.com/carrot-companion-plants-8678310?utm_source=chatgpt.com"
    },
    {
      "title": "Hydroponics vs. Traditional Farming: Pros & Cons",
      "author": "AgriTech Insights",
      "date": "2025-01-29",
      "category": "Modern Farming",
      "image": "https://images.pexels.com/photos/5005518/pexels-photo-5005518.jpeg?auto=compress&cs=tinysrgb&w=600",
      "excerpt": "Compare the advantages and disadvantages of hydroponics and traditional soil-based farming.",
      "description": "This blog explores the benefits and challenges of hydroponic farming versus conventional farming.",
      "link": "https://www.reuters.com/sustainability/land-use-biodiversity/brazilian-farmers-who-are-trying-keep-world-its-coffee-habit-despite-climate-2024-09-16/?utm_source=chatgpt.com"
    }
  ]


@app.route('/blog')
def blog():
    page = request.args.get("page", 1, type=int)  # Get page number, default is 1
    per_page = 6  # Show 6 blogs per page

    start = (page - 1) * per_page
    end = start + per_page
    paginated_blogs = blogs[start:end]

    has_next = end < len(blogs)
    has_previous = start > 0

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

@app.route("/predict", methods=['POST'])
def predict():
    N = float(request.form['Nitrogen'])
    P = float(request.form['Phosphorus'])
    K = float(request.form['Potassium'])
    temp = float(request.form['Temperature'])
    humidity = float(request.form['Humidity'])
    ph = float(request.form['pH'])
    rainfall = float(request.form['Rainfall'])

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    prediction = model.predict([feature_list])
    result = prediction[0]
    
    image_url = crop_images.get(result, 'https://via.placeholder.com/300?text=No+Image+Available')

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