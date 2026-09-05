import requests
from typing import Optional, List, Dict, Any

class ChEMBLAPI:
    
    BASE_URL = "https://www.ebi.ac.uk/chembl/api/data/"

    def get_target_bioactivities(self, target_chembl_id: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        url = f"{self.BASE_URL}activity.json"
        params = {
            "target_chembl_id": target_chembl_id,
            "limit": limit
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get('activities', [])
        except requests.exceptions.RequestException as e:
            print(f"ChEMBLAPI Error: Failed to fetch bioactivities for {target_chembl_id}. Reason: {e}")
            return None


if __name__ == "__main__":

    chembl_tool = ChEMBLAPI()
    egfr_activities = chembl_tool.get_target_bioactivities("CHEMBL240")
    print(egfr_activities[0])
    if egfr_activities:
        print(f"Found {len(egfr_activities)} bioactivity records for EGFR.")
