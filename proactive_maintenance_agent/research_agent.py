from tavily import TavilyClient
from config import TAVILY_API_KEY
from models import ResearchSummary


def research_migration(notice):

    client = TavilyClient(api_key=TAVILY_API_KEY)

    query = f"{notice.old_api_name} to {notice.new_api_name} migration guide official documentation"

    response = client.search(query=query)

    results = response.get("results", [])

    if not results:
        return None

    top_result = results[0]

    return ResearchSummary(
        migration_guide_url=top_result["url"],
        schema_changes="Schema updated. Requires new parameters.",
        pricing_changes="Possible pricing updates.",
        performance_notes="Improved latency."
    )