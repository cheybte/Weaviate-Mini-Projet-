<<<<<<< HEAD
# Weaviate-Mini-Projet-
Ce mini-projet montre comment déployer **Weaviate** (base de données vectorielle) avec **Docker Compose**, importer des données depuis un fichier `data.json` et faire une **recherche sémantique** (chercher par le sens, pas uniquement par mots-clés).
=======
# Weaviate Mini-Projet (Docker) — Recherche Sémantique à partir d’un JSON

Ce mini-projet montre comment déployer **Weaviate** (base de données vectorielle) avec **Docker Compose**, importer des données depuis un fichier `data.json` et faire une **recherche sémantique** (chercher par le sens, pas uniquement par mots-clés).

---

## 1) Objectif du projet

- Déployer une **vector database** localement (sans cloud).
- Importer des Q/R (FAQ) dans Weaviate.
- Poser des questions avec des formulations différentes (paraphrases).
- Obtenir automatiquement la **réponse la plus compatible** avec la requête (Top-1).

---

## 2) Architecture (comment ça marche)

Le projet démarre **2 conteneurs** :

### A) `weaviate`
- C’est la base de données.
- Expose une API :
  - HTTP : `localhost:8082` (dans ce projet on mappe 8082 → 8080 du conteneur)
  - gRPC : `localhost:50051`

### B) `t2v-transformers`
- Service d’inférence (Transformers) qui calcule les **embeddings** localement.
- Weaviate lui envoie les textes et récupère leurs vecteurs.

### Flow complet (pipeline)
1. `docker compose up -d` → démarre Weaviate + Transformers
2. Le script Python :
   - crée la collection `FAQ` (schéma)
   - lit les données depuis `data.json`
   - insère les objets (question, answer, tag)
3. Pendant l’insertion :
   - Weaviate demande au container Transformers de vectoriser le texte
   - stocke (objet + vecteur) et indexe
4. Recherche :
   - la requête de l’utilisateur est vectorisée
   - Weaviate cherche les vecteurs les plus proches
   - renvoie l’objet le plus similaire (Top-1) → la meilleure réponse

---

## 3) Structure du projet
weaviate-mini-projet/
├─ docker-compose.yml
├─ data.json
├─ requirements.txt
└─ import_from_json.py


---

## 4) Prérequis

- Docker + Docker Compose
- Python 3
- WSL Ubuntu (dans mon cas)

---

## 5) Lancer le projet (Run)

### 5.1) Aller dans le dossier
```bash
cd /mnt/c/Users/mbedine/weaviate-mini-projet


5.2) Démarrer Weaviate + Transformers
docker compose up -d
docker compose ps

5.4) Créer un environnement virtuel Python + installer les dépendances

Sur Ubuntu/WSL, pip peut être bloqué (PEP 668), donc on utilise un venv :

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
5.5) Importer data.json + tester la recherche
python import_from_json.py

Tu verras plusieurs tests : on pose différentes questions (paraphrases) et le script affiche la question stockée trouvée + la réponse + le tag.

5.6) Arrêter les services
docker compose down
>>>>>>> a22d3c6 (Initial commit: Weaviate mini project)
<<<<<<< HEAD
# Weaviate-Mini-Projet-
Ce mini-projet montre comment déployer **Weaviate** (base de données vectorielle) avec **Docker Compose**, importer des données depuis un fichier `data.json` et faire une **recherche sémantique** (chercher par le sens, pas uniquement par mots-clés).
=======
# Weaviate Mini-Projet (Docker) — Recherche Sémantique à partir d’un JSON

Ce mini-projet montre comment déployer **Weaviate** (base de données vectorielle) avec **Docker Compose**, importer des données depuis un fichier `data.json` et faire une **recherche sémantique** (chercher par le sens, pas uniquement par mots-clés).

---

## 1) Objectif du projet

- Déployer une **vector database** localement (sans cloud).
- Importer des Q/R (FAQ) dans Weaviate.
- Poser des questions avec des formulations différentes (paraphrases).
- Obtenir automatiquement la **réponse la plus compatible** avec la requête (Top-1).

---

## 2) Architecture (comment ça marche)

Le projet démarre **2 conteneurs** :

### A) `weaviate`
- C’est la base de données.
- Expose une API :
  - HTTP : `localhost:8082` (dans ce projet on mappe 8082 → 8080 du conteneur)
  - gRPC : `localhost:50051`

### B) `t2v-transformers`
- Service d’inférence (Transformers) qui calcule les **embeddings** localement.
- Weaviate lui envoie les textes et récupère leurs vecteurs.

### Flow complet (pipeline)
1. `docker compose up -d` → démarre Weaviate + Transformers
2. Le script Python :
   - crée la collection `FAQ` (schéma)
   - lit les données depuis `data.json`
   - insère les objets (question, answer, tag)
3. Pendant l’insertion :
   - Weaviate demande au container Transformers de vectoriser le texte
   - stocke (objet + vecteur) et indexe
4. Recherche :
   - la requête de l’utilisateur est vectorisée
   - Weaviate cherche les vecteurs les plus proches
   - renvoie l’objet le plus similaire (Top-1) → la meilleure réponse

---

## 3) Structure du projet
weaviate-mini-projet/
├─ docker-compose.yml
├─ data.json
├─ requirements.txt
└─ import_from_json.py


---

## 4) Prérequis

- Docker + Docker Compose
- Python 3
- WSL Ubuntu (dans mon cas)

---

## 5) Lancer le projet (Run)

### 5.1) Aller dans le dossier
```bash
cd /mnt/c/Users/mbedine/weaviate-mini-projet


5.2) Démarrer Weaviate + Transformers
docker compose up -d
docker compose ps

5.4) Créer un environnement virtuel Python + installer les dépendances

Sur Ubuntu/WSL, pip peut être bloqué (PEP 668), donc on utilise un venv :

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
5.5) Importer data.json + tester la recherche
python import_from_json.py

Tu verras plusieurs tests : on pose différentes questions (paraphrases) et le script affiche la question stockée trouvée + la réponse + le tag.

5.6) Arrêter les services
docker compose down
>>>>>>> a22d3c6 (Initial commit: Weaviate mini project)
