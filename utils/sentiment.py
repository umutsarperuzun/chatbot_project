from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Define the model 
MODEL_PATH = "./models"  

# Define the pipeline 
def get_sentiment_analysis_pipeline():
    """
    Create and return the sentiment analysis pipeline.
    """
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Initialize the pipeline 
sentiment_analysis = get_sentiment_analysis_pipeline()

def analyze_sentiment(message):
    """
    Analyze sentiment of a message and return the label and confidence score.
    """
    try:
        #preloaded pipeline
        result = sentiment_analysis(message)[0]
        return result['label'], result['score']
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "UNKNOWN", 0.0

def analyze_sentiment_with_threshold(message, neutral_threshold=0.7):
    """
    Analyze the sentiment of a user message and apply a threshold to classify neutral messages.
    """
    try:
        #preloaded pipeline
        result = sentiment_analysis(message)[0]
        confidence = result['score']
        label = result['label']  

        # Handle NEUTRAL class using the threshold
        if label == "LABEL_1" or confidence < neutral_threshold:  
            return "NEUTRAL", confidence
        elif label == "LABEL_0":  
            return "NEGATIVE", confidence
        elif label == "LABEL_2": 
            return "POSITIVE", confidence

        # Fallback classification
        return label, confidence
    except Exception as e:
        print(f"Error analyzing sentiment with threshold: {e}")
        return "UNKNOWN", 0.0


