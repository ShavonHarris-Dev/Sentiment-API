# Sentiment-API

A RESTful API for sentiment analysis.

## Overview

Sentiment-API lets you analyze the sentiment of text input and returns whether the sentiment is positive, negative, or neutral. This API is ideal for integrating into applications that process user feedback, social media posts, reviews, or any other text data.

## Features

- Simple API for sentiment analysis
- Returns sentiment label and score for input text
- Easy to integrate into web or mobile apps

## Technologies

- Programming Language: Python
- Framework: Flask (or FastAPI if applicable)
- Sentiment Analysis Library: (e.g., TextBlob, VADER, NLTK)

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/ShavonHarris-Dev/Sentiment-API.git
    cd Sentiment-API
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the API locally:**
    ```bash
    python app.py
    ```
    The API will be available at `http://localhost:5000` (default).

2. **Analyze sentiment:**

    **Request**
    ```
    POST /analyze
    Content-Type: application/json

    {
      "text": "This is an amazing project!"
    }
    ```

    **Response**
    ```json
    {
      "sentiment": "positive",
      "score": 0.91
    }
    ```

## Contributing

Contributions are welcome! Open a pull request or issue for suggestions or improvements.

## License

This project is licensed under the MIT License.

## Author

Shavon Harris  
GitHub: [ShavonHarris-Dev](https://github.com/ShavonHarris-Dev)
