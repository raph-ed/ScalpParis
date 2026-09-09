from typing import List, Dict, Any

CATALOGUE_SEMANTIQUE = {
    "restauration": [
        {"produit": "Menu Dejeuner Semaine", "prix_moyen": 19.50, "indice_popularite": 94},
        {"produit": "Plat Signature (Viande / Poisson)", "prix_moyen": 24.00, "indice_popularite": 88},
        {"produit": "Verre de Vin Nature / AOP", "prix_moyen": 7.50, "indice_popularite": 82},
        {"produit": "Formule Entree / Plat", "prix_moyen": 22.00, "indice_popularite": 79},
    ],
    "coffee_shop": [
        {"produit": "Flat White & Latte Specialite", "prix_moyen": 5.20, "indice_popularite": 96},
        {"produit": "Pastry Artisanale (Banana Bread, Cookie)", "prix_moyen": 4.50, "indice_popularite": 91},
        {"produit": "Avocado Toast & Oeufs Poches", "prix_moyen": 13.50, "indice_popularite": 85},
        {"produit": "Matcha Latte Ceremonial", "prix_moyen": 6.00, "indice_popularite": 78},
    ],
    "boulangerie": [
        {"produit": "Baguette de Tradition Label Rouge", "prix_moyen": 1.35, "indice_popularite": 98},
        {"produit": "Croissant Beurre AOP", "prix_moyen": 1.45, "indice_popularite": 95},
        {"produit": "Pain au Levain Naturel (kg)", "prix_moyen": 6.80, "indice_popularite": 84},
        {"produit": "Formule Sandwich Artisanal", "prix_moyen": 8.90, "indice_popularite": 87},
    ],
    "textile": [
        {"produit": "Chemise Coton Bio Uni", "prix_moyen": 79.00, "indice_popularite": 89},
        {"produit": "Denim Brut Coupe Droite", "prix_moyen": 110.00, "indice_popularite": 86},
        {"produit": "Tricot Laine Fine / Cachemire", "prix_moyen": 95.00, "indice_popularite": 81},
        {"produit": "Accessoire Cuir Minimaliste", "prix_moyen": 45.00, "indice_popularite": 74},
    ],
    "epicerie": [
        {"produit": "Huile d'Olive Extra Vierge 500ml", "prix_moyen": 14.50, "indice_popularite": 88},
        {"produit": "Fromage Affine Selection Terroir", "prix_moyen": 8.50, "indice_popularite": 90},
        {"produit": "Vin de Proprietaire Selectionne", "prix_moyen": 12.00, "indice_popularite": 86},
        {"produit": "Cafe en Grains Origine Pure 250g", "prix_moyen": 9.20, "indice_popularite": 83},
    ],
    "coiffure_beaute": [
        {"produit": "Coupe & Coiffage Signature", "prix_moyen": 48.00, "indice_popularite": 92},
        {"produit": "Balayage Naturel & Soin", "prix_moyen": 95.00, "indice_popularite": 87},
        {"produit": "Soin Capillaire Revitalisant", "prix_moyen": 32.00, "indice_popularite": 79},
        {"produit": "Rituel Barbe Traditionnelle", "prix_moyen": 28.00, "indice_popularite": 75},
    ],
    "librairie": [
        {"produit": "Roman Litterature Contemporaine", "prix_moyen": 21.00, "indice_popularite": 94},
        {"produit": "Essai & Sciences Humaines", "prix_moyen": 19.50, "indice_popularite": 86},
        {"produit": "Bande Dessinee Graphique & Roman Graphique", "prix_moyen": 24.00, "indice_popularite": 89},
        {"produit": "Livre Jeunesse Illustre", "prix_moyen": 14.00, "indice_popularite": 80},
    ]
}

def analyser_produits_phares(secteur: str) -> List[Dict[str, Any]]:
    return CATALOGUE_SEMANTIQUE.get(secteur, [
        {"produit": "Prestation Standard", "prix_moyen": 25.00, "indice_popularite": 80},
        {"produit": "Prestation Premium", "prix_moyen": 50.00, "indice_popularite": 75}
    ])