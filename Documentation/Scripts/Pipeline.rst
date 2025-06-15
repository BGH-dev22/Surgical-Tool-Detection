Pipeline du Projet "SurgiSafe Pro"
==================================

1. Définition des Objectifs et Analyse des Besoins
--------------------------------------------------

**Objectif Principal** :
Développer un système intelligent de suivi des instruments chirurgicaux pour améliorer la sécurité en bloc opératoire.

**Fonctionnalités Cibles** :
- Détection et suivi en temps réel des instruments via une IA (YOLO).
- Génération d'alertes basées sur la durée d'utilisation ou l'absence d'instruments.
- Confirmation manuelle par un utilisateur et un agent médical.
- Interface utilisateur avec tableau de bord, statistiques, et export de données.
- Synchronisation vidéo en temps réel et ajout d'un mini-chatbot pour assistance.

**Contraintes** :
- Utilisation de Streamlit.
- Intégration de CV2, YOLO, et autres dépendances.
- Compatibilité avec des vidéos locales.
- Limites de performance matérielle.

**Public Cible** :
Équipes médicales.


2. Conception et Planification
------------------------------

**Architecture** :
- *Interface Utilisateur* : Streamlit pour une interface web interactive.
- *Modèle IA* : YOLOv8 pour la détection et le suivi des instruments.
- *Gestion d'État* : `SurgiSafeStateManager` pour stocker les données (instruments, alertes, stats).
- *Logique Métier* : `SurgiSafeCore` pour traiter les frames et gérer les alertes.
- *Chatbot* : Module simple intégré dans la sidebar pour répondre à des requêtes.

**Plan de Développement** :
- Étape 1 : Configurer l'environnement (bibliothèques, modèle YOLO).
- Étape 2 : Développer la détection et le suivi des instruments.
- Étape 3 : Ajouter les alertes et la confirmation manuelle.
- Étape 4 : Intégrer le tableau de bord et les exports.
- Étape 5 : Ajuster la synchronisation vidéo et ajouter le chatbot.
- Étape 6 : Tester et optimiser.


3. Développement
----------------

**Mise en Place de l'Environnement** :
- Installer Python, Streamlit, OpenCV, PyTorch, Ultralytics.
- Préparer un modèle YOLO entraîné (ex. `best.pt`).

**Implémentation des Modules** :
- *Détection* : Charger le modèle YOLO et traiter les frames vidéo.
- *Suivi* : Mettre à jour les positions et statuts des instruments.
- *Alertes* : Définir des seuils (10, 20, 30, 45 min) et gérer les confirmations.
- *Interface* : Créer une UI avec vidéo en direct, stats, et tableau de bord.
- *Synchronisation Vidéo* : Ajuster `time.sleep` avec le FPS natif.
- *Chatbot* : Ajouter une zone de texte avec réponses prédéfinies.


**Code Base** :
Utiliser le script principal `app.py` comme point d'entrée pour le système.

4. Intégration et Tests
-----------------------

**Tests Unitaires** :
- Vérifier la détection avec une vidéo de test.
- Vérifier les réponses du chatbot et les alertes.

**Tests Intégrés** :
- Lancer l'application complète et simuler un scénario complet.
- Vérifier les exports de données (CSV/JSON).

**Optimisation** :
- Ajuster `conf_threshold` et `iou_threshold` pour réduire les faux positifs.
- Réduire `target_width` si le FPS chute trop.





