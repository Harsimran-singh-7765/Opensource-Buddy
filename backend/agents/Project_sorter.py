import os
import requests
import google.generativeai as genai
from crewai import Agent, Task, Crew , LLM
from google.generativeai import configure
from backend.agents.Git_collector import generate_search_queries,search_github_repos

from dotenv import load_dotenv





load_dotenv(dotenv_path=r".env")

# Now safely get the key
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
configure(api_key=os.environ["GEMINI_API_KEY"])
llm = LLM(model="gemini/gemini-1.5-flash")

configure(api_key=os.environ["GEMINI_API_KEY"])
llm = LLM(model="gemini/gemini-1.5-flash")

os.environ["CREWAI_TELEMETRY_DISABLED"] = "true"


def main():
    print("💬 Welcome to Open-Source Project Hunter!")
    user_topic = input("🧠 Enter a topic you're interested in: ")

    queries = generate_search_queries(user_topic)
    if not queries:
        print("❌ Couldn’t generate search queries.")
        return

    all_results = []
    for q in queries:
        repos = search_github_repos(q)
        all_results.extend(repos)

    unique_repos = list({r['url']: r for r in all_results}.values())
    if not unique_repos:
        print("😕 No repositories found.")
        return

    print(unique_repos)
    # Setup CrewAI Agent
    advisor = Agent(
        role="Open Source Project Advisor",
        goal="Help users find the best open-source repo {repos} to contribute to"
            "You need to analyze the the input list of repos and choose best to contribute , look for a project than a genric repo ",
        
        backstory="You are a skilled repo evaluator who helps people get started with the best open-source projects.",
        verbose=True,
        allow_delegation=False,
        llm = llm
        
    )

    task = Task(
        description="Evaluate open-source GitHub repos {repos} and recommend the best one for the user to contribute to."
                    "evaluate the discription and choose a project which is not a list of something but a Produt based project",
        expected_output="A recommendation message with repo name, stars, description, and link.",
        agent=advisor,
        inputs = all_results
    )

    crew = Crew(
        agents=[advisor],
        tasks=[task],
        verbose=True
    )

    print("\n🤖 Evaluating repositories... Hold tight!\n")
    final_output = crew.kickoff(inputs={"repos": unique_repos})

    print("\n✅ Final Recommendation:\n")
    print(final_output)


if __name__ == "__main__":
    main()
