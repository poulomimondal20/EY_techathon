import requests


class ClinicalTrialsAPIClient:
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    def search_trials(self, company_name, max_results=100, recruiting_only=False):
        if recruiting_only:
            query = f'AREA[LeadSponsorName]{company_name} AND AREA[OverallStatus]RECRUITING'
        else:
            query = f'AREA[LeadSponsorName]{company_name}'
        
        params = {
            'query.cond': query,
            'pageSize': min(max_results, 1000),
            'format': 'json'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching clinical trials: {e}")
            return {"error": str(e)}


def fetch_clinical_trials(company_name, max_results=100, recruiting_only=False):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    if recruiting_only:
        query = f'AREA[LeadSponsorName]{company_name} AND AREA[OverallStatus]RECRUITING'
    else:
        query = f'AREA[LeadSponsorName]{company_name}'
    
    params = {
        'query.cond': query,
        'pageSize': min(max_results, 1000),  
        'format': 'json'
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()  
    return response.json()



from typing import Dict, Any, Optional
from pydantic import BaseModel

class ClinicalTrialQuery(BaseModel):
    query: str
    max_results: Optional[int] = 100
    recruiting_only: Optional[bool] = False

def fetch_clinical_trials_v2(query: str, max_results: int = 100, recruiting_only: bool = False) -> Dict[str, Any]:
    """
    Fetch clinical trials from ClinicalTrials.gov API.
    
    Args:
        query (str): The search query (e.g., company name or condition)
        max_results (int, optional): Maximum number of results to return. Defaults to 100.
        recruiting_only (bool, optional): Filter for recruiting trials only. Defaults to False.
    
    Returns:
        Dict[str, Any]: JSON response from the API
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    # Extract company name from query if it contains "company" keyword
    import re
    company_match = re.search(r'company\s+(\w+)', query, re.IGNORECASE)
    company_name = company_match.group(1) if company_match else query
    
    params = {
        'filter.overallStatus': 'RECRUITING' if recruiting_only else None,
        'filter.advanced': f'AREA[LeadSponsorName]{company_name}',
        'pageSize': min(max_results, 1000),
        'format': 'json'
    }
    
    params = {k: v for k, v in params.items() if v is not None}
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "status": "error"}


if __name__ == "__main__":
    company = "Pfizer"
    trials = fetch_clinical_trials_v2(company, max_results=10, recruiting_only=True)
    print(trials)