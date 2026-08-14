import requests
import json

MODEL = "qwen2.5-coder:7b"
URL = "http://localhost:11434/api/generate"

print("🤖 My Coding AI")
print("Type 'exit' to quit.")

conversation = []

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("AI: Goodbye! 👋")
        break

    conversation.append(f"User: {question}")

    system_prompt = """
You are Coding AI, a friendly programming tutor.

Your job is to help the user learn programming.

Rules:
- Explain concepts in simple language.
- Assume the user is a beginner.
- Give examples when useful.
- Explain code you provide.
- Help find and fix errors.
- Remember the conversation.
"""

    history = "\n".join(conversation)

    prompt = system_prompt + "\n\nConversation:\n" + history + "\nAI:"

    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }

    print("\nAI: ", end="", flush=True)

    try:
        response = requests.post(
            URL,
            json=data,
            stream=True,
            timeout=300
        )

        response.raise_for_status()

        full_answer = ""

        for line in response.iter_lines():
            if line:
                result = json.loads(line.decode("utf-8"))
                text = result["response"]

                print(text, end="", flush=True)
                full_answer += text

        conversation.append(f"AI: {full_answer}")

        print()

    except requests.exceptions.Timeout:
        print("\nAI took too long to respond.")

    except requests.exceptions.ConnectionError:
        print("\nAI can't connect to Ollama.")

    except Exception as error:
        print("\nError:", error)