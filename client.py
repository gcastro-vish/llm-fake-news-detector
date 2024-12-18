from dotenv import load_dotenv
load_dotenv()
from httpx import ReadTimeout, RequestError
from timeit import default_timer as timer
from typing import List, Dict, Union
from csv import QUOTE_ALL
import os
import csv
import httpx
import asyncio
import pathlib

# Vars
URL = "http://127.0.0.1:8000/v1/analyze/"
HEADERS = {"Authorization": f"Bearer {os.getenv("OPENAI_API_KEY")}"}
ROOT_PATH = pathlib.Path(__name__).parent.resolve()
DATA_PATH = os.path.join(ROOT_PATH, "data")
OUTPUT_PATH = os.path.join(ROOT_PATH, "output")

# Functions
def read_txt(file_path: str) -> List[str]:
    with open(file_path, newline='') as f:
        csv_reader = csv.reader(f)
        return list(csv_reader)

async def request_api(headline: str, article: str) -> Dict[str, Union[int, str]]:
    json_data = {"headline": headline, "article": article}

    timeout = httpx.Timeout(30.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(URL, headers=HEADERS, json=json_data)
            return response.json()
    except ReadTimeout:
        print(f"Request timed out for article: {article}")
        return {"error": "Request timed out"}
    except RequestError as e:
        print(f"Request error occurred: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

async def analyze_news(data_dict: Dict[str, List[str]]) -> Dict[str, List[dict]]:
    output = {}
    for label, data in data_dict.items():
        output[label] = []
        tasks = [request_api(row[0], row[1]) for row in data[1:]]
        responses = await asyncio.gather(*tasks)
        output[label].extend(responses)
    return output

def dump_analysis(data_dict: Dict[str, List[str]], news_analysis: Dict[str, List[dict]]) -> None:
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    output_file = os.path.join(OUTPUT_PATH,'output.csv')

    int_label = {"trues": 0, "fakes": 1}
    
    rows = []
    
    for str_label in ['trues', 'fakes']:
        columns = data_dict[str_label][0]
        for i, data in enumerate(data_dict[str_label][1:], start=0):
            analysis = news_analysis[str_label][i]
            row = {col: val for col, val in zip(columns, data)}
            row['true_label'] = int_label[str_label]
            row.update(analysis)
            rows.append(row)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

def analyze_results(news_analysis: Dict[str, List[dict]]) -> Dict[str, float]:
    # using 1 as aux value
    TP = len([1 for analysis in news_analysis["fakes"] if analysis["PREDICTION"]])
    FN = len([1 for analysis in news_analysis["fakes"] if not analysis["PREDICTION"]])
    TN = len([1 for analysis in news_analysis["trues"] if not analysis["PREDICTION"]])
    FP = len([1 for analysis in news_analysis["trues"] if analysis["PREDICTION"]])

    accuracy = (TP + TN) / (TP + TN + FP + FN)
    precision = TP / (TP + FP) if (TP + FP) != 0 else 0
    recall = TP / (TP + FN) if (TP + FN) != 0 else 0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) != 0 else 0

    return {"Accuracy": accuracy, "Precision": precision, "Recall": recall, "F1-Score": f1_score}

async def main():
    """
    Read data from `data/` folder, request `http://127.0.0.1:8000/v1/analyze/`, dump a csv with results and then print a small report with some statistics.
    Each `.txt` in `data/` contains 100 articles. This means running this code will result in a total of 200 gpt-4o-mini-2024-07-18 callings.
    """
    true_path = os.path.join(DATA_PATH, "true.txt")
    fake_path = os.path.join(DATA_PATH, "fake.txt")

    data_dict = {"trues": read_txt(true_path), "fakes": read_txt(fake_path)}

    news_analysis = await analyze_news(data_dict)

    dump_analysis(data_dict, news_analysis)

    report = analyze_results(news_analysis)

    print(report)

if __name__ == "__main__":
    start = timer()
    asyncio.run(main())
    stop = timer()
    print(f"Processing time: {stop - start}", )