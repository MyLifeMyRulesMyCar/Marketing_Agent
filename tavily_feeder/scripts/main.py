import yaml
from tavily_client import search, extract, research
from query_builder import build_queries

def load_config():
    with open("config/research.yml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()

    queries = build_queries(config)

    all_results = []

    for q in queries:
        print(f"\n🔍 Searching: {q}")

        results = search(q)

        urls = [r["url"] for r in results.get("results", [])]

        if config["settings"]["extract_content"]:
            extracted = extract(urls)
        else:
            extracted = urls

        if config["settings"]["use_research_api"]:
            report = research(q)
        else:
            report = None

        all_results.append({
            "query": q,
            "urls": urls,
            "report": report
        })

    print("\n✅ Done!")

if __name__ == "__main__":
    main()
