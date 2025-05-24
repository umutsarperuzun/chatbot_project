from app import app, db  # Import the Flask application and database object
from models import SentimentLog  # Import the SentimentLog model
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

# Start the Flask 
with app.app_context():
    logs = SentimentLog.query.all()

    if not logs:
        print("No sentiment data available in the database.")
    else:
        # Convert data 
        data = [{
            "message": log.message,
            "sentiment": log.sentiment,
            "confidence": log.confidence,
            "timestamp": log.timestamp
        } for log in logs]
        df = pd.DataFrame(data)

        #Sentiment Distribution
        sentiment_counts = df['sentiment'].value_counts()
        colors = ['green', 'blue', 'red'][:len(sentiment_counts)]
        sentiment_counts.plot(kind='bar', color=colors)
        plt.title("Sentiment Distribution")
        plt.xlabel("Sentiment")
        plt.ylabel("Frequency")
        plt.show()

        #Time-Based Sentiment 
        if 'timestamp' in df.columns and not df['timestamp'].empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Group by sentiment by minute
            minute_sentiment = df.groupby('sentiment').resample('T').size().unstack(0).fillna(0)
            minute_sentiment.plot(kind='line', figsize=(10, 6))
            plt.title("Sentiment Trends Over Minutes")
            plt.xlabel("Time (Minutes)")
            plt.ylabel("Message Count")
            plt.legend(title="Sentiment")
            plt.grid(True)
            plt.show()
        else:
            print("Timestamp data is missing or empty.")

        #Confidence Score Distribution
        plt.hist(df['confidence'], bins=10, color='purple', alpha=0.7)
        plt.title("Confidence Score Distribution")
        plt.xlabel("Confidence Score")
        plt.ylabel("Frequency")
        plt.show()

        #Average Confidence Score by Sentiment
        average_confidence = df.groupby('sentiment')['confidence'].mean()
        average_confidence.plot(kind='bar', color=['green', 'blue', 'red'])
        plt.title("Average Confidence Score by Sentiment")
        plt.xlabel("Sentiment")
        plt.ylabel("Average Confidence Score")
        plt.show()

        # Daily Sentiment Distribution
        daily_sentiment = df.groupby([df['timestamp'].dt.date, 'sentiment']).size().unstack().fillna(0)
        daily_sentiment.plot(kind='area', stacked=True, figsize=(10, 6), alpha=0.5)
        plt.title("Daily Sentiment Distribution")
        plt.xlabel("Date")
        plt.ylabel("Message Count")
        plt.legend(title="Sentiment")
        plt.show()

        #Word Cloud for Negative Messages
        negative_messages = " ".join(df[df['sentiment'] == "NEGATIVE"]['message'])
        wordcloud = WordCloud(width=800, height=400, background_color='black').generate(negative_messages)

        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title("Word Cloud for Negative Messages")
        plt.show()

        #Daily Average Confidence Score
        daily_avg_confidence = df.groupby(df['timestamp'].dt.date)['confidence'].mean()
        daily_avg_confidence.plot(kind='line', figsize=(10, 6), color='orange')
        plt.title("Daily Average Confidence Score")
        plt.xlabel("Date")
        plt.ylabel("Average Confidence Score")
        plt.show()

        #Message Length and Sentiment Relationship
        df['message_length'] = df['message'].apply(len)
        df.boxplot(column='message_length', by='sentiment', grid=False, color=dict(boxes='blue', whiskers='black', medians='red'))
        plt.title("Message Length by Sentiment")
        plt.suptitle("")  
        plt.xlabel("Sentiment")
        plt.ylabel("Message Length")
        plt.show()
