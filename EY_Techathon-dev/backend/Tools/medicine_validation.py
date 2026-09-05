import requests
import json

# Function to check if a drug is approved using ChEMBL API
# Approved drugs have max_phase=4

def check_drug_chembl(drug_name):
    try:
        url = f'https://www.ebi.ac.uk/chembl/api/data/molecule?pref_name__iexact={drug_name}&max_phase=4'
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            if not response.text.strip():
                return f"Empty response from ChEMBL API for {drug_name}"
            
            try:
                data = response.json()
                if data.get('page_meta', {}).get('total_count', 0) > 0:
                    return f"{drug_name} is approved (max_phase=4) in ChEMBL database."
                else:
                    return f"{drug_name} is NOT approved or not found in ChEMBL database."
            except json.JSONDecodeError as e:
                return f"Invalid JSON response from ChEMBL API: {e}"
        else:
            return f"ChEMBL API request failed: HTTP {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to ChEMBL API: {e}"
    except Exception as e:
        return f"Unexpected error querying ChEMBL: {e}"


def check_drug_openfda(drug_name):
    try:
        url = f'https://api.fda.gov/drug/drugsfda.json?search=openfda.generic_name:"{drug_name}"'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            if not response.text.strip():
                return f"Empty response from OpenFDA API for {drug_name}"
            
            try:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    return f"{drug_name} is FDA approved or has submissions."
                else:
                    return f"{drug_name} is NOT FDA approved or no submissions found."
            except json.JSONDecodeError as e:
                return f"Invalid JSON response from OpenFDA API: {e}"
        else:
            return f"OpenFDA API request failed: HTTP {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to OpenFDA API: {e}"
    except Exception as e:
        return f"Unexpected error querying OpenFDA: {e}"

def validate_medicine(medicine_name):
    results = {
        'medicine_name': medicine_name,
        'chembl_result': check_drug_chembl(medicine_name),
        'openfda_result': check_drug_openfda(medicine_name)
    }
    
    chembl_approved = "is approved" in results['chembl_result']
    fda_approved = "is FDA approved" in results['openfda_result']
    
    if chembl_approved or fda_approved:
        results['overall_status'] = "APPROVED"
    else:
        results['overall_status'] = "NOT APPROVED/UNKNOWN"
    
    return results

if __name__ == '__main__':
    drug_to_check = input("Enter medicine name: ") or "aspirin"
    
    print(f"\n=== Validating Medicine: {drug_to_check} ===")
    
    validation_results = validate_medicine(drug_to_check)
    
    print(f"ChEMBL Result: {validation_results['chembl_result']}")
    print(f"OpenFDA Result: {validation_results['openfda_result']}")
    print(f"Overall Status: {validation_results['overall_status']}")
    
    print(f"\n=== Testing with known approved drug: ibuprofen ===")
    ibuprofen_results = validate_medicine("ibuprofen")
    print(f"Ibuprofen - Overall Status: {ibuprofen_results['overall_status']}")