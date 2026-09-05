import requests
from typing import Optional, List, Dict, Any

class StringDBAPI:

    BASE_URL = "https://string-db.org/api/json/network"

    def __init__(self, species: int = 9606): # Default to Homo sapiens
        self.species = species

    def get_interaction_network(self, protein_ids: List[str]) -> Optional[List[Dict[str, Any]]]:
        params = {
            "identifiers": "\r".join(protein_ids),
            "species": self.species,
            "caller_identity": "PharmAgentsFramework"
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"StringDBAPI Error: Failed to fetch network for {protein_ids}. Reason: {e}")
            return None


if __name__ == "__main__":
    string_tool = StringDBAPI()
    # Get interactions for TP53 and MDM2
    network = string_tool.get_interaction_network(["TP53", "MDM2"])
    print(network)
    if network:
        print(f"Found {len(network)} interactions.")