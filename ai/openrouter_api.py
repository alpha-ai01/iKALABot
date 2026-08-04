import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1'
)

def generate_openrouter_response(prompt, is_x_search=False):
    model = 'openai/gpt-4o-mini'

    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    return response.choices[0].message.content.strip()
