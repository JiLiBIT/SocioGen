import requests
import json

# in terminal run:
# ollama serve
# ollama run deepseek-r1:1.5b


url = "http://localhost:11434/api/chat"

def deepseekR1(prompt):
    data = {
        "model": "deepseek-r1:14b",
        "messages": [
            {
                "role": "user",
                "content": prompt

            }
        ],
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["message"]["content"]

if __name__ == "__main__":
    response = deepseekR1("who wrote the book godfather")
    print(response)