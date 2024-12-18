from openai import AsyncOpenAI
from typing import Dict, Union
import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define the log message format
    datefmt='%Y-%m-%d %H:%M:%S',  # Define the date format
    handlers=[
        logging.StreamHandler()  # Output logs to the console
    ]
)
logger = logging.getLogger(__name__)

# Functions
def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def make_analysis(headline: str, article: str) -> Dict[str, Union[int, str]]:
    client = get_openai_client()

    tools = [
        {
            "type": "function",
            "function": {
            "name": "analyze_news",
            "description": "Analyze if the given headline and/or article are fake news.",
            "parameters": {
                "type": "object",
                "properties": {
                    "PREDICTION": {
                        "type": "integer",
                        "description": "Flag if the headline and/or article is a fake news."
                    },
                    "JUSTIFICATION": {
                        "type": "string",
                        "description": "Brief justification of the analysis made."
                    }
                },
                "required": ["PREDICTION", "JUSTIFICATION"]
            }
            }
        }
    ]
    tool_choice = {"type": "function", "function": {"name": "analyze_news"}}
    
    messages=[{
        "role": "system","content": """
You are an investigator specializing in detecting fake news. Your task is to analyze whether the given headline and article are credible or potentially fake news. Provide a detailed evaluation based on the following factors:\nHeadline vs. Content Consistency: compare the headline with the content of the article. Does the content support the claims made in the headline, or is the headline sensationalized or misleading? Is there any exaggeration or contradiction between the headline and the body of the article?\nSource and Author Credibility: check the credibility of the source. Is the article published by a reputable news organization or website, or is it from an unreliable or lesser-known source? Evaluate the author's credibility. Are they an expert in the field they are writing about, and do they have a professional track record?\nEmotional Manipulation: analyze the tone and language of both the headline and the article. Does the article use emotional or polarizing language to evoke a strong emotional response (fear, anger, etc.) rather than providing neutral, objective reporting?\nFormatting: check if the article uses sensational formatting (e.g., all caps, excessive punctuation, strange layout) that might indicate a clickbait approach.\nLogical Fallacies: look for any logical inconsistencies in the article. Are there false dichotomies, oversimplifications, or misleading comparisons that weaken the arguments or conclusions?\nConspiracy Theories: does the article promote or support any conspiracy theories? Are there unverified, highly speculative claims without substantial evidence?. Your analysis must not be superficial and should be based on the data presented.\n
Your response should include two values:\n"PREDICTION" <integer>: ("1" or "0"), where "1" indicates evidence suggesting the article is fake news, and "0" indicates no evidence of the article being fake news.\n"JUSTIFICATION" <string>: Provide a brief explanation supporting your analysis.
    """},
    {"role":"user","content":f'Headline: "{headline}"\nArticle: "{article}"'}
    ]

    chat_completion = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini-2024-07-18",
        tools=tools,
        tool_choice=tool_choice,
        temperature=0
    )

    function_args = json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)
    logger.info("function_args: %s", function_args)
    
    return function_args