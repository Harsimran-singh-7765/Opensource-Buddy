import os
import requests
import google.generativeai as genai
from crewai import Agent, Task, Crew , LLM
from google.generativeai import configure
from backend.agents.Git_collector import generate_search_queries,search_github_repos,search_and_filter_repos
import markdown
from dotenv import load_dotenv

from crewai_tools import SerperDevTool
from crewai_tools import ScrapeWebsiteTool
from langchain.tools import Tool
from langchain.agents import Tool


# Initialize the tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


tools=[search_tool, scrape_tool]


load_dotenv(dotenv_path=r".env")

# Now safely get the key
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
configure(api_key=os.environ["GEMINI_API_KEY"])
llm = LLM(model="gemini/gemini-1.5-flash")

configure(api_key=os.environ["GEMINI_API_KEY"])
llm = LLM(model="gemini/gemini-1.5-flash")

os.environ["CREWAI_TELEMETRY_DISABLED"] = "true"
def func(user_topic: str):
   #print("💬 Welcome to Open-Source Project Hunter!")
    #user_topic = input("🧠 Enter a topic you're interested in: ")

    # Step 1: Get filtered repositories using Gemini + GitHub
    unique_repos = search_and_filter_repos(user_topic)
    if not unique_repos:
        print("❌ No repositories found.")
        return "❌ No repositories found."

    # Step 2: Setup CrewAI agent
    advisor = Agent(
        role="Open Source Project Advisor",
        goal="Help users find the best open-source repo to contribute to. Analyze the list {repos} and pick the one that's a real project,"
        "not just a tool or list."
        "The github repo should be something user can contribute",
        backstory="You are a skilled developer who loves evaluating GitHub repos and recommending the best ones to new contributors.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools = tools
    )
    editor = Agent(
        role="Format Text",
        goal="Take the synopsis and format it as a single clean <div> using semantic HTML for modern websites.",
        backstory=(
            "You're a top UI/UX designer. Your job is to format academic content into clean HTML. "
            "Focus on visual clarity using <h1>, <h2>, <p>, <ul>, <b>, <u>, etc. Use Google Fonts style."
            "Keep it minimal, modern, and responsive-ready. Output only the HTML <div>, no comments."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    task = Task(
        description=(
            "You are a skilled open source advisor. You will receive a list of GitHub repositories. "
            "Evaluate them and recommend the best 3 repositories to contribute to, prioritizing product-based "
            "projects with active issues. Avoid simple list collections or archived/inactive projects. "
            "Perform a quality analysis based on issues, stars, recent commits, and contribution docs."
        ),
        expected_output=(
            "Return your output as Markdown with detailed formatting.\n\n"
            "For each of the **Top 3 Recommended Projects**, include the following:\n\n"
            "### 🏷️ Project Title\n"
            "🔗 [GitHub Repository Link]\n\n"
            "**💡 Why You Should Contribute:**\n"
            "- Describe the purpose of the project.\n"
            "- Highlight activity level, issue health, and impact.\n\n"
            "**🛠️ How to Get Started:**\n"
            "- Mention beginner-friendly issues (if any).\n"
            "- Point out the contributing guide, setup instructions, or starter files.\n\n"
            "Close with a brief summary or motivational note for contributors."
        ),
        agent=advisor,
        inputs={"repos": unique_repos}
    )
    OpenSourceFormatterTask = Task(
        description=(
            "You will take the raw recommendation text about GitHub repositories and format it into clean, professional HTML inside a single <div>. "
            "Use the following HTML tags:\n"
            "- <h1> for the overall title (e.g., 'Top Open Source Picks')\n"
            "- <h2> for each project title\n"
            "- <a href='...'> for links to the GitHub repo\n"
            "- <p> for description and explanation\n"
            "- <ul>, <li> if needed for contribution steps\n"
            "- Use <b> and <u> sparingly for emphasis\n\n"
            "Avoid all boilerplate tags like <html> or <body>. Return only the <div>."
        ),
        expected_output=(
            "A single HTML <div> that contains the formatted output with the following structure:\n\n"
            "1. <h1> Top Open Source Projects to Contribute\n\n"
            "2. For each project:\n"
            "- <h2> Project Name\n"
            "- <a href='GITHUB_URL'>GitHub Repo Link</a>\n"
            "- <p><b>Why You Should Contribute:</b> Reasoning</p>\n"
            "- <p><b>Where to Start:</b> Steps, files, or issues to begin with</p>\n\n"
            "Make it visually appealing, compact, and ready to render in a web app like OpenSource Buddy. Use clean, semantic HTML only."
        ),
        agent=editor
    )
    # Step 3: CrewAI execution
    crew = Crew(
        agents=[advisor,editor],
     
        tasks=[task, OpenSourceFormatterTask],
        verbose=True
    )

    print("\n🤖 Evaluating repositories... Hold tight!\n")
    final_output = crew.kickoff(inputs={"repos": unique_repos})
    
    print("\n✅ Final Recommendation:\n")
    print(type(final_output))
    return final_output.raw

