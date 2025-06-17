import requests

class decideSlideType:
    def __init__(self, api_key, endpoint_url, api_version="2025-01-01-preview"):
        self.api_key = api_key
        self.endpoint = endpoint_url
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

    def DecideSlideType(self, context):
        prompt = f"""
This is the data of Document Slide:
{context}

Your task is to categorize each slide based on its content and intent into one of the following categories:
1. Introduction
2. Insight
3. Solution

return only one word of above slide types without any explaination.
"""
        data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 2000
        }

        response = requests.post(self.endpoint, headers=self.headers, json=data)

        if response.status_code == 200:
            text = response.json()['choices'][0]['message']['content']
            print(f'✅ Slide Type Generated : {text}')
            return text
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")