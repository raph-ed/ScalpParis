# ScalpMeParis
**Paris Commercial Market Intelligence
Outil d'analyse de marché et d'aide à la décision pour l'implantation commerciale à Paris. La plateforme extrait les données administratives des établissements parisiens, calcule les métriques financières sectorielles et cartographie les opportunités commerciales par arrondissement.**

Fonctionnalités
Extraction de données d'entreprises : Interrogation paginée de l'API Recherche d'Entreprises (data.gouv.fr) selon le code postal (75001 à 75020) et l'activité principale (codes NAF).  

Indicateurs financiers (SQL) : Stockage relationnel et calcul des moyennes de chiffre d'affaires, marges nettes, et classement des commerces par rentabilité.  

Cartographie satellite : Visualisation géographique sur fond Leaflet / Esri World Imagery avec segmentation colorimétrique selon l'affluence et le volume d'affaires :  

Rouge : forte affluence / CA élevé (> 200 000 €).  
Orange : flux intermédiaire (100 000 € – 200 000 €).  
Vert : commerce de quartier / clientèle régulière (< 100 000 €).  

Analyse de catalogue : Extraction des produits les plus vendus, des prix moyens observés et des indices de demande par domaine d'activité.  
Persistance des retours utilisateurs : Module de notation sur 10 et de recueil de commentaires persistés dans une table SQL dédiée.  
Exports tabulaires : Génération de fichiers CSV à la volée pour les synthèses de marché et la table de feedbacks.

Spécifications techniques
Backend : Python 3.11+, FastAPI, Uvicorn.  
Base de données : SQLite (paris_analytics.db).  
Client HTTP : HTTPX (asynchrone).
Frontend : HTML5, Vanilla CSS (thème sombre minimaliste), JavaScript natif, Leaflet.js.  
Source de données tierce : API Recherche d’Entreprises (DINSIC / base SIRENE).  
