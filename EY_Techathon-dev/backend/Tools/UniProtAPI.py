import requests
from typing import Optional, Dict, Any

class UniProtAPI:
    BASE_URL = "https://rest.uniprot.org/uniprotkb/"

    def fetch_protein_data(self, uniprot_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}{uniprot_id}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"UniProtAPI Error: Failed to fetch data for {uniprot_id}. Reason: {e}")
            return None

if __name__ == "__main__":

    uniprot_tool = UniProtAPI()
    app_protein_data = uniprot_tool.fetch_protein_data("P05067") 
    if app_protein_data:
        print(f"Successfully fetched data for: {app_protein_data['proteinDescription']['recommendedName']['fullName']['value']}")
