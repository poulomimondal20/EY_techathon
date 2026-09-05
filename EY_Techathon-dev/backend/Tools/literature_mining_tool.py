"""Literature Mining Tool for pharmaceutical research"""

import json
import httpx
from typing import List, Dict, Optional


def search_pubmed_literature(query: str, max_results: int = 20) -> str:
    try:
        # Using NCBI E-utilities API for PubMed search
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        # Search for article IDs
        search_url = f"{base_url}esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        response = httpx.get(search_url, params=search_params)
        search_data = response.json()
        
        if "esearchresult" not in search_data or not search_data["esearchresult"]["idlist"]:
            return json.dumps({"error": "No results found", "query": query})
        
        # Get article details
        id_list = ",".join(search_data["esearchresult"]["idlist"])
        summary_url = f"{base_url}esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": id_list,
            "retmode": "json"
        }
        
        summary_response = httpx.get(summary_url, params=summary_params)
        summary_data = summary_response.json()
        
        articles = []
        for uid, article in summary_data["result"].items():
            if uid != "uids":
                articles.append({
                    "pmid": article.get("uid"),
                    "title": article.get("title", ""),
                    "authors": article.get("authors", []),
                    "journal": article.get("fulljournalname", ""),
                    "pubdate": article.get("pubdate", ""),
                    "doi": article.get("elocationid", ""),
                    "abstract": article.get("abstract", "")[:500]  # Truncate abstract
                })
        
        return json.dumps({
            "query": query,
            "total_results": len(articles),
            "articles": articles
        })
        
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}", "query": query})


if __name__ == "__main__":
    test_query = "cancer immunotherapy"
    results = search_pubmed_literature(test_query, max_results=5)
    print(results)