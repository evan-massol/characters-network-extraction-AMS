"""
Utility script to analyze detected aliases and generate suggestions.
Use this script to:
- View all groupings made
- Identify potential errors
- Generate suggestions for manual_aliases.json
"""

import json
from collections import defaultdict

def load_aliases_report(filepath="./json/aliases_report.json"):
    """Load the generated alias report."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_entities_output(filepath="./json/entities_output.json"):
    """Load the entities file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_aliases(aliases_report):
    """Analyze and display detected aliases."""
    print("=" * 80)
    print("ALIAS ANALYSIS REPORT")
    print("=" * 80)
    
    for entity_type in ["PER", "LOC", "MISC"]:
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

def find_potential_errors(entities_output):
    """
    Identify potentially erroneous groupings
    (e.g., short names that could belong to multiple people)
    """
    print("\n" + "=" * 80)
    print("CHECKING POTENTIALLY PROBLEMATIC GROUPINGS")
    print("=" * 80)
    
    # Collect all names and their frequencies
    all_names = defaultdict(int)
    for chapter in entities_output:
        for entity in chapter["entities"]["PER"]:
            all_names[entity["name"]] += entity["count"]
    
    # Identifier les noms très fréquents (pourraient être sur-groupés)
    high_freq = {name: count for name, count in all_names.items() if count > 100}
    
    if high_freq:
        print("\n⚠ Entités avec beaucoup d'occurrences (vérifiez le regroupement):")
        for name, count in sorted(high_freq.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {name}: {count} occurrences")
    
    # Identifier les noms très courts (1 mot) qui pourraient être ambigus
    short_names = {name: count for name, count in all_names.items() 
                   if len(name.split()) == 1 and count > 10}
    
    if short_names:
        print("\n⚠ Noms courts fréquents (pourraient être ambigus):")
        for name, count in sorted(short_names.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {name}: {count} occurrences")

def generate_manual_suggestions(aliases_report):
    """
    Generate suggestions for the manual_aliases.json file
    based on detected patterns.
    """
    print("\n" + "=" * 80)
    print("SUGGESTIONS FOR MANUAL ALIASES")
    print("=" * 80)
    print("\nCopy these lines into manual_aliases.json if they are correct:")
    print("\n```json")
    
    suggestions = {"PER": {}, "LOC": {}, "MISC": {}}
    
    # For now, just display the structure
    # You can enrich this logic with your own rules
    
    print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    print("```")

def show_entity_stats(entities_output):
    """Affiche des statistiques sur les entités détectées."""
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
            total_per += entity["count"]
            unique_per.add(entity["name"])
        for entity in chapter["entities"]["LOC"]:
            total_loc += entity["count"]
            unique_loc.add(entity["name"])
        for entity in chapter["entities"]["MISC"]:
            total_misc += entity["count"]
            unique_misc.add(entity["name"])
    
    print(f"\nPersonnes (PER):")
    print(f"  - {len(unique_per)} entités uniques")
    print(f"  - {total_per} occurrences totales")
    
    print(f"\nLieux (LOC):")
    print(f"  - {len(unique_loc)} entités uniques")
    print(f"  - {total_loc} occurrences totales")
    
    print(f"\nDivers (MISC):")
    print(f"  - {len(unique_misc)} entités uniques")
    print(f"  - {total_misc} occurrences totales")

def main():
    """Fonction principale."""
    print("\n🔍 Analyse des alias détectés...\n")
    
    try:
        aliases_report = load_aliases_report()
        entities_output = load_entities_output()
        
        # Analyses
        show_entity_stats(entities_output)
        analyze_aliases(aliases_report)
        find_potential_errors(entities_output)
        generate_manual_suggestions(aliases_report)
        
        print("\n" + "=" * 80)
        print("✓ Analyse terminée !")
        print("=" * 80)
        print("\nConsultez manual_aliases.json pour ajouter vos corrections manuelles.")
        
    except FileNotFoundError as e:
        print(f"❌ Erreur: Fichier non trouvé - {e}")
        print("   Assurez-vous d'avoir exécuté FirstInLeaderboard.py d'abord.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
