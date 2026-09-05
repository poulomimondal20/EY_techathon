import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from rdkit import Chem
from rdkit.Chem import AllChem
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity

class DrugRepurposingTool:
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    "notebooks/outputs/ae_models")
        self.encoder = None
        self.decoder = None
        self.fingerprints = None
        self.latents = None
        self.sim_matrix = None
        self.drug_data = None
        self._load_models()
        self._load_data()
    
    def _load_models(self):
        try:
            self.encoder = load_model(os.path.join(self.base_dir, "encoder.keras"))
            self.decoder = load_model(os.path.join(self.base_dir, "decoder.keras"))
            print("✅ Models loaded successfully")
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            raise
    
    def _load_data(self):
        try:
            predictions_path = os.path.join(os.path.dirname(self.base_dir), "repurposing_predictions.csv")
            self.drug_data = pd.read_csv(predictions_path)
            print("✅ Drug data loaded successfully")
            self._compute_fingerprints()
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise

    def _smiles_to_fingerprint(self, smiles: str, radius: int = 2, nBits: int = 2048) -> np.ndarray:
        if isinstance(smiles, str):
            try:
                cleaned_smiles = smiles.strip()
                
                if cleaned_smiles.endswith('e'):
                    cleaned_smiles = cleaned_smiles[:-1]
                
                mol = Chem.MolFromSmiles(cleaned_smiles)
                if mol:
                    try:
                        canonical_smiles = Chem.MolToSmiles(mol, canonical=True)
                        mol = Chem.MolFromSmiles(canonical_smiles)
                    except:
                        pass
                    
                    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
                    return np.array(fp, dtype=np.int8)
                else:
                    print(f"⚠️ Failed to parse SMILES: {smiles}")
            except Exception as e:
                print(f"⚠️ Error processing SMILES {smiles}: {str(e)}")
        return None

    def _compute_fingerprints(self):
        fingerprints = []
        valid_idx = []
        
        for i, row in self.drug_data.iterrows():
            fp = self._smiles_to_fingerprint(row['SMILES'])
            if fp is not None:
                fingerprints.append(fp)
                valid_idx.append(i)
        
        self.fingerprints = np.array(fingerprints, dtype=np.float32)
        self.drug_data = self.drug_data.iloc[valid_idx].reset_index(drop=True)
        
        self.latents = self.encoder.predict(self.fingerprints, batch_size=64)
        self.sim_matrix = cosine_similarity(self.latents)
        print("✅ Fingerprints and similarity matrix computed")

    def predict_repurposed_use(self, drug_name: str, k: int = 10) -> dict:
        try:
            drug_idx = self.drug_data[self.drug_data["Drug"].str.lower() == drug_name.lower()].index
            if len(drug_idx) == 0:
                return {"error": f"Drug '{drug_name}' not found in database"}
            
            drug_idx = drug_idx[0]
            latent = self.latents[drug_idx].reshape(1, -1)
            
            similarities = cosine_similarity(latent, self.latents)[0]
            neigh_idx = similarities.argsort()[::-1][:k]
            
            neighbors = self.drug_data.iloc[neigh_idx]
            neighbor_sims = similarities[neigh_idx]
            
            uses = neighbors["Repurposed_Use"].fillna("Unknown").astype(str).tolist()
            counter = Counter(uses)
            predicted_use, count = counter.most_common(1)[0]
            confidence = count / k
            
            similar_drugs = []
            for idx, (_, row) in enumerate(neighbors.iterrows()):
                similar_drugs.append({
                    "drug": row["Drug"],
                    "current_use": row["Repurposed_Use"],
                    "similarity": float(neighbor_sims[idx])
                })
            
            return {
                "predicted_repurposed_use": predicted_use,
                "confidence": float(confidence),
                "similar_drugs": similar_drugs
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def get_similar_drugs(self, drug_name: str, k: int = 10) -> dict:
        try:
            drug_idx = self.drug_data[self.drug_data["Drug"].str.lower() == drug_name.lower()].index
            if len(drug_idx) == 0:
                return {"error": f"Drug '{drug_name}' not found in database"}
            
            drug_idx = drug_idx[0]
            similarities = self.sim_matrix[drug_idx]
            neigh_idx = similarities.argsort()[::-1][1:k+1]
            
            similar_drugs = []
            for idx in neigh_idx:
                row = self.drug_data.iloc[idx]
                similar_drugs.append({
                    "drug": row["Drug"],
                    "current_use": row["Repurposed_Use"],
                    "similarity": float(similarities[idx])
                })
            
            return {
                "query_drug": drug_name,
                "similar_drugs": similar_drugs
            }
            
        except Exception as e:
            return {"error": f"Failed to find similar drugs: {str(e)}"}


def predict_drug_repurposing(drug_name: str, k: int = 10):
    tool = DrugRepurposingTool()
    return tool.predict_repurposed_use(drug_name, k)

def find_similar_drugs(drug_name: str, k: int = 10):
    tool = DrugRepurposingTool()
    return tool.get_similar_drugs(drug_name, k)


if __name__ == "__main__":
    repurposing_tool = DrugRepurposingTool()
    
    drug_name = "aspirin"
    
    repurposing_result = repurposing_tool.predict_repurposed_use(drug_name, k=10)
    print(f"Repurposing prediction for '{drug_name}':")
    print(repurposing_result)
    
    similar_drugs_result = repurposing_tool.get_similar_drugs(drug_name, k=10)
    print(f"\nSimilar drugs to '{drug_name}':")
    print(similar_drugs_result)