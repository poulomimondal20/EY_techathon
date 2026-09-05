from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

def smiles_to_fingerprint(smiles: str, radius: int = 2, nBits: int = 2048) -> np.ndarray:
    if isinstance(smiles, str):
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            # Generate the Morgan fingerprint as a bit vector
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
            return np.array(fp)
    return None



if __name__ == "__main__":
    aspirin_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"

    # Generate the 2048-bit fingerprint
    aspirin_fp = smiles_to_fingerprint(aspirin_smiles)

    for i, bit in enumerate(aspirin_fp):
        if bit == 1:
            print(f"Bit {i} is set.")
    print(f"Total bits set: {np.sum(aspirin_fp)}")

