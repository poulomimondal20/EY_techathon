import requests

class PatientLandscapeApiTool:
    """Dynamic API tool to fetch patient landscape data from various sources."""

    @staticmethod
    def fetch_who_data(resource: str, params: dict = None):
        """Fetch data from WHO GHO API.

        :param resource: API resource, e.g. 'MORT', 'DISEASE', etc.
        :param params: Optional query parameters.
        :return: JSON response or None if request fails.
        """
        if params is None:
            params = {}
        url = f"https://ghoapi.azureedge.net/api/{resource}"
        response = requests.get(url, params=params)
        return response.json() if response.ok else None

    @staticmethod
    def fetch_cdc_data(query: str, params: dict = None):
        """Fetch data from CDC Wonder API.

        Note: This endpoint may require custom handling depending on the query format.

        :param query: Query string for CDC Wonder.
        :param params: Optional query parameters.
        :return: Text response (could be HTML or JSON) or None if request fails.
        """
        if params is None:
            params = {}
        # Example endpoint; adjust according to CDC Wonder API specifications
        url = "https://wonder.cdc.gov/controller/datarequest/D76"
        params.update({"query": query})
        response = requests.get(url, params=params)
        return response.text if response.ok else None

    @staticmethod
    def fetch_hl7_data(resource: str, params: dict = None):
        """Fetch data from HL7 FHIR API.

        :param resource: FHIR resource, e.g. 'Patient', 'Observation', etc.
        :param params: Optional query parameters.
        :return: JSON response or None if request fails.
        """
        if params is None:
            params = {}
        url = f"https://hapi.fhir.org/baseR4/{resource}"
        response = requests.get(url, params=params)
        return response.json() if response.ok else None

# Example usage:
if __name__ == "__main__":
    # WHO API sample
    # who_data = PatientLandscapeApiTool.fetch_who_data("MORT", {"$filter": "Year eq 2020"})
    # print("WHO Data Sample:", who_data)

    # # CDC Wonder API sample
    # cdc_data = PatientLandscapeApiTool.fetch_cdc_data("heart disease")
    # print("CDC Data Sample:", cdc_data[:200] if cdc_data else "No data")

    # HL7 FHIR API sample
    hl7_data = PatientLandscapeApiTool.fetch_hl7_data("Patient", {"_count": 5})
    print("HL7 Data Sample:", hl7_data)
