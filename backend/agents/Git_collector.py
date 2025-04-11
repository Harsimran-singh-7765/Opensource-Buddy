import os
import requests
import google.generativeai as genai
from crewai import Agent, Task, Crew , LLM
from google.generativeai import configure

from dotenv import load_dotenv





load_dotenv(dotenv_path=r".env")

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")





def generate_search_queries(user_topic):
    prompt = f"""
    The user wants to discover useful and active open-source GitHub repositories related to: "{user_topic}"

    👉 Provide 10 smart GitHub search queries as a pure Python list of strings. No explanations.
    LOOK FOR REPO WHOSE TITLE ARE ACTUALLY A PROJECT ,check the discription of repo as well
    Example: ["machine learning site:github.com stars:>100", "AI tools in:readme stars:>50", "chatbot language:Python"]
    """
    response = model.generate_content(prompt)
    text = response.text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        lines = [line for line in lines if not line.startswith("```")]
        text = "\n".join(lines).strip()

    try:
        return eval(text)
    except Exception as e:
        print("Error parsing Gemini response:", text)
        print("Exception:", e)
        return []




def search_github_repos(keyword):
    print(f"🔍 Searching GitHub for: {keyword}")
    url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if "items" not in data:
        print("⚠️ GitHub API Error:", data)
        return []

    return [
        {
            "name": repo["name"],
            "description": repo["description"],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"]
        }
        for repo in data["items"][:5]
    ]


