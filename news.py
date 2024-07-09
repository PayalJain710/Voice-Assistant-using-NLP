import requests

from textblob import TextBlob

def get_news(limit):
    """Fetch top news headlines with sentiment analysis using News API"""
    base_url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',
        'apiKey': 'API_KEY',
        'pageSize': limit
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        if articles:
            top_headlines = "Here are the top headlines with their sentiments:\n"
            for idx, article in enumerate(articles[:limit], start=1):
                headline = article['title']
                analysis = TextBlob(headline)
                sentiment = "positive" if analysis.sentiment.polarity > 0 else "negative" if analysis.sentiment.polarity < 0 else "neutral"
                top_headlines += f"{idx}. {headline} (Sentiment: {sentiment})\n"
            return top_headlines
        else:
            return "No news articles found."
    else:
        return "Unable to fetch news. Please try again later."
