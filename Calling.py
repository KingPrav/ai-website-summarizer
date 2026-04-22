import os
from dotenv import load_dotenv
from scraper import fetch_website_contents
from IPython.display import Markdown, display
from openai import OpenAI

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")

openai = OpenAI()




system_prompt = "Be a funny and snarky assistant"
user_prompt = """
Here is the url of the website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.
"""

# Step 2: Make the messages list

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt + website}
    ]

# Step 3: Call OpenAI
# response =
def summarize(url):
    website = fetch_website_contents(url)
    response = openai.chat.completions.create(
        model = "gpt-4.1-mini",
        messages = messages_for(website)
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(summarize("https://praveenraj-2002.online/"))