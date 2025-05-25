from email.mime.image import MIMEImage
from functools import wraps
import json
import re
from bson import ObjectId
from flask import Flask, flash, render_template, request, redirect, url_for, session
import pandas as pd
from flask import request, redirect, url_for, render_template
from datetime import datetime

import requests
from transformers import pipeline
import matplotlib.pyplot as plt
import io
import base64
import pymongo
from wordcloud import WordCloud
import seaborn as sns
from collections import Counter
import numpy as np
from datetime import datetime
from textblob import TextBlob
import matplotlib
import os
from urllib.parse import urljoin
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
from fpdf import FPDF  # PDF generation library
matplotlib.use('Agg')
from bson import ObjectId
matplotlib.use('Agg')  # Use a non-interactive backend
from nltk.sentiment import SentimentIntensityAnalyzer
import io
from flask import Flask, render_template, request, jsonify
import nltk
nltk.download('vader_lexicon')











import csv
import re
from urllib.parse import quote
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

app = Flask(__name__)

# Define keywords to look for in reviews
KEYWORDS = {
    'good': ['good', 'great', 'excellent', 'fantastic', 'love', 'like', 'satisfied', 'amazing', '❤️', 'Thankyou'],
    'bad': ['bad', 'poor', 'terrible', 'disappointed', 'hate', 'worse', 'not good', 'Fake', '😡', 'not great'],
    'recommended': ['recommend', 'recommended', 'suggest', 'advise', 'should buy']
}

# Initialize WebDriver outside the routes
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#driver.get("https://www.amazon.com")

# Load the CSV file
#df = pd.read_csv('Iphone 13 Amazon Reviews.csv')
df = pd.read_csv('zaibten_scrap_datafile.csv')


# Print column names for debugging
print(df.columns)

# Replace 'category' with the actual column name
categories = df['category'].unique()

def create_review_plot(good_count, bad_count):
    labels = ['Good Reviews', 'Bad Reviews']
    sizes = [good_count, bad_count]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_rating_distribution_plot(filtered_df):
    filtered_df.loc[:, 'rating_numeric'] = pd.to_numeric(filtered_df['rating'].str.split(' ').str[0], errors='coerce')
    rating_counts = filtered_df['rating_numeric'].value_counts().sort_index()
    
    plt.figure(figsize=(8, 5))
    rating_counts.plot(kind='bar', color='skyblue')
    plt.title('Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Number of Reviews')
    plt.xticks(rotation=0)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_average_rating_plot(filtered_df):
    average_rating = filtered_df['rating_numeric'].mean()
    
    plt.figure(figsize=(6, 4))
    plt.bar(['Average Rating'], [average_rating], color='lightblue')
    plt.ylim(0, 5)
    plt.title('Average Rating')
    plt.ylabel('Rating')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_box_plot(filtered_df):
    plt.figure(figsize=(6, 4))
    plt.boxplot(filtered_df['rating_numeric'], vert=False)
    plt.title('Box Plot of Ratings')
    plt.xlabel('Rating')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_word_cloud(filtered_df):
    reviews = ' '.join(filtered_df['review_text'].dropna().astype(str))
    if not reviews.strip():
        return None  # No review text, return None or some placeholder
   
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(reviews)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_top_reviews_plot(filtered_df):
    filtered_df['rating_numeric'] = pd.to_numeric(filtered_df['rating'].str.split(' ').str[0], errors='coerce')
    top_reviews = filtered_df.dropna(subset=['rating_numeric']).nlargest(10, 'rating_numeric')
    
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(range(len(top_reviews)))  # Generate multiple colors
    plt.barh(top_reviews['product_name'], top_reviews['rating_numeric'], color=colors)
    plt.title('Top 10 Reviews')
    plt.xlabel('Rating')
    plt.ylabel('Product Name')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_top_reviewers_plot(filtered_df):
    top_users = filtered_df['profile_name'].value_counts().nlargest(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_users.index, y=top_users.values, palette='plasma')
    plt.title('Top 10 Reviewers')
    plt.xlabel('Reviewer')
    plt.ylabel('Number of Reviews')
    plt.xticks(rotation=45)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_sentiment_analysis_plot(filtered_df):
    sentiment_counts = filtered_df['rating_numeric'].apply(lambda x: 'Positive' if x >= 4 else 'Negative').value_counts()
    
    plt.figure(figsize=(6, 4))
    sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, palette='muted')
    plt.title('Sentiment Analysis of Reviews')
    plt.xlabel('Sentiment')
    plt.ylabel('Number of Reviews')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_trend_of_ratings_plot(filtered_df):
    if 'date' in filtered_df.columns:
        filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')
        ratings_over_time = filtered_df.groupby(filtered_df['date'].dt.to_period('M'))['rating_numeric'].mean()
        
        plt.figure(figsize=(10, 5))
        ratings_over_time.plot(marker='o')
        plt.title('Trend of Average Ratings Over Time')
        plt.xlabel('Date')
        plt.ylabel('Average Rating')
        plt.xticks(rotation=45)
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return base64.b64encode(img.getvalue()).decode()
    return None

def create_top_five_words_plot(filtered_df):
    reviews = ' '.join(filtered_df['review_text'].astype(str))
    words = [word for word in reviews.split() if len(word) > 2]  # Filter out short words
    most_common_words = Counter(words).most_common(5)
    
    words, counts = zip(*most_common_words)
    
    plt.figure(figsize=(8, 5))
    sns.barplot(x=list(counts), y=list(words), palette='viridis')
    plt.title('Top 5 Most Frequent Words in Reviews')
    plt.xlabel('Count')
    plt.ylabel('Words')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_review_length_distribution_plot(filtered_df):
    filtered_df['review_length'] = filtered_df['review_text'].apply(lambda x: len(str(x)))
    
    plt.figure(figsize=(8, 5))
    sns.histplot(filtered_df['review_length'], bins=30, kde=True)
    plt.title('Distribution of Review Lengths')
    plt.xlabel('Length of Review (characters)')
    plt.ylabel('Frequency')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_ratings_heatmap(filtered_df):
    heatmap_data = filtered_df.pivot_table(index='subcategory', columns='rating_numeric', values='review_text', aggfunc='count', fill_value=0)
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, cmap='Blues')
    plt.title('Ratings Heatmap Across Subcategories')
    plt.xlabel('Ratings')
    plt.ylabel('Subcategories')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()


app.secret_key = '05b49f8c793c97f1f870020fb69c4571fd2e5607'

# MongoDB connection
app.config["MONGO_URI"] = "mongodb+srv://dawoodzahid488:BozqArXOh5NImhu3@cluster0.nyf6y.mongodb.net/your_database?retryWrites=true&w=majority"
mongo = pymongo.MongoClient(app.config["MONGO_URI"])
db = mongo.Zaibten  # Replace 'your_database' with your actual database name
users_collection = db.users  # Replace with your users collection name
reviews_collection = db.reviews  # Collection to store review data

@app.route('/')
@app.route('/home')
def home():
    # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None

    # Load the CSV file with reviews
    csv_file = 'combined_reviews.csv'  # Update the path to your CSV file
    df = pd.read_csv(csv_file)

    # Filter reviews with a 5-star rating
    df_filtered = df[df['rating'] == '5.0 out of 5 stars']

    # Drop duplicate products and select the first 9 unique ones
    df_unique_products = df_filtered.drop_duplicates(subset='product_name').head(12)

    # Prepare the data to pass to the template
    reviews = df_unique_products[['product_name', 'review_text', 'model', 'category', 'image']].to_dict(orient='records')

    # Render the home.html template, passing both the username and reviews data
    return render_template('home.html', username=username, reviews=reviews)



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email, "password": password})

        if user:
            session['user_id'] = str(user['_id'])
            return redirect(url_for('home'))
        else:
            # Pass 'invalid' as True if login fails
            return render_template('login.html', invalid=True)
    
    # Default 'invalid' as False for GET requests
    return render_template('login.html', invalid=False)


# Route for signup
@app.route('/signup', methods=['GET', 'POST'])

def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return 'User already exists'
        
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # or just '%Y-%m-%d'
        
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": password,
            "created_at": current_date  # <--- date field added here
        })
        return redirect(url_for('login'))
    
    return render_template('signup.html')
@app.route('/layout')
def dashboard():
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        return f"{user['name']}!"
    else:
        return redirect(url_for('login'))

@app.route('/livescrap')
@login_required
def livescrap():
        # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None

    return render_template('livescrap.html', username=username)

@app.route('/scrape', methods=['POST'])
@login_required
def scrape():
    # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None

    product_name = request.form['product_name']
    url = request.form['product_url']

    names, ratings, rating_dates, titles, reviews_text, images = [], [], [], [], [], []
    keywords_found = {'good': [], 'bad': [], 'recommended': []}
    page_number = 1

    sia = SentimentIntensityAnalyzer()  # Initialize SentimentIntensityAnalyzer

    while True:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-hook='review']"))
            )
            html_data = BeautifulSoup(driver.page_source, 'html.parser')
            reviews = html_data.find_all('div', {'data-hook': 'review'})
            if not reviews:
                break

            for review in reviews:
                name = review.find('span', {'class': 'a-profile-name'}).text.strip()
                names.append(name)
                rating = review.find('span', {'class': 'a-icon-alt'}).text
                ratings.append(rating)
                rating_date = review.find('span', {'data-hook': 'review-date'}).text
                rating_dates.append(rating_date)
                title = review.find('a', {'data-hook': 'review-title'}).text
                titles.append(title)
                review_text = review.find('span', {'data-hook': 'review-body'}).text
                reviews_text.append(review_text)

                for key in keywords_found.keys():
                    for keyword in KEYWORDS[key]:
                        if keyword in review_text.lower() and review_text not in keywords_found[key]:
                            keywords_found[key].append(review_text)

                images.append('')

            next_page = html_data.find('li', {'class': 'a-last'})
            if next_page and next_page.a and 'href' in next_page.a.attrs:
                url = urljoin(url, next_page.a['href'])
                page_number += 1
            else:
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # Create DataFrame with ratings and sentiment analysis
    data = pd.DataFrame({
        'Product Name': [product_name] * len(names),
        'Profile Name': names,
        'Rating': ratings,
        'Date': rating_dates,
        'Title': titles,
        'Review Text': reviews_text,
    })

    # Convert ratings to numeric for comparison
    data['Rating'] = data['Rating'].str.extract('(\d+\.\d+)').astype(float)  # Extract numeric rating

    # Set sentiment based on rating only
    data['Sentiment'] = data['Rating'].apply(lambda x: 'Negative' if x < 4 else 'Positive')

    # (Optional) Collect insights based on keywords but do not change sentiment
    for idx, row in data.iterrows():
        review_text = row['Review Text']
        if any(keyword in review_text.lower() for keyword in KEYWORDS['good']):
            # This is for insights; you can log or print for further analysis
            pass

    total_good_reviews = len(keywords_found['good'])
    total_bad_reviews = len(keywords_found['bad'])
    product_status = "Good Product: Recommended" if total_good_reviews > total_bad_reviews else "Not Recommended Product"

    # Plot good vs bad reviews
    plt.figure(figsize=(6, 4))
    labels = ['Good Reviews', 'Bad Reviews']
    values = [total_good_reviews, total_bad_reviews]
    plt.bar(labels, values, color=['green', 'red'])
    plt.title('Good vs Bad Reviews')
    img_io1 = BytesIO()
    plt.savefig(img_io1, format='png')
    img_io1.seek(0)
    plt.close()

    # Plot distribution of ratings
    rating_counts = pd.Series(ratings).value_counts()
    plt.figure(figsize=(6, 4))
    rating_counts.plot(kind='bar', color='skyblue')
    plt.title('Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    img_io2 = BytesIO()
    plt.savefig(img_io2, format='png')
    img_io2.seek(0)
    plt.close()

    # Plot word count analysis
    word_counts = [len(review.split()) for review in reviews_text]
    plt.figure(figsize=(6, 4))
    plt.hist(word_counts, bins=20, color='purple', edgecolor='black')
    plt.title('Review Word Count Distribution')
    plt.xlabel('Word Count')
    plt.ylabel('Frequency')
    img_io3 = BytesIO()
    plt.savefig(img_io3, format='png')
    img_io3.seek(0)
    plt.close()

    send_email([img_io1, img_io2, img_io3], product_name, product_status, total_good_reviews, total_bad_reviews)

    img_data = base64.b64encode(img_io1.getvalue()).decode()
    rendered_page = render_template('livescrap.html', 
                                    tables=[data.to_html(classes='data', index=False)],  # Exclude index
                                    titles=['Scraped Reviews'],
                                    keywords_found=keywords_found,
                                    total_good_reviews=total_good_reviews,
                                    total_bad_reviews=total_bad_reviews,
                                    product_status=product_status,
                                    graph_data=img_data, username=username)
    return rendered_page

def create_pdf(img_ios, product_name, product_status, total_good_reviews, total_bad_reviews):
    pdf = FPDF()
    pdf.add_page()

    # Add logo
    # logo_path = 'static/images/logo.png'  # Replace with your logo's path
    # pdf.image(logo_path, 10, 8, 33)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Review Analysis for Product: {product_name}", ln=True, align="C")
    pdf.ln(10)

    # Product details
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Product Status: {product_status}", ln=True)
    pdf.cell(200, 10, txt=f"Total Good Reviews: {total_good_reviews}", ln=True)
    pdf.cell(200, 10, txt=f"Total Bad Reviews: {total_bad_reviews}", ln=True)
    pdf.ln(10)

    # Attach each graph
    for img_io in img_ios:
        pdf.image(img_io, x=10, w=180)
        pdf.ln(10)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

def get_logged_in_user_email():
    # Ensure 'user_id' is in session
    if 'user_id' not in session:
        print("No user ID in session.")
        return None

    try:
        # Fetch the currently logged-in user based on session ID
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        if user:
            return user.get("email")  # Ensure your email field is correct
    except Exception as e:
        print(f"Error fetching user email: {e}")
    return None

def send_email(img_ios, product_name, product_status, total_good_reviews, total_bad_reviews):
    sender_email = "dawoodzahid488@gmail.com"
    recipient_email = get_logged_in_user_email()
    
    if not recipient_email:
        print("No recipient email found; email not sent.")
        return  # Exit function if recipient email is None
    
    password = "yrcd wubo xysl jgbi"
    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Review Analysis for Product: {product_name}"

    # Create PDF and attach
    pdf_attachment = create_pdf(img_ios, product_name, product_status, total_good_reviews, total_bad_reviews)
    attach_part = MIMEBase('application', 'octet-stream')
    attach_part.set_payload(pdf_attachment.read())
    encoders.encode_base64(attach_part)
    attach_part.add_header('Content-Disposition', 'attachment', filename="Review_Analysis.pdf")
    msg.attach(attach_part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to determine sentiment
def Yelp_get_sentiment_score(comment):
    analysis = TextBlob(comment)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"



def Yelp_scrape_reviews(url, product_name):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)  # Allow the page to load
    reviews_data = []

    while True:
        try:
            # Locate all reviews on the current page
            reviews_section = driver.find_elements(By.CSS_SELECTOR, "li.fdbk-container")
            for review in reviews_section:
                try:
                    username = review.find_element(By.CSS_SELECTOR, "div.fdbk-container__details__info__username span").text
                    date = review.find_element(By.CSS_SELECTOR, "span.fdbk-container__details__info__divide__time span").text
                    comment = review.find_element(By.CSS_SELECTOR, "div.fdbk-container__details__comment span").text.strip()
                    if not comment:
                        continue
                    feedback_type_icon = review.find_element(By.CSS_SELECTOR, "div.fdbk-container__details__info__icon svg")
                    feedback_type = feedback_type_icon.get_attribute("data-test-type")

                    sentiment_score = Yelp_get_sentiment_score(comment)

                    reviews_data.append({
                        "Product Name": product_name,
                        "Username": username,
                        "Date": date,
                        "Comment": comment,
                        "Feedback Type": feedback_type,
                        # "Sentiment Score": sentiment_score
                    })
                except Exception as e:
                    print("Error processing review:", e)

            # Check for the "Next" button and navigate to the next page
            next_button = driver.find_elements(By.CSS_SELECTOR, "a.pagination__next")
            if next_button and "disabled" not in next_button[0].get_attribute("class"):
                next_button[0].click()
                time.sleep(3)  # Allow the next page to load
            else:
                print("No more pages to scrape.")
                break
        except Exception as e:
            print("An error occurred during pagination:", e)
            break

    # Close the browser
    driver.quit()
    return reviews_data

# Function to generate graphs
def generate_graphs(summary):
    # Pie chart for sentiment distribution
    labels = ['Positive', 'Negative', 'Neutral']
    sizes = [summary['good_reviews'], summary['bad_reviews'], summary['neutral_reviews']]
    colors = ['#28a745', '#e74c3c', '#f1c40f']
    explode = (0.1, 0, 0)  # explode the first slice

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save graph to memory
    graph_buffer = BytesIO()
    plt.savefig(graph_buffer, format='png')
    graph_buffer.seek(0)
    plt.close(fig)
    return graph_buffer

def save_to_mongo(summary, user_email):
    """Save scraped data to MongoDB."""
    review_data = {
        "product_name": summary['product_name'],
        "good_reviews": summary['good_reviews'],
        "bad_reviews": summary['bad_reviews'],
        "neutral_reviews": summary['neutral_reviews'],
        "recommendation": summary['recommendation'],
        "user_email": user_email,
        "created_at": datetime.now()  # Store real-time timestamp
    }
    reviews_collection.insert_one(review_data)
    print("Data saved to MongoDB successfully!")

def send_email(summary, graph_buffer):
    """Send email with sentiment analysis and attached graph."""
    sender_email = "dawoodzahid488@gmail.com"
    recipient_email = get_logged_in_user_email()  # Function to fetch logged-in user's email
    
    # Save the scraped data to MongoDB
    save_to_mongo(summary, recipient_email)

    subject = f"{summary['product_name']} - Review Sentiment Analysis Report"

    # Email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # HTML Email Body
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f2f2f2; margin: 0; padding: 0; color: #333333;">
        <div style="background-color: #ffffff; padding: 30px; text-align: center; border-bottom: 1px solid #ddd;">
            <img src="cid:logo" alt="Zaibten Logo" style="border-radius: 10px; width: 120px; height: 120px;"/>
            <h1 style="font-size: 26px; color: #333333; font-weight: 600; margin-top: 15px;">{summary['product_name']} Review Analysis</h1>
            <p style="font-size: 18px; color: #666666; margin-top: 10px;">Here is the sentiment analysis of your product reviews.</p>
        </div>
        <div style="padding: 30px; background-color: #ffffff; margin: 30px auto; width: 90%; max-width: 650px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <h2 style="font-size: 22px; color: #333333; margin-bottom: 15px;">Summary</h2>
            <p><strong>Good Reviews:</strong> <span style="color: #28a745;">{summary['good_reviews']}</span></p>
            <p><strong>Bad Reviews:</strong> <span style="color: #e74c3c;">{summary['bad_reviews']}</span></p>
            <p><strong>Neutral Reviews:</strong> {summary['neutral_reviews']}</p>
            <p><strong>Recommendation:</strong> {summary['recommendation']}</p>
        </div>
        <div style="text-align: center; margin-top: 30px;">
            <h2>Sentiment Distribution</h2>
            <img src="cid:graph" alt="Sentiment Distribution Graph" style="width: 100%; max-width: 600px; border-radius: 8px;"/>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    # Logo Attachment
    with open("static/images/logo.png", "rb") as logo_file:
        logo_data = logo_file.read()
        logo = MIMEImage(logo_data, name="logo.png")
        logo.add_header('Content-ID', '<logo>')
        msg.attach(logo)

    # Graph Attachment
    graph_image = MIMEImage(graph_buffer.read(), name="sentiment_graph.png")
    graph_image.add_header('Content-ID', '<graph>')
    msg.attach(graph_image)

    # SMTP Sending
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, "yrcd wubo xysl jgbi")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        
@app.route('/ebay_index', methods=['GET', 'POST'])
@login_required
def ebay_Index():
    # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None

    reviews_df = None
    positive_comments = []  # List for positive comments
    negative_comments = []  # New list for negative comments
    summary = {
        "good_reviews": 0,
        "bad_reviews": 0,
        "neutral_reviews": 0,
        "recommendation": "",
        "product_name": ""
    }

    if request.method == 'POST':
        product_name = request.form['product_name']
        url = request.form['url']
        summary["product_name"] = product_name
        reviews_data = Yelp_scrape_reviews(url, product_name)
        reviews_df = pd.DataFrame(reviews_data)

        # Filter positive comments
        positive_comments = reviews_df[reviews_df['Feedback Type'] == "positive"]['Comment'].tolist()

        # Filter negative comments
        negative_comments = reviews_df[reviews_df['Feedback Type'] == "negative"]['Comment'].tolist()

        # Count the types of reviews based on Feedback Type
        summary['good_reviews'] = reviews_df[reviews_df['Feedback Type'] == "positive"].shape[0]
        summary['bad_reviews'] = reviews_df[reviews_df['Feedback Type'] == "negative"].shape[0]
        summary['neutral_reviews'] = reviews_df[reviews_df['Feedback Type'] == "neutral"].shape[0]

        # Determine recommendation
        if summary['good_reviews'] > (summary['good_reviews'] + summary['bad_reviews'] + summary['neutral_reviews']) / 2:
            summary['recommendation'] = "Recommended"
        else:
            summary['recommendation'] = "Not Recommended"

        # Generate graph
        graph_buffer = generate_graphs(summary)

        # Send email with graph
        send_email(summary, graph_buffer)

    return render_template(
        'ebay_index.html',
        tables=[reviews_df.to_html(classes='table table-striped')] if reviews_df is not None else None,
        summary=summary,
        username=username,
        positive_comments=positive_comments,  # Pass the list of positive comments
        negative_comments=negative_comments   # Pass the list of negative comments
    )

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    selected_category = request.form.get('category')
    selected_subcategory = request.form.get('subcategory')
    selected_model = request.form.get('model')  # Added model dropdown
    subcategories = []
    models = []
    product_name = None
    good_review_count = 0
    bad_review_count = 0
    review_plot = None
    rating_distribution_plot = None
    average_rating_plot = None
    box_plot = None
    word_cloud = None
    top_reviews_plot = None
    top_reviewers_plot = None
    sentiment_plot = None
    trend_plot = None
    top_words_plot = None
    review_length_plot = None
    ratings_heatmap_plot = None

    if selected_category:
        subcategories = df[df['category'] == selected_category]['subcategory'].unique()
        
        if selected_subcategory:
            models = df[(df['category'] == selected_category) & 
                        (df['subcategory'] == selected_subcategory)]['model'].unique()  # Fetch models

            if selected_model:
                filtered_df = df[(df['category'] == selected_category) & 
                                 (df['subcategory'] == selected_subcategory) &
                                 (df['model'] == selected_model)]
                
                filtered_df['rating_numeric'] = pd.to_numeric(filtered_df['rating'].str.split(' ').str[0], errors='coerce')

                good_reviews = filtered_df[filtered_df['rating_numeric'] >= 4.0]
                if not good_reviews.empty:
                    product_name = good_reviews['product_name'].iloc[0]
                    good_review_count = len(good_reviews)
                    bad_review_count = len(filtered_df) - good_review_count
                    review_plot = create_review_plot(good_review_count, bad_review_count)
                    rating_distribution_plot = create_rating_distribution_plot(filtered_df)
                    average_rating_plot = create_average_rating_plot(filtered_df)
                    box_plot = create_box_plot(filtered_df)
                    word_cloud = create_word_cloud(filtered_df)
                    top_reviews_plot = create_top_reviews_plot(filtered_df)
                    top_reviewers_plot = create_top_reviewers_plot(filtered_df)
                    sentiment_plot = create_sentiment_analysis_plot(filtered_df)
                    trend_plot = create_trend_of_ratings_plot(filtered_df)
                    top_words_plot = create_top_five_words_plot(filtered_df)
                    review_length_plot = create_review_length_distribution_plot(filtered_df)
                    ratings_heatmap_plot = create_ratings_heatmap(filtered_df)

    return render_template('index.html', categories=categories, subcategories=subcategories, 
                           models=models,  # Pass models to template
                           selected_category=selected_category, selected_subcategory=selected_subcategory, 
                           selected_model=selected_model,  # Pass model to form
                           product_name=product_name, good_review_count=good_review_count, 
                           bad_review_count=bad_review_count, review_plot=review_plot,
                           rating_distribution_plot=rating_distribution_plot, average_rating_plot=average_rating_plot, 
                           box_plot=box_plot, word_cloud=word_cloud, top_reviews_plot=top_reviews_plot,
                           top_reviewers_plot=top_reviewers_plot, sentiment_plot=sentiment_plot,
                           trend_plot=trend_plot, top_words_plot=top_words_plot,
                           review_length_plot=review_length_plot, ratings_heatmap_plot=ratings_heatmap_plot)



@app.route('/about', methods=['GET', 'POST'])
def about():
    # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None
        
    return render_template("about.html", username=username)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None
        
    return render_template("contact.html", username=username)

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the session
    return redirect(url_for('login'))

@app.route('/reviews', methods=['GET', 'POST'])
@login_required
def reviews():
    # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None


    # Fetch unique values from 'category', 'subcategory', and 'model'
    categories = df['category'].dropna().unique()
    subcategories = df['subcategory'].dropna().unique()
    models = df['model'].dropna().unique()

    selected_category = None
    selected_subcategory = None
    selected_model = None

    best_product = None  # Initialize variable to hold best product details
    graph_url = None  # Initialize variable to hold the graph image URL
    pie_chart_url = None  # Initialize variable to hold the pie chart image URL
    histogram_url = None  # Initialize variable to hold histogram image URL
    boxplot_url = None  # Initialize variable to hold boxplot image URL
    scatterplot_url = None  # Initialize variable to hold scatterplot image URL
    line_chart_url = None  # Initialize variable to hold line chart image URL
    line_chart_url_2 = None  # Initialize variable for the second line chart
    pie_chart_url_2 = None  # Initialize variable for the second pie chart

    if request.method == 'POST':
        selected_category = request.form.get('category')
        selected_subcategory = request.form.get('subcategory')
        selected_model = request.form.get('model')

        # Filter the data based on user selection
        filtered_df = df[(
            df['category'] == selected_category) & 
            (df['subcategory'] == selected_subcategory) & 
            (df['model'] == selected_model)
        ]


        # Find the product with the highest rating
        if not filtered_df.empty:
            best_product = filtered_df.loc[filtered_df['rating'].idxmax()]  # Get row with max rating

            # Generate a bar chart for the ratings distribution
            rating_counts = filtered_df['rating'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(rating_counts.index, rating_counts.values, color='skyblue')
            ax.set_xlabel('Ratings')
            ax.set_ylabel('Number of Reviews')
            ax.set_title('Ratings Distribution')

            # Save the bar chart to a string in base64 format
            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            graph_url = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Generate a pie chart for the rating proportions
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(rating_counts.values, labels=rating_counts.index, autopct='%1.1f%%', colors=['skyblue', 'lightgreen', 'orange', 'lightcoral', 'gold'])
            ax.set_title('Rating Proportions')

            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            pie_chart_url = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Generate a histogram for review length distribution
            review_lengths = filtered_df['review_text'].apply(lambda x: len(str(x)) if isinstance(x, str) else 0)
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.hist(review_lengths, bins=20, color='skyblue', edgecolor='black')
            ax.set_xlabel('Review Length (Characters)')
            ax.set_ylabel('Frequency')
            ax.set_title('Review Length Distribution')

            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            histogram_url = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Generate a boxplot for rating distribution
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.boxplot(filtered_df['rating'], patch_artist=True, boxprops=dict(facecolor='skyblue', color='black'))
            ax.set_ylabel('Ratings')
            ax.set_title('Boxplot of Ratings')

            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            boxplot_url = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Generate a scatter plot for review length vs. rating
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(review_lengths, filtered_df['rating'], color='blue', alpha=0.5)
            ax.set_xlabel('Review Length (Characters)')
            ax.set_ylabel('Ratings')
            ax.set_title('Review Length vs. Rating')

            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            scatterplot_url = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Generate a line chart for average ratings over time
            dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
            avg_ratings = [3.5, 4.0, 4.5, 3.0, 3.8, 4.2, 4.0, 3.6, 4.1, 4.3]

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(dates, avg_ratings, marker='o', color='blue')
            ax.set_xlabel('Review Date')
            ax.set_ylabel('Average Rating')
            ax.set_title('Average Ratings Over Time')

            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            line_chart_url = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Generate a second line chart for rating changes over time
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(dates, [4.2, 4.1, 4.3, 3.9, 4.0, 4.1, 4.4, 4.0, 3.8, 4.2], marker='o', color='green')
            ax.set_xlabel('Review Date')
            ax.set_ylabel('Rating Value')
            ax.set_title('Rating Trend Over Time')

            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            line_chart_url_2 = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Generate a second pie chart for sentiment distribution
            sentiment_counts = {'Positive': 80, 'Negative': 15, 'Neutral': 5}  # Example counts
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), autopct='%1.1f%%', colors=['lightgreen', 'orange', 'lightcoral'])
            ax.set_title('Review Sentiment Distribution')

            img_io = io.BytesIO()
            fig.savefig(img_io, format='png')
            img_io.seek(0)
            pie_chart_url_2 = base64.b64encode(img_io.getvalue()).decode('utf-8')


    return render_template(
        'reviews.html',
        categories=categories,
        subcategories=subcategories,
        models=models,
        selected_category=selected_category,
        selected_subcategory=selected_subcategory,
        selected_model=selected_model,
        best_product=best_product,  # Pass best product to the template
        graph_url=graph_url,  # Pass the ratings distribution graph URL
        pie_chart_url=pie_chart_url,  # Pass the pie chart URL
        histogram_url=histogram_url,  # Pass the histogram URL
        boxplot_url=boxplot_url,  # Pass the boxplot URL
        scatterplot_url=scatterplot_url,  # Pass the scatter plot URL
        line_chart_url=line_chart_url,  # Pass the line chart URL
        line_chart_url_2=line_chart_url_2,  # Pass the second line chart URL
        pie_chart_url_2=pie_chart_url_2,  # Pass the second pie chart URL
        username=username
    )

@app.route('/get_subcategories/<category>', methods=['GET'])
def get_subcategories(category):
    subcategories = df[df['category'] == category]['subcategory'].dropna().unique()
    return jsonify(subcategories=subcategories.tolist())

@app.route('/get_models/<subcategory>', methods=['GET'])
def get_models(subcategory):
    models = df[df['subcategory'] == subcategory]['model'].dropna().unique()
    return jsonify(models=models.tolist())




# Load pre-trained sentiment-analysis model from Hugging Face
sentiment_analyzer = pipeline("sentiment-analysis")

def foodreviewssentiment_score(review):
    result = sentiment_analyzer(review)
    label = result[0]['label']
    score = result[0]['score']
    
    if label == 'POSITIVE' and score > 0.5:
        return "Positive"
    elif label == 'NEGATIVE' and score > 0.5:
        return "Negative"
    else:
        return "Neutral"


# def foodreviewscreate_graphs(positive_count, negative_count, review_data):
#     graphs = {}
    
#     # 1. Sentiment Analysis Bar Chart
#     fig, ax = plt.subplots()
#     ax.bar(['Positive', 'Negative'], [positive_count, negative_count], color=['green', 'red'])
#     ax.set_xlabel('Sentiment')
#     ax.set_ylabel('Review Count')
#     ax.set_title('Review Sentiment Analysis')
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     graphs['sentiment_bar'] = base64.b64encode(img.getvalue()).decode('utf-8')
#     plt.close(fig)

#     # 2. Sentiment Analysis Pie Chart
#     fig, ax = plt.subplots()
#     ax.pie([positive_count, negative_count], labels=['Positive', 'Negative'], colors=['green', 'red'], autopct='%1.1f%%', startangle=90)
#     ax.set_title('Sentiment Distribution')
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     graphs['sentiment_pie'] = base64.b64encode(img.getvalue()).decode('utf-8')
#     plt.close(fig)

#     # 3. Sentiment Over Time Line Chart (Simulating with index as time)
#     review_data['sentiment_numeric'] = review_data['classification'].map({'Positive': 1, 'Negative': -1})
#     fig, ax = plt.subplots()
#     ax.plot(review_data.index, review_data['sentiment_numeric'], color='blue')
#     ax.set_xlabel('Review Index')
#     ax.set_ylabel('Sentiment')
#     ax.set_title('Sentiment Over Time (Reviews)')
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     graphs['sentiment_line'] = base64.b64encode(img.getvalue()).decode('utf-8')
#     plt.close(fig)

#     # 4. Word Cloud (Top 10 Frequent Words - Sampled)
#     from wordcloud import WordCloud
#     text = ' '.join(review_data['review'])
#     wordcloud = WordCloud(max_words=10).generate(text)
#     fig, ax = plt.subplots()
#     ax.imshow(wordcloud, interpolation='bilinear')
#     ax.axis('off')
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     graphs['wordcloud'] = base64.b64encode(img.getvalue()).decode('utf-8')
#     plt.close(fig)

#     # 5. Review Length vs Sentiment Box Plot
#     review_data['review_length'] = review_data['review'].apply(len)
#     fig, ax = plt.subplots()
#     sns.boxplot(x='classification', y='review_length', data=review_data, ax=ax)
#     ax.set_title('Review Length vs Sentiment')
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     graphs['review_length_box'] = base64.b64encode(img.getvalue()).decode('utf-8')
#     plt.close(fig)

#     # 6. Sentiment Distribution Over Review Length (New Graph)
#     fig, ax = plt.subplots()
#     sns.scatterplot(x='review_length', y='sentiment_numeric', data=review_data, hue='classification', palette='coolwarm', alpha=0.7)
#     ax.set_xlabel('Review Length')
#     ax.set_ylabel('Sentiment')
#     ax.set_title('Sentiment Distribution Over Review Length')
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     graphs['sentiment_length'] = base64.b64encode(img.getvalue()).decode('utf-8')
#     plt.close(fig)

#     return graphs


def foodreviewscreate_graphs(positive_count, negative_count, review_data):
    graphs_data = {}

    # 1. Sentiment Analysis Bar Chart
    graphs_data['sentiment_bar'] = {
        "labels": ["Positive", "Negative"],
        "data": [positive_count, negative_count],
        "colors": ["green", "red"],
    }

    # 2. Sentiment Analysis Pie Chart
    graphs_data['sentiment_pie'] = {
        "labels": ["Positive", "Negative"],
        "data": [positive_count, negative_count],
        "colors": ["green", "red"],
    }

    # 3. Sentiment Over Time Line Chart
    review_data['sentiment_numeric'] = review_data['classification'].map({'Positive': 1, 'Negative': -1}).tolist()
    graphs_data['sentiment_line'] = {
        "x": list(review_data.index),
        "y": review_data['sentiment_numeric'].tolist(),
        "color": "blue",
    }

    # 4. Word Frequency (Top 10)
    from collections import Counter
    word_counts = Counter(" ".join(review_data['review']).split())
    top_words = word_counts.most_common(10)
    graphs_data['wordcloud'] = {
        "labels": [word for word, count in top_words],
        "data": [count for word, count in top_words],
    }

    # 5. Review Length vs Sentiment Box Plot
    review_data['review_length'] = review_data['review'].apply(len)
    graphs_data['review_length_box'] = review_data[['classification', 'review_length']].to_dict('list')

    # 6. Sentiment Distribution Over Review Length
    graphs_data['sentiment_length'] = review_data[['review_length', 'sentiment_numeric']].to_dict('list')

    return graphs_data



def create_graphs_for_email(positive_count, negative_count, review_data):
    graphs_data = {}

    # 1. Sentiment Analysis Bar Chart
    fig, ax = plt.subplots()
    ax.bar(["Positive", "Negative"], [positive_count, negative_count], color=["green", "red"])
    ax.set_title("Sentiment Analysis - Bar Chart")
    ax.set_ylabel("Count")
    bar_buffer = io.BytesIO()
    plt.savefig(bar_buffer, format="png")
    plt.close(fig)
    bar_buffer.seek(0)

    # 2. Sentiment Analysis Pie Chart
    fig, ax = plt.subplots()
    ax.pie([positive_count, negative_count], labels=["Positive", "Negative"], colors=["green", "red"], autopct='%1.1f%%')
    ax.set_title("Sentiment Analysis - Pie Chart")
    pie_buffer = io.BytesIO()
    plt.savefig(pie_buffer, format="png")
    plt.close(fig)
    pie_buffer.seek(0)

    # 3. Sentiment Over Time Line Chart
    review_data['sentiment_numeric'] = review_data['classification'].map({'Positive': 1, 'Negative': -1}).tolist()
    fig, ax = plt.subplots()
    ax.plot(review_data.index, review_data['sentiment_numeric'], color="blue")
    ax.set_title("Sentiment Over Time")
    ax.set_ylabel("Sentiment")
    ax.set_xlabel("Time")
    line_buffer = io.BytesIO()
    plt.savefig(line_buffer, format="png")
    plt.close(fig)
    line_buffer.seek(0)

    # 4. Word Frequency (Top 10)
    from collections import Counter
    word_counts = Counter(" ".join(review_data['review']).split())
    top_words = word_counts.most_common(10)
    words, counts = zip(*top_words)

    fig, ax = plt.subplots()
    ax.bar(words, counts)
    ax.set_title("Top 10 Most Frequent Words")
    ax.set_ylabel("Frequency")
    ax.set_xticklabels(words, rotation=45, ha="right")
    wordcloud_buffer = io.BytesIO()
    plt.savefig(wordcloud_buffer, format="png")
    plt.close(fig)
    wordcloud_buffer.seek(0)

    # Return graph data and buffers
    return {
        "sentiment_bar": bar_buffer,
        "sentiment_pie": pie_buffer,
        "sentiment_line": line_buffer,
        "wordcloud": wordcloud_buffer,
    }




def save_review_data(summary, user_email):
    """
    Save scraped review data in MongoDB
    """
    review_data = {
        "product_name": summary['product_name'],
        "ratings": summary['ratings'],
        "recommendation": summary['recommendation'],
        "user_email": user_email,
        "reviews": summary['reviews'],  # Storing all review text data
        "created_at": datetime.now()  # Store real-time timestamp
    }
    
    reviews_collection.insert_one(review_data)  # Insert into MongoDB
    print("Review data saved successfully!")

def send_email_with_graphs(summary, graphs_data):
    # Save to MongoDB (moved inside function)
    save_review_data(summary, summary['user_email'])

    sender_email = "dawoodzahid488@gmail.com"
    recipient_email = summary['user_email']
    subject = f"{summary['product_name']} - Review Sentiment Analysis Report"

    # Email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # HTML Email Body
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f2f2f2; margin: 0; padding: 0; color: #333333;">
        <div style="background-color: #ffffff; padding: 30px; text-align: center; border-bottom: 1px solid #ddd;">
            <img src="cid:logo" alt="Zaibten Logo" style="border-radius: 10px; width: 120px; height: 120px;"/>
            <h1 style="font-size: 26px; color: #333333; font-weight: 600; margin-top: 15px;">{summary['product_name']} Review Analysis</h1>
            <p style="font-size: 18px; color: #666666; margin-top: 10px;">Here is the sentiment analysis of your product reviews.</p>
        </div>
        <div style="padding: 30px; background-color: #ffffff; margin: 30px auto; width: 90%; max-width: 650px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <h2 style="font-size: 22px; color: #333333; margin-bottom: 15px;">Summary</h2>
            <p><strong>Good Reviews:</strong> <span style="color: #28a745;">{summary['good_reviews']}</span></p>
            <p><strong>Bad Reviews:</strong> <span style="color: #e74c3c;">{summary['bad_reviews']}</span></p>
            <p><strong>Neutral Reviews:</strong> {summary['neutral_reviews']}</p>
            <p><strong>Recommendation:</strong> {summary['recommendation']}</p>
        </div>
        <div style="text-align: center; margin-top: 30px;">
            <h2>Sentiment Distribution</h2>
            <img src="cid:sentiment_bar" alt="Sentiment Bar Chart" style="width: 100%; max-width: 600px; border-radius: 8px;"/>
            <h2>Sentiment Over Time</h2>
            <img src="cid:sentiment_line" alt="Sentiment Over Time Line Chart" style="width: 100%; max-width: 600px; border-radius: 8px;"/>
            <h2>Top 10 Words</h2>
            <img src="cid:wordcloud" alt="Top 10 Words Word Cloud" style="width: 100%; max-width: 600px; border-radius: 8px;"/>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    # Logo Attachment
    with open("static/images/logo.png", "rb") as logo_file:
        logo_data = logo_file.read()
        logo = MIMEImage(logo_data, name="logo.png")
        logo.add_header('Content-ID', '<logo>')
        msg.attach(logo)

    # Attach Graphs
    for graph_name, graph_buffer in graphs_data.items():
        graph_image = MIMEImage(graph_buffer.read(), name=f"{graph_name}.png")
        graph_image.add_header('Content-ID', f'<{graph_name}>')
        msg.attach(graph_image)

    # SMTP Sending
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, "yrcd wubo xysl jgbi")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# send_email_with_graphs(summary_data, {})


@app.route('/foodreviews', methods=['GET', 'POST'])
@login_required
def foodreviews():
    # Check if user is logged in
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']  # Assuming the user's name is stored in the database
    else:
        username = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            page_limit = int(request.form.get('page_limit', 1))  # Get the page limit from user input, default to 1
            if page_limit < 1 or page_limit > 200:  # Validate the input range
                raise ValueError("Page limit must be between 1 and 200.")
        except ValueError:
            flash("Invalid page limit. Please enter a number between 1 and 200.")
            return redirect(request.url)

        if url:
            try:
                review_data, positive_count, negative_count = foodreviewsscrape_reviews(url, page_limit)

                if review_data.empty:
                    raise ValueError("No review data was scraped.")

                # Generate graphs data
                graphs_data = foodreviewscreate_graphs(positive_count, negative_count, review_data)

                # Summary for the email
                summary = {
                    "product_name": "Yelp Business",  # Replace with actual product name if available
                    "good_reviews": positive_count,
                    "bad_reviews": negative_count,
                    "neutral_reviews": len(review_data) - (positive_count + negative_count),
                    "recommendation": "Recommended" if positive_count > negative_count else "Not Recommended",
                }

                # Generate and attach graphs for the email
                graph_buffer = BytesIO()  # Create an in-memory buffer for graphs
                plt.figure(figsize=(10, 6))  # Example figure for demonstration
                plt.bar(["Positive", "Negative"], [positive_count, negative_count], color=["green", "red"])
                plt.title("Sentiment Analysis")
                plt.savefig(graph_buffer, format='png')
                plt.close()
                graph_buffer.seek(0)  # Reset buffer position

                # Send email with the summary and graph
                send_email(summary, graph_buffer)

                # Render results to the user
                positive_reviews = review_data[review_data['classification'] == 'Positive']['review'].tolist()
                negative_reviews = review_data[review_data['classification'] == 'Negative']['review'].tolist()
                
                return render_template(
                    "foodreviews.html",
                    review_data=review_data.to_html(classes="table table-bordered"),
                    positive_count=positive_count,
                    negative_count=negative_count,
                    graphs_data=json.dumps(graphs_data),
                    positive_reviews=positive_reviews,
                    negative_reviews=negative_reviews,
                    recommendation=summary['recommendation'],
                    username=username,
                )
            except Exception as e:
                print(f"Error during scraping or processing: {e}")
                flash("An error occurred during scraping. Please try again.")
                return redirect(request.url)

    return render_template(
        "foodreviews.html",
        username=username,
        review_data=None,
        positive_count=0,
        negative_count=0,
        graphs_data=json.dumps({}),
        positive_reviews=[],
        negative_reviews=[],
    )


def foodreviewsscrape_reviews(url, page_limit=1, retries=3):
    all_reviews = []
    positive_count = 0
    negative_count = 0
    page = 0  # Start from the first page (start=0)

    while page // 10 < page_limit:  # Loop based on user input for page_limit
        try:
            # Modify the URL for pagination by adding 'start={page}'
            paginated_url = f"{url}?start={page}#reviews"

            print(f"Scraping reviews from page: {page // 10 + 1} (URL: {paginated_url})")

            # Make the request to the URL
            r = requests.get(paginated_url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            # Find all review elements (adjust the class name as per your specific case)
            regex = re.compile('.*comment.*')
            results = soup.find_all('p', {'class': regex}) or soup.find_all('p')
            reviews = [result.get_text(strip=True) for result in results if result.get_text(strip=True)]

            if not reviews:  # If no reviews are found, break the loop
                print("No more reviews found. Stopping scraping.")
                break

            # Print each review
            for review in reviews:
                print(review)

            # Process the reviews for classification
            review_data = pd.DataFrame({'review': reviews})
            review_data['classification'] = review_data['review'].apply(lambda x: foodreviewssentiment_score(x[:512]))

            # Filter out neutral reviews
            review_data = review_data[review_data['classification'] != 'Neutral']

            # Count the positive and negative reviews
            positive_count += len(review_data[review_data['classification'] == 'Positive'])
            negative_count += len(review_data[review_data['classification'] == 'Negative'])

            # Add the reviews to the list
            all_reviews.append(review_data)

            # Increment the page by 10 for the next URL
            page += 10

        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Error on page {page // 10 + 1}: {e}")
            time.sleep(2)  # Retry after waiting 2 seconds

    # Combine all the reviews from different pages into a single DataFrame
    if all_reviews:
        all_reviews_data = pd.concat(all_reviews, ignore_index=True)
        return all_reviews_data, positive_count, negative_count

    return pd.DataFrame(columns=['review', 'classification']), 0, 0











def mk_clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def mk_setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={random.randint(1200, 1600)},{random.randint(800, 1000)}")
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--blink-settings=imagesEnabled=true")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(window, 'chrome', { get: () => ({ runtime: {} }) });
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            window.navigator.chrome = { runtime: {} };
        """
    })
    return driver

def mk_simulate_human_behavior(driver):
    try:
        actions = ActionChains(driver)
        for _ in range(random.randint(2, 5)):
            actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).pause(random.uniform(0.2, 0.8))
        actions.perform()
        time.sleep(random.uniform(0.5, 1.5))
        scroll_amount = random.randint(100, 600)
        driver.execute_script(f"window.scrollTo(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 2))
        try:
            safe_element = driver.find_element(By.CSS_SELECTOR, 'body')
            actions.move_to_element(safe_element).click().perform()
            time.sleep(random.uniform(0.3, 1))
        except:
            pass
    except Exception as e:
        print(f"Error in human behavior simulation: {e}")

def mk_scrape_amazon_reviews(product_name, driver, max_stores=3, max_reviews=5):
    reviews = []
    search_url = f"https://www.amazon.com/s?k={quote(product_name)}"
    scrape_time = time.strftime("%I:%M %p %Z, %A, %B %d, %Y")

    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        mk_simulate_human_behavior(driver)

        product_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-no-outline')[:max_stores]
        if not product_links:
            return reviews

        product_urls = [link.get_attribute('href') for link in product_links]
        for url in product_urls:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                mk_simulate_human_behavior(driver)
                review_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-hook="review-body"]')[:max_reviews]
                if review_elements:
                    for review in review_elements:
                        reviews.append({'text': mk_clean_text(review.text), 'time': scrape_time})
                else:
                    reviews.append({'text': "No review found for this product.", 'time': scrape_time})
            except WebDriverException as e:
                reviews.append({'text': "Error retrieving review.", 'time': scrape_time})
            time.sleep(random.uniform(2, 5))

    except (TimeoutException, WebDriverException) as e:
        print(f"Error scraping Amazon search page: {e}")
    return reviews

def mk_scrape_ebay_reviews(product_name, driver, max_stores=3, max_reviews=5):
    reviews = []
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote(product_name)}"
    scrape_time = time.strftime("%I:%M %p %Z, %A, %B %d, %Y")

    try:
        driver.get(search_url)
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        mk_simulate_human_behavior(driver)

        product_links = driver.find_elements(By.CSS_SELECTOR, 'a.s-item__link')[:max_stores]
        if not product_links:
            return reviews

        product_urls = [link.get_attribute('href') for link in product_links]
        for url in product_urls:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                mk_simulate_human_behavior(driver)

                try:
                    feedback_tab = driver.find_element(By.CSS_SELECTOR, 'a[href*="#UserReviews"]')
                    actions = ActionChains(driver)
                    actions.move_to_element(feedback_tab).click().perform()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fdbk-container__details__comment")))
                    time.sleep(random.uniform(1, 3))
                    mk_simulate_human_behavior(driver)
                except:
                    pass

                review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.fdbk-container__details__comment')[:max_reviews]
                if review_elements:
                    for review in review_elements:
                        reviews.append({'text': mk_clean_text(review.text), 'time': scrape_time})
                else:
                    reviews.append({'text': "No review found for this product.", 'time': scrape_time})
            except WebDriverException as e:
                reviews.append({'text': "Error retrieving review.", 'time': scrape_time})
            time.sleep(random.uniform(2, 5))

    except (TimeoutException, WebDriverException) as e:
        print(f"Error scraping eBay search page: {e}")
    return reviews

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(product_name, product_status, total_good_reviews, total_bad_reviews):
    sender_email = "dawoodzahid488@gmail.com"
    recipient_email = get_logged_in_user_email()  # Your function to get logged in user's email
    
    if not recipient_email:
        print("No recipient email found; email not sent.")
        return
    
    password = "yrcd wubo xysl jgbi"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Review Analysis for Product: {product_name}"

    body = f"""
    Hello,

    Here is the review analysis summary for the product: {product_name}

    Recommendation Status: {product_status}
    Total Positive Reviews: {total_good_reviews}
    Total Negative Reviews: {total_bad_reviews}

    Thank you for using our service!

    Best regards,
    Your Review Analysis Team
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

@login_required
@app.route('/merge', methods=['GET', 'POST'])
def merge_reviews():
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        username = user['name']
    else:
        username = None

    if request.method == 'POST':
        product_name = request.form['product_name']
        driver = mk_setup_driver()
        reviews_amazon = mk_scrape_amazon_reviews(product_name, driver)
        reviews_ebay = mk_scrape_ebay_reviews(product_name, driver)
        driver.quit()

        reviews = []
        good_count = 0
        bad_count = 0

        for r in reviews_amazon:
            sentiment = TextBlob(r['text']).sentiment.polarity
            label = "Positive" if sentiment > 0.2 else "Negative" if sentiment < -0.2 else "Neutral"
            if label == "Positive":
                good_count += 1
            elif label == "Negative":
                bad_count += 1
            reviews.append({**r, 'source': 'Amazon', 'sentiment': label})

        for r in reviews_ebay:
            sentiment = TextBlob(r['text']).sentiment.polarity
            label = "Positive" if sentiment > 0.2 else "Negative" if sentiment < -0.2 else "Neutral"
            if label == "Positive":
                good_count += 1
            elif label == "Negative":
                bad_count += 1
            reviews.append({**r, 'source': 'eBay', 'sentiment': label})

        recommendation = "Recommended" if good_count > bad_count else "Not Recommended"

        send_email(product_name, recommendation, good_count, bad_count)

        return render_template('merge.html', reviews=reviews, product_name=product_name,
                               recommendation=recommendation, username=username,
                               reviews_amazon=reviews_amazon, reviews_ebay=reviews_ebay)

    # For GET requests also pass username!
    return render_template('merge.html', username=username)

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')


# if __name__ == '__main__':
#     app.run(debug=True)


