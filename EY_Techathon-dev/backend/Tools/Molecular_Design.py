from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
from rdkit.Chem.QED import qed as calc_qed
from typing import Optional, List, Dict, Tuple
import random

class MolecularDesigner:
    
    def __init__(self):
        self.common_decorations = {
            'halogens': ['F', 'Cl', 'Br'],
            'electron_withdrawing': ['CF3', 'NO2', 'CN', 'C(=O)O'],
            'electron_donating': ['CH3', 'OCH3', 'NH2', 'OH'],
            'heterocycles': ['c1ccncc1', 'c1cccnc1', 'c1ccoc1'],
            'linkers': ['CH2', 'O', 'NH', 'S']
        }
    
    def validate_molecule(self, mol: Chem.Mol) -> bool:
        if not mol:
            return False
        try:
            Chem.SanitizeMol(mol)
            # Check for reasonable properties
            mw = Descriptors.MolWt(mol)
            if mw > 800 or mw < 50:
                return False
            return True
        except:
            return False
    
    def get_molecular_properties(self, smiles: str) -> Dict[str, float]:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return {}
        
        return {
            'molecular_weight': Descriptors.MolWt(mol),
            'logP': Descriptors.MolLogP(mol),
            'hbd': Descriptors.NumHDonors(mol),
            'hba': Descriptors.NumHAcceptors(mol),
            'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
            'aromatic_rings': Descriptors.NumAromaticRings(mol),
            'tpsa': Descriptors.TPSA(mol),
            'qed': calc_qed(mol)
        }
    
    def decorate_aromatic_ring(self, smiles: str, decoration: str = "F", position: int = 0) -> Optional[str]:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return None

        # Find aromatic carbons with hydrogens
        aromatic_pattern = Chem.MolFromSmarts('[cH]')
        matches = mol.GetSubstructMatches(aromatic_pattern)
        
        if not matches:
            return None
        
        # Select position (default first, or specify)
        if position >= len(matches):
            position = 0
        
        atom_idx = matches[position][0]
        
        # Use predefined reaction SMARTS for different decorations
        reaction_smarts_map = {
            'F': '[cH:1]>>[c:1]F',
            'Cl': '[cH:1]>>[c:1]Cl',
            'Br': '[cH:1]>>[c:1]Br',
            'I': '[cH:1]>>[c:1]I',
            'CH3': '[cH:1]>>[c:1]C',
            'CF3': '[cH:1]>>[c:1]C(F)(F)F',
            'NO2': '[cH:1]>>[c:1][N+](=O)[O-]',
            'CN': '[cH:1]>>[c:1]C#N',
            'OH': '[cH:1]>>[c:1]O',
            'NH2': '[cH:1]>>[c:1]N',
            'OCH3': '[cH:1]>>[c:1]OC',
            'C(=O)O': '[cH:1]>>[c:1]C(=O)O',
            'CH2': '[cH:1]>>[c:1]CC',  # Ethyl group instead of methylene
            'O': '[cH:1]>>[c:1]OC',    # Methoxy instead of just oxygen
            'NH': '[cH:1]>>[c:1]NC',   # Methylamino instead of just NH
            'S': '[cH:1]>>[c:1]SC'     # Methylthio instead of just sulfur
        }
        
        reaction_smarts = reaction_smarts_map.get(decoration, f'[cH:1]>>[c:1]{decoration}')
        
        try:
            rxn = AllChem.ReactionFromSmarts(reaction_smarts)
            if rxn:
                products = rxn.RunReactants((mol,))
                
                if products:
                    product_mol = products[0][0]
                    if self.validate_molecule(product_mol):
                        return Chem.MolToSmiles(product_mol)
        except Exception as e:
            print(f"Reaction failed for decoration {decoration}: {e}")
        
        return None
    
    def generate_bioisosteres(self, smiles: str) -> List[str]:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return []
        
        analogs = []
        
        # Use SMARTS-based replacements for more precise matching
        replacements = [
            # Carboxylic acid to amide
            ('[C:1](=O)[OH]', '[C:1](=O)N'),
            # Benzene to pyridine (meta position)
            ('c1cc([*:1])ccc1', 'c1nc([*:1])ccc1'),
            # Ether to amine
            ('[C:1][O:2][C:3]', '[C:1][NH:2][C:3]'),
            # Sulfur to oxygen
            ('[C:1][S:2][C:3]', '[C:1][O:2][C:3]'),
        ]
        
        for old_smarts, new_smarts in replacements:
            try:
                pattern = Chem.MolFromSmarts(old_smarts)
                if pattern and mol.HasSubstructMatch(pattern):
                    rxn_smarts = f'{old_smarts}>>{new_smarts}'
                    rxn = AllChem.ReactionFromSmarts(rxn_smarts)
                    if rxn:
                        products = rxn.RunReactants((mol,))
                        for product_set in products:
                            for product_mol in product_set:
                                if self.validate_molecule(product_mol):
                                    analog_smiles = Chem.MolToSmiles(product_mol)
                                    if analog_smiles != smiles:
                                        analogs.append(analog_smiles)
            except Exception as e:
                print(f"Bioisostere reaction failed for {old_smarts}: {e}")
                continue
        
        return list(set(analogs))  # Remove duplicates
    
    def scaffold_hop(self, smiles: str) -> List[str]:
        """Generate scaffold hopping analogs."""
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return []
        
        analogs = []
        
        # Find ring systems and try replacements
        ring_info = mol.GetRingInfo()
        
        # Simple scaffold replacements
        scaffold_replacements = {
            'c1ccccc1': ['c1ccncc1', 'c1cccnc1', 'c1ccoc1', 'c1ccsc1'],  # Benzene alternatives
            'c1ccncc1': ['c1ccccc1', 'c1cccnc1', 'c1ccoc1'],  # Pyridine alternatives
        }
        
        original_smiles = smiles
        for scaffold, alternatives in scaffold_replacements.items():
            if scaffold in original_smiles:
                for alt in alternatives:
                    try:
                        new_smiles = original_smiles.replace(scaffold, alt)
                        new_mol = Chem.MolFromSmiles(new_smiles)
                        if self.validate_molecule(new_mol):
                            analogs.append(Chem.MolToSmiles(new_mol))
                    except:
                        continue
        
        return list(set(analogs))
    
    def generate_analog_series(self, smiles: str, num_analogs: int = 10) -> List[Dict[str, any]]:
        """Generate a diverse series of analogs with properties."""
        analogs = []
        
        # Strategy 1: Aromatic decorations
        for decoration_type, decorations in self.common_decorations.items():
            for decoration in decorations[:2]:  # Limit to 2 per type
                try:
                    analog_smiles = self.decorate_aromatic_ring(smiles, decoration)
                    if analog_smiles and analog_smiles != smiles:
                        properties = self.get_molecular_properties(analog_smiles)
                        analogs.append({
                            'smiles': analog_smiles,
                            'strategy': f'aromatic_decoration_{decoration_type}',
                            'modification': decoration,
                            'properties': properties
                        })
                except:
                    continue
        
        # Strategy 2: Bioisosteres
        bioisosteres = self.generate_bioisosteres(smiles)
        for bio_smiles in bioisosteres[:3]:  # Limit to 3
            properties = self.get_molecular_properties(bio_smiles)
            analogs.append({
                'smiles': bio_smiles,
                'strategy': 'bioisosteric_replacement',
                'modification': 'bioisostere',
                'properties': properties
            })
        
        # Strategy 3: Scaffold hopping
        scaffolds = self.scaffold_hop(smiles)
        for scaffold_smiles in scaffolds[:3]:  # Limit to 3
            properties = self.get_molecular_properties(scaffold_smiles)
            analogs.append({
                'smiles': scaffold_smiles,
                'strategy': 'scaffold_hopping',
                'modification': 'scaffold_replacement',
                'properties': properties
            })
        
        # Remove duplicates and limit to requested number
        unique_analogs = []
        seen_smiles = set()
        for analog in analogs:
            if analog['smiles'] not in seen_smiles:
                seen_smiles.add(analog['smiles'])
                unique_analogs.append(analog)
        
        return unique_analogs[:num_analogs]
    
    def optimize_for_property(self, smiles: str, target_property: str, target_value: float, tolerance: float = 0.1) -> List[str]:
        """Generate analogs optimized for a specific property."""
        analogs = self.generate_analog_series(smiles, num_analogs=20)
        
        optimized = []
        for analog in analogs:
            if target_property in analog['properties']:
                prop_value = analog['properties'][target_property]
                if abs(prop_value - target_value) <= tolerance:
                    optimized.append(analog['smiles'])
        
        return optimized

# Convenience functions for backward compatibility
def decorate_aromatic_ring(smiles: str, decoration: str = "F") -> Optional[str]:
    """Legacy function for backward compatibility."""
    designer = MolecularDesigner()
    return designer.decorate_aromatic_ring(smiles, decoration)

if __name__ == "__main__":
    designer = MolecularDesigner()
    
    lead_smiles = "c1ccccc1C(=O)O"  # Benzoic acid
    
    print(f"Original lead: {lead_smiles}")
    print(f"Properties: {designer.get_molecular_properties(lead_smiles)}")
    print("\n" + "="*50)
    
    # Generate analog series
    analogs = designer.generate_analog_series(lead_smiles, num_analogs=8)
    
    for i, analog in enumerate(analogs, 1):
        print(f"\nAnalog {i}:")
        print(f"  SMILES: {analog['smiles']}")
        print(f"  Strategy: {analog['strategy']}")
        print(f"  MW: {analog['properties'].get('molecular_weight', 'N/A'):.2f}")
        print(f"  LogP: {analog['properties'].get('logP', 'N/A'):.2f}")
        print(f"  QED: {analog['properties'].get('qed', 'N/A'):.3f}")
