from google import genai

import os
os.environ["GEMINI_API_KEY"] = ""

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

while True:

    prompt = """Act like you're completing sentences and correcting mistakes.
    what i want you to do is to feel my sentences for search just like google search and typing error correction.
    i want 5 suggestions, sort the suggestions from the most common to the least.
    i want the sugggestion's by order with nothing by the suggestions.
    do this for everything im gonna enter you from now.
    the input is: """

    inp = input('quary: ')

    prompt += inp

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )

    print(response.text)

