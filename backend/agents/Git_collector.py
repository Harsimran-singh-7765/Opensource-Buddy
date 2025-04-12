import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# === ENV and GEMINI Setup ===
load_dotenv(dotenv_path=".env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN")
token = os.getenv("GITHUB_TOKEN")
model = genai.GenerativeModel("gemini-2.0-flash")

# === STEP 1: Generate smart search queries ===
def generate_search_queries(user_topic):
    prompt = f"""
You are helping users discover *contributable*, *active* open-source GitHub repositories based on the topic: "{user_topic}".

✅ Only suggest queries that will find actual *projects*, not just libraries/tools/tutorials.  
✅ Focus on repos that have README, stars, issues, and contribution potential.  
✅ Avoid official repos like pandas, sklearn etc.  
✅ Be developer-minded while suggesting.

Output ONLY 10 GitHub search queries in a raw Python list. No extra text.

Example:
["site:github.com machine learning project stars:>100 fork:false", 
 "open source web app in:readme stars:>50", 
 "issue:open bug tracker stars:>20", 
 "python automation site:github.com stars:>75"]
"""
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = "\n".join([line for line in raw_text.splitlines() if not line.startswith("```")])

    try:
        queries = eval(raw_text)
        return queries if isinstance(queries, list) else []
    except Exception as e:
        print("⚠️ Error parsing Gemini response:\n", raw_text)
        print("Exception:", e)
        return []

# === STEP 2: Search GitHub with filters ===
import requests

def search_github_repos(query):
    print(f"🔍 Searching GitHub for: {query}")
    
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"⚠️ GitHub API Error [{response.status_code}]: {response.text}")
        return []

    data = response.json()
    repos = data.get("items", [])
    
    # Filter: no forks + open issues > 3
    return [
        {
            "name": repo["name"],
            "description": repo["description"],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "open_issues": repo["open_issues_count"]
        }
        for repo in repos
        if not repo["fork"] and repo.get("open_issues_count", 0) > 3
    ][:5]  # Top 5 per query

# === STEP 3: Master function to call ===
def search_and_filter_repos(user_topic):
    print("💬 Welcome to Open-Source Project Hunter!")
    print(f"🧠 Topic: {user_topic}")

    queries = generate_search_queries(user_topic)
    if not queries:
        print("❌ Couldn't generate search queries.")
        return []

    all_results = []
    for q in queries:
        repos = search_github_repos(q)
        all_results.extend(repos)

    # Remove duplicates based on URL
    unique_repos = list({r['url']: r for r in all_results}.values())
    
    if not unique_repos:
        print("😕 No repositories found.")
        return []

    print(f"✅ Found {len(unique_repos)} unique repositories!\n")
    return unique_repos
