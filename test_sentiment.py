from utils.sentiment import analyze_sentiment, analyze_sentiment_with_threshold

if __name__ == "__main__":
    print("Device set to use cpu")

    print("Testing analyze_sentiment:")
    print(analyze_sentiment("This system is amazing!"))
    print(analyze_sentiment("I am very disappointed with this service."))
    print(analyze_sentiment("It works fine, nothing special."))

    print("\nTesting analyze_sentiment_with_threshold:")
    print(analyze_sentiment_with_threshold("This system is amazing!"))
    print(analyze_sentiment_with_threshold("I am very disappointed with this service."))
    print(analyze_sentiment_with_threshold("It works fine, nothing special."))
