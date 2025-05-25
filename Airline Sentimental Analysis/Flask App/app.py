from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Initialize Flask app
app = Flask(__name__)

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Function to scrape reviews
def scrape_reviews(base_url, pages, page_size):
    reviews = []
    for i in range(1, pages + 1):
        url = f"{base_url}/page/{i}/?sortby=post_date%3ADesc&pagesize={page_size}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for para in soup.find_all("div", {"class": "text_content"}):
            reviews.append(para.get_text(strip=True))
    return reviews

# Function to analyze sentiment
def analyze_sentiment(review):
    result = sentiment_pipeline(review[:512])[0]
    return result['label'], result['score']

# Function to create a word cloud
def create_wordcloud(reviews):
    text = " ".join(reviews)
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    img = io.BytesIO()
    plt.figure(figsize=(8, 4))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# Function to create bar chart
def create_bar_chart(sentiment_counts):
    labels = list(sentiment_counts.keys())
    values = list(sentiment_counts.values())
    img = io.BytesIO()
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['green', 'red', 'blue'])
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    plt.title("Sentiment Distribution")
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# Function to create scatter plot
def create_scatter_plot(df):
    img = io.BytesIO()
    colors = df['sentiment'].map({'POSITIVE': 'green', 'NEGATIVE': 'red', 'NEUTRAL': 'blue'})
    plt.figure(figsize=(8, 4))
    plt.scatter(df.index, df['confidence'], c=colors, alpha=0.6)
    plt.xlabel("Review Index")
    plt.ylabel("Confidence Score")
    plt.title("Confidence Scores for Sentiments")
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()


# Function to analyze sentiment
def analyze_sentiment(review):
    result = sentiment_pipeline(review[:512])[0]
    return result['label'], result['score']

# Function to generate base64 graph images
def generate_plot(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()


def send_email_with_review_summary(product_name, positive_count, negative_count, recommendation, reviews, graphs):
    sender_email = "muzamilkhanofficial786@gmail.com"
    recipient_email = "muzamilkhanofficials@gmail.com"
    sender_password = "iaqu xvna tpix ugkt"
    
    subject = f"{product_name} - Review Sentiment Analysis Report"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>{product_name} - Sentiment Analysis</h2>
        <p><strong>Positive Reviews:</strong> {positive_count}</p>
        <p><strong>Negative Reviews:</strong> {negative_count}</p>
        <p><strong>Recommendation:</strong> {recommendation}</p>
        <h3>Graphs</h3>
        <img src="cid:sentiment_bar" alt="Sentiment Bar Chart">
        <img src="cid:sentiment_pie" alt="Sentiment Pie Chart">
        <img src="cid:wordcloud" alt="Word Cloud">
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))
    
    # Attach graphs
    for graph_name, graph_buffer in graphs.items():
        img_data = base64.b64decode(graph_buffer)  # Decode the base64 image string
        image = MIMEImage(img_data, name=f"{graph_name}.png")
        image.add_header('Content-ID', f"<{graph_name}>")
        msg.attach(image)
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Define Flask routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        base_url = request.form.get('base_url')
        pages = int(request.form.get('pages', 2))
        page_size = int(request.form.get('page_size', 100))

        # Scrape reviews
        reviews = scrape_reviews(base_url, pages, page_size)
        if not reviews:
            return render_template('index.html', error="No reviews found.")

        # Analyze sentiment
        review_data = []
        for review in reviews:
            sentiment, confidence = analyze_sentiment(review)
            review_data.append({"review": review, "sentiment": sentiment, "confidence": confidence})

        # Convert to DataFrame
        df = pd.DataFrame(review_data)

        # Count sentiments
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        sentiment_counts.setdefault("POSITIVE", 0)
        sentiment_counts.setdefault("NEGATIVE", 0)
        sentiment_counts.setdefault("NEUTRAL", 0)

        # Generate visualizations
        wordcloud_image = create_wordcloud(reviews)
        bar_chart_image = create_bar_chart(sentiment_counts)
        scatter_plot_image = create_scatter_plot(df)

        # Line graph (sentiment trends)
        line_fig = plt.figure()
        df['sentiment'].value_counts().plot(kind='line', marker='o', title='Sentiment Trends')
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        line_graph = generate_plot(line_fig)

        # Pie chart (sentiment distribution)
        pie_fig = plt.figure()
        plt.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), autopct='%1.1f%%', startangle=140)
        plt.title('Sentiment Distribution')
        pie_graph = generate_plot(pie_fig)

        # Recommendation logic
        recommendation = "Recommended" if sentiment_counts["POSITIVE"] > sentiment_counts["NEGATIVE"] else "Not Recommended"

        # Generate email graphs
        graphs = {
            "sentiment_bar": bar_chart_image,
            "sentiment_pie": pie_graph,
            "wordcloud": wordcloud_image
        }

        # Send email
        send_email_with_review_summary(
            product_name="Sample Product",
            positive_count=sentiment_counts["POSITIVE"],
            negative_count=sentiment_counts["NEGATIVE"],
            recommendation="Recommended" if sentiment_counts["POSITIVE"] > sentiment_counts["NEGATIVE"] else "Not Recommended",
            reviews=reviews,
            graphs=graphs
        )

        # Render results
        return render_template(
            'index.html',
            sentiment_counts=sentiment_counts,
            reviews=review_data,
            recommendation=recommendation,
            wordcloud_image=wordcloud_image,
            bar_chart_image=bar_chart_image,
            scatter_plot_image=scatter_plot_image,
            line_graph=line_graph,
            pie_graph=pie_graph
        )

    return render_template('index.html')

def model(review_texts):
    # Load tokenizer and model (make sure paths are correct)
    tokenizer = AutoTokenizer.from_pretrained("best.pt") # type: ignore
    model = AutoModelForSequenceClassification.from_pretrained("best.pt") # type: ignore

    sentiments = []

    for text in review_texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1) # type: ignore
        pred_class = torch.argmax(probs, dim=1).item() # type: ignore

        # Map the prediction to sentiment label
        if pred_class == 0:
            sentiments.append("Negative")
        elif pred_class == 1:
            sentiments.append("Neutral")
        else:
            sentiments.append("Positive")

    return sentiments

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
