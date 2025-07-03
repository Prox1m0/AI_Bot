from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  model="openrouter/cypher-alpha:free",
  messages=[
    {
      "role": "user",
      "content": "В чем смысл жизни?"
    }
  ]
)
print(completion.choices[0].message.content)