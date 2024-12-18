# llm-fake-news-detector
A fake news detector using a LLM (GPT).

# Set-up tutorial
Before starting up, you should create a .env file and a virtual environment. In a bash:
- Create a .env file with your OpenAI API key.
```
touch .env
echo "OPENAI_API_KEY=<your-openai-api-key-here>" > .env
```

- Create a virtual enviroment and install dependencies.
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

- Finally, start the API:
```
source .venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --timeout-keep-alive 60
```