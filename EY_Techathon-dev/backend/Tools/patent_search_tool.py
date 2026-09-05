import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Union
import os
from dotenv import load_dotenv
import time
import json
import re

load_dotenv()

class PatentSearchTool:
    def __init__(self):
        self.serp_api_key = os.getenv("SERP_API_KEY")
        
        if not self.serp_api_key:
            raise ValueError("SERP_API_KEY not found in environment variables")
    
    def call_serp_api(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"SERP API request failed: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Failed to parse SERP API response: {e}")
            return {}
        
    def scrape_patents_info(self, patent_ids: List[str]) -> List[Dict[str, Any]]:
        url = "https://serpapi.com/search"
        patent_summaries = []
        
        for patent_id in patent_ids:
            try:
                print(f"Scraping patent: {patent_id}")
                
                # Search for patent using SERP API
                params = {
                    "q": patent_id, 
                    "api_key": self.serp_api_key, 
                    "engine": "google_patents"
                }
                response = self.call_serp_api(url, params)
                
                if not response or 'organic_results' not in response:
                    print(f"No results found for patent {patent_id}")
                    continue
                
                if not response['organic_results']:
                    print(f"Empty results for patent {patent_id}")
                    continue
                
                # Get detailed patent information
                serpapi_link = response['organic_results'][0].get('serpapi_link')
                if not serpapi_link:
                    print(f"No serpapi_link found for patent {patent_id}")
                    continue
                
                new_response = self.call_serp_api(
                    serpapi_link, 
                    {"api_key": self.serp_api_key}
                )
                
                if not new_response:
                    print(f"Failed to get detailed info for patent {patent_id}")
                    continue
                
                title = new_response.get('title', 'Title not available')
                html_link = new_response.get('description_link')
                
                # Scrape patent text if HTML link available
                patent_text = "Patent text not available"
                if html_link:
                    try:
                        page = requests.get(html_link, timeout=30)
                        page.raise_for_status()
                        
                        soup = BeautifulSoup(page.content, 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        
                        # Extract summary section
                        start_index = text.find("SUMMARY")
                        end_index = text.find("DESCRIPTION")
                        if start_index != -1 and end_index != -1:
                            patent_text = text[start_index:end_index]
                        else:
                            # If SUMMARY not found, try ABSTRACT
                            start_index = text.find("ABSTRACT")
                            if start_index != -1:
                                patent_text = text[start_index:start_index+1000]
                            else:
                                patent_text = text[:1000] if text else "Relevant section not found."
                    
                    except Exception as e:
                        print(f"Failed to scrape patent text for {patent_id}: {e}")
                
                response_dict = {
                    "summary": patent_text,
                    "patent_id": patent_id, 
                    "title": title,  
                    "patent_link": html_link,
                    "status": "success"
                }
                patent_summaries.append(response_dict)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing patent {patent_id}: {e}")
                patent_summaries.append({
                    "patent_id": patent_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        return patent_summaries
    
    def get_patents_info(self, queries: Union[List[str], str]) -> List[Dict[str, Any]]:
        if isinstance(queries, str):
            queries = [queries]
        
        patent_ids = set()
        
        for query in queries:
            print(f"Searching patents for query: {query}")
            
            # SERP API patent search
            try:
                serp_params = {
                    "q": query,
                    "api_key": self.serp_api_key,
                    "engine": "google_patents",
                    "num": 10
                }
                serp_response = self.call_serp_api("https://serpapi.com/search", serp_params)
                
                print(f"Debug: API response keys: {list(serp_response.keys()) if serp_response else 'Empty response'}")
                
                if serp_response and 'organic_results' in serp_response:
                    print(f"Debug: Found {len(serp_response['organic_results'])} results")
                    
                    for i, result in enumerate(serp_response['organic_results']):
                        # Check all possible fields for patent information
                        patent_link = result.get('link', result.get('url', ''))
                        title = result.get('title', 'No title')
                        snippet = result.get('snippet', '')
                        
                        print(f"Debug result {i}: {title}")
                        print(f"Debug all result keys: {list(result.keys())}")
                        print(f"Debug link: {patent_link}")
                        
                        # More flexible patent ID extraction
                        patent_id = None
                        
                        # Method 1: Check if patent_id is directly provided
                        if 'patent_id' in result:
                            patent_id = result['patent_id']
                        
                        # Method 2: From Google Patents URL or path
                        elif patent_link and ('patents.google.com' in patent_link or 'patent/' in patent_link):
                            # Handle both full URLs and path formats
                            if 'patents.google.com' in patent_link:
                                parts = patent_link.split('/')
                                for j, part in enumerate(parts):
                                    if part == 'patent' and j + 1 < len(parts):
                                        potential_id = parts[j + 1].split('?')[0]
                                        if any(potential_id.startswith(prefix) for prefix in ['US', 'EP', 'WO', 'CN', 'JP', 'KR', 'AU']):
                                            patent_id = potential_id
                                            break
                            else:
                                # Handle path format like "patent/US9730895B2/en"
                                parts = patent_link.split('/')
                                for part in parts:
                                    if re.match(r'^[A-Z]{2}\d+[A-Z]*\d*$', part):
                                        patent_id = part
                                        break

                        # Method 3: From title and snippet using regex
                        if not patent_id:
                            full_text = f"{title} {snippet}"
                            
                            # Look for patent patterns in text
                            patent_patterns = [
                                r'US\d{7,8}[AB]\d?',  # US patents with A/B suffix
                                r'US\d{6,8}',         # Standard US patents
                                r'EP\d{6,8}[AB]\d?',  # European patents
                                r'WO\d{4}/\d{6}',     # WIPO patents
                                r'CN\d{6,8}[AB]?',    # Chinese patents
                                r'JP\d{7,8}[AB]?'     # Japanese patents
                            ]
                            
                            for pattern in patent_patterns:
                                matches = re.findall(pattern, full_text)
                                if matches:
                                    patent_id = matches[0]
                                    break
                        
                        # Method 4: Check serpapi_link for patent ID
                        if not patent_id and 'serpapi_link' in result:
                            serpapi_url = result['serpapi_link']
                            serpapi_match = re.search(r'patent_id=([^&]+)', serpapi_url)
                            if serpapi_match:
                                patent_id = serpapi_match.group(1)
                        
                        # Method 5: Try to extract from any URL field
                        if not patent_id:
                            all_urls = [
                                result.get('link', ''),
                                result.get('url', ''),
                                result.get('serpapi_link', ''),
                                result.get('cached_page_link', '')
                            ]
                            
                            for url in all_urls:
                                if url:
                                    url_patent_match = re.search(r'(US\d{6,8}[AB]?\d?|EP\d{6,8}[AB]?|WO\d{4}/\d{6}|CN\d{6,8}[AB]?)', url)
                                    if url_patent_match:
                                        patent_id = url_patent_match.group(1)
                                        break
                        
                        if patent_id:
                            print(f"Debug: Extracted patent ID: {patent_id}")
                            patent_ids.add(patent_id)
                        else:
                            print(f"Debug: Could not extract patent ID from result {i}")
                            # Print full result for debugging
                            print(f"Full result: {json.dumps(result, indent=2)}")
                
                else:
                    print(f"Debug: No organic_results in response or empty response")
                    if serp_response:
                        print(f"Debug: Available keys: {list(serp_response.keys())}")
                    
            except Exception as e:
                print(f"SERP API search failed for query '{query}': {e}")
        
        print(f"Found {len(patent_ids)} unique patent IDs: {list(patent_ids)}")
        
        if not patent_ids:
            return [{
                "error": "No patent IDs found for the given queries",
                "queries": queries,
                "status": "no_results"
            }]
        
        return self.scrape_patents_info(list(patent_ids))
    
    def search_drug_patents(self, drug_name: str, indication: str = "") -> List[Dict[str, Any]]:
        queries = [f"{drug_name} pharmaceutical patent"]
        if indication:
            queries.append(f"{drug_name} {indication} treatment patent")
        
        return self.get_patents_info(queries)


if __name__ == "__main__":
    patent_tool = PatentSearchTool()
    
    print("=== Disease Patent Search Test ===")
    disease_name = input("Enter disease name: ") or "diabetes"
    
    print(f"\nSearching patents for: {disease_name}")
    # Search for drug patents related to the disease
    disease_patents = patent_tool.search_drug_patents(f"{disease_name}", "treatment")
    
    print(f"\nFound {len(disease_patents)} results:")
    for i, patent in enumerate(disease_patents, 1):
        if patent.get('status') == 'success':
            print(f"\n--- Patent {i} ---")
            print(f"Patent ID: {patent['patent_id']}")
            print(f"Title: {patent['title']}")
            print(f"Summary: {patent['summary'][:200]}...")
            if patent.get('patent_link'):
                print(f"Link: {patent['patent_link']}")
            print("-" * 50)
        elif patent.get('status') == 'no_results':
            print(f"No patents found for: {disease_name}")
        else:
            print(f"Error: {patent.get('error', 'Unknown error')}")


