from rdkit.Chem import RDConfig
from rdkit.Chem import Descriptors
from rdkit import Chem
import os
import sys
sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
import sascorer # This import requires the path setup above

class SyntheticAccessibilityScorer:
    """
    Calculates the Synthetic Accessibility (SA) Score for a molecule.
    """
    def calculate_sa_score(self, smiles: str) -> float:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return 10.0 # Assign worst score to invalid molecules
        
        return sascorer.calculateScore(mol)


if __name__ == "__main__":
    sa_scorer = SyntheticAccessibilityScorer()

    easy_mol_score = sa_scorer.calculate_sa_score("CCO") # Ethanol
    print(f"SA Score for Ethanol: {easy_mol_score:.2f}")

    complex_mol_score = sa_scorer.calculate_sa_score("CC1=C2C(C(=O)C3(C(CC4C(C3C(CC(C4C(C2(C)C)(CC1OC(=O)C(C(C)C)N)O)O)OC(=O)C5=CC=CC=C5)OC(=O)C)O)C)OC(=O)C6=CC=CC=C6")
    print(f"SA Score for a complex molecule (Taxol): {complex_mol_score:.2f}")
