# llm-fake-news-detector
An API that uses a Large Language Model (GPT) to detect fake news from a given article.

## Set-up Tutorial
To set up and run the Fake News Detector API, follow these steps:

#### 1. Create the `.env` file
Create a `.env` file to store your OpenAI API key for authentication.

```bash
touch .env                                                  # Create a .env file
echo "OPENAI_API_KEY=<your-openai-api-key-here>" > .env     # Insert your OpenAI API Key into .env
```

#### 2. Create a virtual environment and install dependencies.
```bash
python3 -m venv .venv               # Create virtual environment
source .venv/bin/activate           # Activate the virtual environment
pip install -r requirements.txt     # Install dependencies
deactivate                          # Deactivate the virtual environment after installation
```

#### 3. Finally, start the API:
```bash
source .venv/bin/activate                                                       # Activate the virtual environment
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --timeout-keep-alive 60     # Start API
```

Your API is now running locally at http://127.0.0.1:8000.

## API Usage
To analyze whether a news article is fake, send a POST request to the following endpoint:
```
POST http://127.0.0.1:8000/v1/analyze/
```

#### Request Headers
The request must include the following header for authentication:
```
Authorization: Bearer <OPENAI_API_KEY>
```

#### Request Body:
The body of the request must include the headline (article headline) and article (full text of the article). Here's an example:
```json
{
    "headline": "Example of a misleading headline",
    "article": "This is the full content of the article that may or may not be fake."
}
```

#### Request Reponse:
The request response is a json including the following keys:
```json
{
    "PREDICTION": "<"1" indicates evidence suggesting the article is fake news, and "0" otherwise>",
    "JUSTIFICATION": "<Brief justification of prediction made.>"
}
```

#### Example call (Python):
You can use the client.py script included in the project to easily make API requests from a `.txt` file. However, here's a more straightforward example:
```python
import requests

url = "http://127.0.0.1:8000/v1/analyze/"
headers = {
    "Authorization": "Bearer <your-openai-api-key>"
}
data = {
    "headline": "Example of a misleading headline",
    "article": "This is the full content of the article that may or may not be fake."
}

response = requests.post(url, json=data, headers=headers)

print(response.json())
```

## Reminder
Never expose your `.env` file in public repositories, as it can compromise the security of your application.
