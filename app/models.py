from pydantic import BaseModel
from typing import List, Optional

class TextInput(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    emotions: dict  # frustrated, excited, confident, uncertain
    timestamp: str

class BatchTextInput(BaseModel):
    texts: List[str]

class BatchSentimentResponse(BaseModel):
    results: List[SentimentResponse]
    total_processed: int