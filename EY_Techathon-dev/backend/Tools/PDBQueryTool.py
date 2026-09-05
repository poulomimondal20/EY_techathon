import requests
from typing import Optional, Dict, Any

class PDBQueryTool:
    BASE_URL = "https://data.rcsb.org/rest/v1/core/entry/"

    def get_structure_summary(self, pdb_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}{pdb_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"PDBQueryTool Error: Failed to fetch structure for {pdb_id}. Reason: {e}")
            return None

# --- Example Usage ---
if __name__ == "__main__":
    pdb_tool = PDBQueryTool()
    structure_info = pdb_tool.get_structure_summary("6M0J")
    if structure_info:
        print(f"Structure Title: {structure_info['struct']['title']}")
