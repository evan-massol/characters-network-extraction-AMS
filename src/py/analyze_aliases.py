import json
from collections import defaultdict
from utils import filter_antidict, clean_entity_name

def load_aliases_report(filepath="./json/aliases_report.json"):
    """Load the generated alias report."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_entities_output(filepath="./json/entities_output.json"):
    """Load the entities file and clean entity names."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Clean all entity names in-place
        for chapter in data:
            for entity_type in ["PER", "MISC"]:
                for entity in chapter["entities"][entity_type]:
                    entity["name"] = clean_entity_name(entity["name"])
        return data

def analyze_aliases(aliases_report):
    """Analyze and display detected aliases."""
    print("=" * 80)
    print("ALIAS ANALYSIS REPORT")
    print("=" * 80)
    
    for entity_type in ["PER", "MISC"]:
        if not aliases_report[entity_type]:
            continue
            
        print(f"\n{'─' * 80}")
        print(f"TYPE: {entity_type}")
        print(f"{'─' * 80}")
        
        # Regrouper par forme canonique
        grouped = defaultdict(list)
        for alias, canonical in aliases_report[entity_type].items():
            grouped[canonical].append(alias)
        
        # Afficher chaque groupe
        for canonical, aliases in sorted(grouped.items()):
            print(f"\n  ✓ {canonical}")
            for alias in sorted(aliases):
                print(f"    ← {alias}")
                
def generate_manual_suggestions():
    """
    Génère des suggestions pour le fichier manual_aliases.json
    à partir du rapport d'alias détectés.
    """
    print("\n" + "=" * 80)
    print("SUGGESTIONS FOR MANUAL ALIASES")
    print("=" * 80)
    print("\nCopiez ces lignes dans manual_aliases.json si elles sont correctes :")
    print("\n```json")

    # Charger le rapport d'alias
    try:
        aliases_report = load_aliases_report()
    except Exception as e:
        print(f"Erreur lors du chargement du rapport d'alias : {e}")
        print("{}\n```")
        return

    suggestions = {"PER": {}, "MISC": {}}

    for entity_type in ["PER", "MISC"]:
        canonical_to_aliases = defaultdict(list)
        for alias, canonical in aliases_report[entity_type].items():
            if alias != canonical:
                canonical_to_aliases[canonical].append(alias)
        for canonical, aliases in canonical_to_aliases.items():
            # On ne propose que si plusieurs alias pour une même forme canonique
            if len(aliases) > 0:
                suggestions[entity_type][canonical] = sorted(aliases)

    print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    print("```")

def show_entity_stats(entities_output, antidict=None):
    """Affiche des statistiques sur les entités détectées (hors antidictionnaire si fourni)."""
    print("\n" + "=" * 80)
    print("STATISTIQUES GLOBALES")
    print("=" * 80)
    
    total_per = 0
    total_loc = 0
    total_misc = 0
    
    unique_per = set()
    unique_loc = set()
    unique_misc = set()
    
    for chapter in entities_output:
        for entity in chapter["entities"]["PER"]:
            if not antidict or entity["name"].lower() not in antidict:
                total_per += entity["count"]
                unique_per.add(entity["name"])
        for entity in chapter["entities"]["MISC"]:
            if not antidict or entity["name"].lower() not in antidict:
                total_misc += entity["count"]
                unique_misc.add(entity["name"])
    
    print(f"\nPersonnes (PER):")
    print(f"  - {len(unique_per)} entités uniques")
    print(f"  - {total_per} occurrences totales")
    
    print(f"\nDivers (MISC):")
    print(f"  - {len(unique_misc)} entités uniques")
    print(f"  - {total_misc} occurrences totales")

def main():
    """Fonction principale."""
    print("\nAnalyse des alias détectés...\n")
    
    try:
        aliases_report = load_aliases_report()
        entities_output = load_entities_output()
        antidict = filter_antidict("fonctionnels_fr.txt")
        
        # Analyses
        show_entity_stats(entities_output, antidict=antidict)
        analyze_aliases(aliases_report)
        generate_manual_suggestions()
        
        print("\n" + "=" * 80)
        print("Analyse terminée !")
        print("=" * 80)
        print("\nConsultez manual_aliases.json pour ajouter vos corrections manuelles.")
        
    except FileNotFoundError as e:
        print(f"Erreur: Fichier non trouvé - {e}")
        print("   Assurez-vous d'avoir exécuté FirstInLeaderboard.py d'abord.")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
