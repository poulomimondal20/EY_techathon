from admet_ai import ADMETModel
from typing import Dict, Any
import pandas as pd

def predict_admet_with_admet_ai(smiles_string: str) -> Dict[str, Any]:
    """
    Predicts a suite of ADMET properties for a molecule using the ADMET-AI package.

    Args:
        smiles_string: A single molecule represented as a SMILES string.

    Returns:
        A dictionary containing the predicted properties and their values.
    """
    try:
        model = ADMETModel()
        preds = model.predict(smiles=smiles_string)
        
        if isinstance(preds, pd.DataFrame):
            if not preds.empty:
                return preds.iloc[0].to_dict()
            else:
                return {}
        elif isinstance(preds, dict):
            return preds
        else:
            return {}
    except Exception as e:
        print(f"Error predicting ADMET properties: {e}")
        return {}

if __name__ == "__main__":
    ibuprofen_smiles = "CC(C)Cc1ccc(C(C)C(=O)O)cc1"
    admet_predictions = predict_admet_with_admet_ai(ibuprofen_smiles)
    print(admet_predictions)
    if admet_predictions:
        print(f"ADMET-AI Predictions for Ibuprofen:")
        print(f"  Blood-Brain Barrier (BBB) Permeability: {admet_predictions.get('BBB_Martins')}")
        print(f"  CYP2D6 Inhibition: {admet_predictions.get('CYP2D6_Veith')}")
        print(f"  Human Intestinal Absorption (HIA): {admet_predictions.get('HIA_Hou')}")

