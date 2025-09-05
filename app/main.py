from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import os
from transformers import pipeline
import torch
from collections import defaultdict

from .models import TextInput, SentimentResponse, BatchTextInput, BatchSentimentResponse

# Configure logging
import os
log_file = os.path.expanduser('~/app.log') if os.access('/app', os.W_OK) else None

handlers = [logging.StreamHandler()]
if log_file:
    handlers.append(logging.FileHandler(log_file))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sentiment Analysis API",
    description="A REST API for sentiment analysis using transformers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
sentiment_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Load the model on startup"""
    global sentiment_pipeline
    try:
        logger.info("Loading sentiment analysis model...")
        # Use a very lightweight model for faster deployment
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if torch.cuda.is_available() else -1
        )
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        # Fallback to a simpler model
        sentiment_pipeline = pipeline("sentiment-analysis")
        logger.info("Loaded fallback model")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Sentiment Analysis API is running!",
        "version": "1.0.0",
        "endpoints": ["/predict", "/predict-batch", "/health"]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": sentiment_pipeline is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=SentimentResponse)
async def predict_sentiment(input_data: TextInput):
    """Predict sentiment for a single text"""
    try:
        logger.info(f"Processing sentiment prediction for text length: {len(input_data.text)}")
        
        if not sentiment_pipeline:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        if not input_data.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Get prediction
        result = sentiment_pipeline(input_data.text)[0]
        
        # Map labels (model-specific)
        label_mapping = {
            "LABEL_0": "negative",
            "LABEL_1": "neutral", 
            "LABEL_2": "positive",
            "NEGATIVE": "negative",
            "POSITIVE": "positive"
        }
        
        sentiment = label_mapping.get(result['label'], result['label'].lower())
        
        response = SentimentResponse(
            text=input_data.text,
            sentiment=sentiment,
            confidence=round(result['score'], 4),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Prediction completed: {sentiment} (confidence: {result['score']:.4f})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in sentiment prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/predict-batch", response_model=BatchSentimentResponse)
async def predict_sentiment_batch(input_data: BatchTextInput):
    """Predict sentiment for multiple texts"""
    try:
        logger.info(f"Processing batch prediction for {len(input_data.texts)} texts")
        
        if not sentiment_pipeline:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        if len(input_data.texts) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
        
        results = []
        for text in input_data.texts:
            if text.strip():  # Skip empty texts
                result = sentiment_pipeline(text)[0]
                
                label_mapping = {
                    "LABEL_0": "negative",
                    "LABEL_1": "neutral",
                    "LABEL_2": "positive", 
                    "NEGATIVE": "negative",
                    "POSITIVE": "positive"
                }
                
                sentiment = label_mapping.get(result['label'], result['label'].lower())
                
                results.append(SentimentResponse(
                    text=text,
                    sentiment=sentiment,
                    confidence=round(result['score'], 4),
                    timestamp=datetime.now().isoformat()
                ))
        
        response = BatchSentimentResponse(
            results=results,
            total_processed=len(results)
        )
        
        logger.info(f"Batch prediction completed for {len(results)} texts")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch sentiment prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Metrics tracking
request_count = defaultdict(int)

@app.middleware("http")
async def count_requests(request, call_next):
    request_count[request.url.path] += 1
    response = await call_next(request)
    return response

@app.get("/metrics")
async def get_metrics():
    return {"request_counts": dict(request_count)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)