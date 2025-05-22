Détection et Suivi d’Outils Chirurgicaux avec Alerte
=====================================================

Objectif du projet
------------------
Développer une application de vision par ordinateur capable de détecter, suivre et alerter en cas d’oubli d’un outil chirurgical dans le corps d’un patient, à partir d’un flux vidéo en direct (via scrcpy/tablette ou caméra connectée).

Pipeline Global
---------------

1. Acquisition Vidéo
~~~~~~~~~~~~~~~~~~~~
- Source : Flux en direct depuis une tablette Android via scrcpy ou caméra Bluetooth.
- Technologie : `scrcpy`, `OpenCV`.

2. Prétraitement d’images
~~~~~~~~~~~~~~~~~~~~~~~~~
- Redimensionnement, normalisation.
- Conversion en format compatible avec le modèle de détection.

3. Détection d’objets chirurgicaux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Modèle utilisé : `YOLOv8` 
- Entraînement préalable sur un dataset médical annoté.
- Sortie : Bounding boxes, classes (pinces, scalpels, etc.)

4. Suivi des objets détectés
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Algorithme : `DeepSORT`.
- Objectif : attribuer un ID unique à chaque outil pour éviter les doublons et suivre leur position dans le temps.

5. Analyse et Alerte
~~~~~~~~~~~~~~~~~~~~
- Vérification en fin d’opération : si un outil est détecté mais non retiré.
- Système d’alerte :
  - Visuelle : sur l’écran
  - Sonore : bip
  - Enregistrement : alerte sauvegardée dans un fichier (log .txt ou CSV)

6. Interface Utilisateur
~~~~~~~~~~~~~~~~~~~~~~~~
- Application interactive pour le personnel médical.
- Affichage vidéo, overlays des détections, notifications.

Pipeline Technique
------------------

1. Chargement du modèle YOLOv8
2. Lecture image par image via OpenCV
3. Détection → suivi (DeepSORT) → vérification
4. Alerte déclenchée si nécessaire
5. Résultat sauvegardé et visualisé

Technologies utilisées
----------------------
- Python 3.10
- OpenCV
- Ultralytics YOLOv8
- DeepSORT
- scrcpy (acquisition vidéo)
- TensorFlow 
- GUI possible :Streamlit 



