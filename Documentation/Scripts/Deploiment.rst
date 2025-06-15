==============================
Documentation de l'Interface SurgiSafe Pro
==============================

.. image:: Surgical-Tool-Detection/Documentation/Images/SurgiSafe.png
   :align: center
   :alt: Logo SurgiSafe Pro

Introduction
============

**SurgiSafe Pro** est une application basée sur **Streamlit** qui permet le **suivi intelligent des instruments chirurgicaux en temps réel** à partir d'une vidéo.

Elle utilise le modèle **YOLOv8** pour la détection d'objets, un système de **suivi avec identifiants uniques**, et une **analyse temporelle** pour identifier les instruments oubliés ou à risque.

L'interface offre :
- une **visualisation en direct**,
- des **statistiques dynamiques**,
- des **alertes automatiques**,
- des **options d'exportation des données**.

.. image:: Surgical-Tool-Detection/Documentation/Images/interface.png
   :align: center
   :alt: Interface principale de SurgiSafe Pro

Fonctionnalités Principales
===========================

1. Chargement et Configuration du Modèle
----------------------------------------

- **Chargement du Modèle** : via la barre latérale (par défaut : ``C:/Users/Hp/runs/train/exp_endovis_i5/weights/best.pt``).
- **Validation** : vérifie l'existence du fichier et signale les erreurs.
- **Configuration Avancée** : ajustement des seuils de confiance (0.01 à 1.0) et d'IoU (0.1 à 1.0).

.. image:: Surgical-Tool-Detection/Documentation/Images/model.png
   :align: center
   :alt: Configuration du modèle YOLOv8

2. Sélection et Traitement de la Source Vidéo
---------------------------------------------

- **Upload de Vidéo** : formats supportés : MP4, AVI, MOV, MKV.
- **Validation Vidéo** : métadonnées (durée, frames, FPS).
- **Traitement Temps Réel** : redimension adaptatif (320 à 1280 px), skip frames si FPS < 10.

.. image:: Surgical-Tool-Detection/Documentation/Images/video.png
   :align: center
   :alt: Upload et lecture de la vidéo chirurgicale

3. Détection et Suivi des Instruments
-------------------------------------

- **Détection Spatiale** : avec YOLOv8 (ex. : *Right_Prograsp_Forceps*).
- **Suivi Temporel** : identifiants uniques (Track ID), moyenne glissante des bbox.
- **Historique** : 50 dernières détections par instrument.

.. image::Surgical-Tool-Detection/Documentation/Images/progr.png
   :align: center
   :alt: Détection et suivi des instruments chirurgicaux

4. Analyse Temporelle et Gestion des Risques
--------------------------------------------

- **Durée de Présence** :
  - Normal : < 10 min
  - Warning : 10–20 min
  - Danger : 20–30 min
  - Critical : > 30 min
  - Extended : > 45 min
- **Mouvement** : distance parcourue.
- **Statut** : *active*, *lost*, *removed*.

.. image:: Surgical-Tool-Detection/Documentation/Images/alerte.png
   :align: center
   :alt: Analyse temporelle des instruments et gestion des risques

5. Système d’Alerte
-------------------

- **Génération d’Alerte** : seuils personnalisables.
- **Affichage** : messages visuels avec emojis : ⚠️ 🔶 🚨 💀
- **Sonore** : option d'alerte audio (*fichier requis : beep.mp3*).
- **Historique** : jusqu’à 100 alertes.


6. Visualisation et Annotations
-------------------------------

- **Vidéo Annotée** : boîtes englobantes colorées (vert, jaune, orange, rouge, violet).
- **Overlay Système** : heure, FPS, durée, n° d'instruments actifs.
- **Indicateurs** : cercles de statut colorés.

.. image:: Surgical-Tool-Detection/Documentation/Images/story.png
   :align: center
   :alt: Visualisation annotée de la vidéo avec overlay dynamique

7. Tableau de Bord de Performance
---------------------------------

- **Statistiques Temps Réel** : FPS, durée, alertes, instruments actifs.
- **Graphiques** :
  - Detections par frame
  - Répartition des risques
  - Types d’alertes
- **Tableau Instruments** : nom, ID, durée, statut, confiance, mouvement.

.. image:: Surgical-Tool-Detection/Documentation/Images/diag.png
   :align: center
   :alt: Tableau de bord en temps réel avec graphiques

8. Exportation de Données
--------------------------

- **Instruments** : CSV avec ID, nom, durée, statut, risque.
- **Alertes** : CSV avec timestamp, niveau, message.
- **Détections** : CSV par frame.
- **Rapport Complet** : fichier JSON (session complète).


9. Contrôles et Paramètres
---------------------------

- **Démarrer/Arrêter** l’analyse.
- **Réinitialiser** la session.
- **Générer un rapport** JSON.
- **Paramètres Avancés** : sons, seuils, export auto.

.. image:: Surgical-Tool-Detection/Documentation/Images/control.png
   :align: center
   :alt: Commandes de contrôle et paramètres de session

Configuration Requise
=====================

- **Dépendances** :
  - ``streamlit``, ``ultralytics``, ``cv2``, ``numpy``, ``pandas``, ``plotly``, ``torch``
- **Modèle YOLOv8** : ``best.pt``
- **Vidéo** : formats MP4, AVI, MOV, MKV
- **Système** : support GPU (CUDA) ou CPU

Utilisation
===========

1. Chargez un modèle via la barre latérale.
2. Téléchargez une vidéo.
3. Ajustez les paramètres.
4. Lancez l’analyse.
5. Observez les alertes et statistiques.
6. Exportez les résultats.


Téléchargement des Données
===========================

Le dataset d'entraînement peut être téléchargé depuis :

- **EndoVis Instrument Dataset** : https://endovissub-instrument.grand-challenge.org/


   Veuillez respecter les licences de dataset utilisé.

