from rdkit import Chem
from rdkit.Chem import QED
from typing import Optional

def calculate_qed_score(smiles: str) -> Optional[float]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
        
    return QED.qed(mol)

if __name__ == "__main__":
    hits_to_prioritize = [
        "Clc1ccccc1C(=O)NC1CCCCC1", # A molecule with poor properties
        "CC1=C(C=C(C=C1)N(C)C)C(=O)N2CCN(CC2)C" # A more drug-like molecule
    ]

    for hit_smi in hits_to_prioritize:
        score = calculate_qed_score(hit_smi)
        if score is not None:
            print(f"QED score for {hit_smi}: {score:.3f}")
