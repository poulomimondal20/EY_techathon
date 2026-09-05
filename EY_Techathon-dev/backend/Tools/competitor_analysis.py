import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

class ClinicalTrialsAPIClient:    
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/v2"
        self.session = requests.Session()
    
    def get_trials_by_sponsor(self, sponsor_name: str, 
                              recruitment_status: str = None,
                              phase: str = None,
                              limit: int = 100) -> pd.DataFrame:
        
        # Build query filter
        filters = [f'organization.name:AREA["{sponsor_name}"]']
        
        if recruitment_status:
            filters.append(f'recruitment_status:{recruitment_status}')
        if phase:
            filters.append(f'phase:{phase}')
        
        query = " AND ".join(filters)
        
        params = {
            "query.cond": query,
            "pageSize": min(limit, 100),  # API max is 100 per page
            "format": "json"
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}/studies",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse trials
            trials = []
            for study in data.get("studies", []):
                protocol = study["protocolSection"]
                trials.append({
                    "nct_id": study["protocolSection"]["identificationModule"]["nctId"],
                    "title": protocol["identificationModule"]["officialTitle"],
                    "status": protocol["statusModule"]["overallStatus"],
                    "phase": protocol["designModule"].get("phases", [None]),
                    "enrollment": protocol["designModule"]["enrollmentInfo"].get("count"),
                    "start_date": protocol["statusModule"].get("startDateStruct", {}).get("date"),
                    "completion_date": protocol["statusModule"].get("completionDateStruct", {}).get("date"),
                    "condition": protocol["conditionsModule"]["conditions"] if "conditionsModule" in protocol else None,
                    "sponsor": sponsor_name
                })
            
            return pd.DataFrame(trials)
        
        except requests.RequestException as e:
            print(f"Error fetching trials: {e}")
            return pd.DataFrame()
    
    def get_trial_details(self, nct_id: str) -> Dict:
        """Get detailed information for a specific trial"""
        try:
            response = self.session.get(
                f"{self.base_url}/studies/{nct_id}",
                params={"format": "json"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching trial {nct_id}: {e}")
            return {}
    
    def monitor_competitor_trials(self, competitor_names: List[str]) -> pd.DataFrame:
        """Monitor all trials for multiple competitors"""
        all_trials = []
        
        for competitor in competitor_names:
            df = self.get_trials_by_sponsor(competitor)
            all_trials.append(df)
        
        return pd.concat(all_trials, ignore_index=True)


if __name__ == "__main__":
    client = ClinicalTrialsAPIClient()
    
    competitor = "Pfizer"
    trials_df = client.get_trials_by_sponsor(competitor, recruitment_status="RECRUITING", limit=50)
    print(trials_df.head())
    
    competitors = ["Pfizer", "Moderna", "AstraZeneca"]
    all_trials_df = client.monitor_competitor_trials(competitors)
    print(all_trials_df.head())