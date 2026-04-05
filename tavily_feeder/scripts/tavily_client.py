import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query):
    return client.search(query)

def extract(urls):
    return client.extract(urls=urls)

def research(query):
    return client.research(
        input=query,
        model="mini"
    )
