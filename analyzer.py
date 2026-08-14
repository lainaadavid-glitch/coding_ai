import requests

MODEL = "qwen2.5-coder:7b"
URL = "http://localhost:11434/api/generate"


def analyze_code(code):
    prompt = f"""
You are an expert Python debugging assistant.

Analyze the following Python code.

Do these things:

1. Find syntax errors.
2. Find logical errors.
3. Explain each problem simply.
4. Provide corrected code.
5. Explain what you changed.

Code:

```python
{code}