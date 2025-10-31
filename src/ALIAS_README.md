# Système de Gestion des Alias d'Entités Nommées

## 🎯 Objectif

Ce système permet de regrouper automatiquement les variantes d'une même entité (par exemple "Hari Seldon" et "Seldon") pour améliorer la qualité de l'extraction des entités nommées.

## 📋 Fonctionnement

### 1. Détection Automatique

Le système détecte automatiquement les relations entre :
- **Noms complets et noms courts** : "Hari Seldon" → "Seldon"
- **Prénoms et noms complets** : "Hari Seldon" → "Hari"
- **Variantes avec parties communes**

**Algorithme :**
- Les entités les plus longues deviennent les formes "canoniques" (références)
- Les noms courts qui sont des sous-parties sont automatiquement regroupés
- Exemple : "Seldon" (33 occurrences) + "Hari Seldon" (5 occurrences) = "Hari Seldon" (38 occurrences)

### 2. Alias Manuels

Pour les cas que l'algorithme ne peut pas détecter automatiquement (titres, surnoms, etc.), vous pouvez définir des alias manuels dans `manual_aliases.json` :

```json
{
  "PER": {
    "Empereur": "Cléon I",
    "Sire": "Cléon I",
    "Premier ministre": "Eto Demerzel"
  },
  "LOC": {
    "Capitale": "Trantor"
  },
  "MISC": {
  }
}
```

**Les alias manuels ont TOUJOURS priorité sur la détection automatique.**

## 🚀 Utilisation

### Étape 1 : Exécuter l'extraction

```bash
cd src
python FirstInLeaderboard.py
```

**Sorties générées :**
- `entities_output.json` : Toutes les entités avec comptages fusionnés
- `aliases_report.json` : Liste de tous les alias détectés (auto + manuels)
- `EvanMASSOL_MartinGERIS.csv` : Graphes (avec entités fusionnées)

### Étape 2 : Analyser les résultats

```bash
python analyze_aliases.py
```

Ce script affiche :
- 📊 Statistiques globales
- 🔗 Liste des regroupements effectués
- ⚠️  Alertes sur les regroupements potentiellement problématiques
- 💡 Suggestions d'alias manuels

### Étape 3 : Affiner avec des alias manuels

1. Consultez le rapport de `analyze_aliases.py`
2. Identifiez les erreurs ou les cas manquants
3. Ajoutez vos corrections dans `manual_aliases.json`
4. Ré-exécutez `FirstInLeaderboard.py`

## 📁 Structure des Fichiers de Sortie

### entities_output.json

```json
[
  {
    "book_code": "paf",
    "file": "chapter_1.txt",
    "chapter_number": 0,
    "entities": {
      "PER": [
        {
          "name": "Hari Seldon",    // Forme canonique
          "type": "PER",
          "count": 38                // Total fusionné
        }
      ],
      "LOC": [...],
      "MISC": [...]
    },
    "aliases": {                     // Transparence des regroupements
      "PER": {
        "Seldon": "Hari Seldon",
        "Empereur": "Cléon I"
      }
    },
    "summary": {
      "total_persons": 10,
      "total_locations": 7,
      "total_misc": 3
    }
  }
]
```

### aliases_report.json

Liste globale de tous les alias utilisés dans l'ensemble des livres :

```json
{
  "PER": {
    "Seldon": "Hari Seldon",
    "Demerzel": "Eto Demerzel",
    "Empereur": "Cléon I"
  },
  "LOC": {...},
  "MISC": {...}
}
```

## 🔧 Personnalisation

### Modifier les règles de détection automatique

Dans `FirstInLeaderboard.py`, fonction `build_entity_aliases()` :

```python
# Augmenter la longueur minimale pour éviter les initiales
if len(last_word) > 3:  # au lieu de > 2
    ...
```

### Filtrer certains types d'alias

Vous pouvez désactiver certaines détections automatiques :

```python
# Ne créer des alias QUE pour les noms de famille
if len(words) >= 2:
    last_word = words[-1]
    # ... garder seulement cette partie
```

## 📊 Exemples de Regroupements

### Cas typiques détectés automatiquement :

| Entités trouvées | Forme canonique | Occurrences totales |
|-----------------|-----------------|---------------------|
| "Hari Seldon", "Seldon" | "Hari Seldon" | 38 |
| "Eto Demerzel", "Demerzel" | "Eto Demerzel" | 11 |
| "Chetter Hummin", "Hummin" | "Chetter Hummin" | 15 |

### Cas nécessitant des alias manuels :

| Alias | Forme canonique | Raison |
|-------|----------------|---------|
| "Empereur" | "Cléon I" | Titre |
| "Sire" | "Cléon I" | Titre honorifique |
| "Premier ministre" | "Eto Demerzel" | Fonction |

## ⚠️  Bonnes Pratiques

1. **Vérifiez toujours** : Utilisez `analyze_aliases.py` après chaque exécution
2. **Noms courts ambigus** : Faites attention aux noms d'une seule partie qui pourraient référer à plusieurs personnes
3. **Priorité aux alias manuels** : En cas de doute, définissez explicitement dans `manual_aliases.json`
4. **Testez progressivement** : Commencez avec peu d'alias manuels, ajoutez au fur et à mesure

## 🐛 Dépannage

### "Trop d'entités regroupées ensemble"

→ Ajoutez une exception dans `manual_aliases.json` ou ajustez les règles de détection

### "Certaines variantes ne sont pas détectées"

→ Ajoutez-les manuellement dans `manual_aliases.json`

### "Le rapport ne s'affiche pas"

→ Assurez-vous d'avoir exécuté `FirstInLeaderboard.py` au moins une fois pour générer les fichiers

## 📝 Notes Techniques

- Les alias manuels sont chargés depuis `manual_aliases.json` à chaque exécution
- Le système préserve TOUJOURS la forme canonique la plus longue
- Les graphes NetworkX utilisent automatiquement les formes canoniques
- L'UTF-8 est préservé dans tous les exports JSON
