import os 
import sys 
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.tavily import TavilyTools
from agno.tools.baidusearch import BaiduSearchTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import json

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Tools'))


try:
    from medicine_validation import validate_medicine
except ImportError as e:
    print(f"Warning: Medicine validation tool not found: {e}")



class MedicineValidationResult(BaseModel):
    medicine_name: str = Field(..., description="Name of the validated medicine")
    is_approved: bool = Field(default=False, description="Whether the medicine is FDA approved")
    regulatory_status: str = Field(default="Unknown", description="Current regulatory approval status")
    approved_indications: List[str] = Field(default_factory=list, description="Approved uses for the medicine")
    safety_warnings: List[str] = Field(default_factory=list, description="Safety warnings and contraindications")
    manufacturers: List[str] = Field(default_factory=list, description="Authorized manufacturers")
    prescription_status: str = Field(default="Unknown", description="Prescription or OTC status")
    summary: str = Field(default="", description="Brief validation summary")


class MedicineValidationAgent:
    def __init__(self):
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are a medical validation agent specializing in verifying 
            the authenticity and approval status of medicines.
            
            Core Capabilities:
            - Medicine authenticity verification
            - FDA and regulatory approval status
            - Drug safety and efficacy validation
            - Counterfeit drug identification
            
            RESPONSE FORMAT: Return your final response as valid JSON only, no markdown or extra text.""",
            tools=[
                TavilyTools(), 
                BaiduSearchTools(), 
                self._validate_medicine_wrapper
            ],
            markdown=False
        )
    
    def _validate_medicine_wrapper(self, medicine_name: str):
        try:
            results = validate_medicine(medicine_name)
            return results
        except Exception as e:
            return {"error": f"Medicine validation failed: {str(e)}"}
    
    def validate_medicine_query(self, query: str) -> MedicineValidationResult:
        try:
            result = self.agent.run(f"""
            Validate the medicine: {query}
            
            Search for and gather:
            - FDA approval status and history
            - Approved indications and uses
            - Safety warnings and contraindications
            - Authorized manufacturers
            - Prescription vs OTC status
            
            Return your response as a JSON object with this exact structure:
            {{
                "medicine_name": "Name of the medicine",
                "is_approved": true,
                "regulatory_status": "FDA approved since YYYY",
                "approved_indications": ["Indication 1", "Indication 2"],
                "safety_warnings": ["Warning 1", "Warning 2"],
                "manufacturers": ["Manufacturer 1", "Manufacturer 2"],
                "prescription_status": "OTC or Prescription",
                "summary": "Brief validation summary"
            }}
            
            Return ONLY the JSON object, no additional text or markdown.
            """).content
            
            if not result or result.strip() == "":
                return MedicineValidationResult(
                    medicine_name=query,
                    is_approved=False,
                    regulatory_status="Unknown",
                    prescription_status="Unknown",
                    summary="Error: Unable to validate medicine"
                )
            
            # Clean up the response
            cleaned_result = result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.startswith("```"):
                cleaned_result = cleaned_result[3:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]
            cleaned_result = cleaned_result.strip()
            
            data = json.loads(cleaned_result)
            
            # Handle None values from LLM response
            if data.get("is_approved") is None:
                data["is_approved"] = False
            if data.get("regulatory_status") is None:
                data["regulatory_status"] = "Unknown"
            if data.get("prescription_status") is None:
                data["prescription_status"] = "Unknown"
            if data.get("summary") is None:
                data["summary"] = ""
                
            return MedicineValidationResult(**data)
            
        except json.JSONDecodeError as e:
            return MedicineValidationResult(
                medicine_name=query,
                is_approved=False,
                regulatory_status=f"Error parsing response: {str(e)}",
                prescription_status="Unknown",
                summary=result if result else "No response received"
            )
        except Exception as e:
            return MedicineValidationResult(
                medicine_name=query,
                is_approved=False,
                regulatory_status=f"Error: {str(e)}",
                prescription_status="Unknown",
                summary="Please try again."
            )
    
    def validate_drug(self, medicine_name: str) -> MedicineValidationResult:
        return self.validate_medicine_query(medicine_name)
    
    

if __name__ == "__main__":
    validation_agent = MedicineValidationAgent()
    
    print("=== Medicine Validation Agent Test ===")
    
    query = "Aspirin"
    result = validation_agent.validate_drug(query)
    print(f"\nValidation Result (JSON):")
    print("-" * 80)
    print(result.model_dump_json(indent=2))
    print("-" * 80)
    
