================================
Modèle de Détection et de Suivi
================================

.. contents::
   :local:
   :depth: 2

Introduction
============

Ce document décrit le modèle de détection et de suivi des instruments chirurgicaux utilisé dans l'application **SurgiSafe Pro**. Ce modèle, basé sur YOLOv8 (You Only Look Once, version 8), est conçu pour identifier et suivre en temps réel divers instruments chirurgicaux dans des vidéos ou flux en direct, offrant une solution pour améliorer la sécurité en salle d'opération.

Caractéristiques Principales
============================

- **Détection en Temps Réel** : Utilise YOLOv8 pour détecter les instruments avec une précision élevée.
- **Suivi Persistant** : Intègre un mécanisme de suivi basé sur les identifiants de piste pour suivre les instruments à travers les trames.
- **Seuils Ajustables** : Permet de configurer les seuils de confiance et d'intersection sur union (IoU) pour optimiser la détection.
- **Compatibilité Multi-Dispositifs** : Fonctionne sur CPU ou GPU (si CUDA est disponible).

Configuration du Modèle
======================

Chargement du Modèle
--------------------

Le modèle est chargé à partir d'un fichier `.pt` pré-entraîné. Par exemple :

- Chemin par défaut : ``C:/Users/Hp/runs/train/exp_endovis_i5/weights/best.pt``
- Commande de chargement dans l'interface : Bouton "🔄 Load Model" dans la barre latérale.

Paramètres de Détection
-----------------------

Les paramètres suivants peuvent être ajustés dans la barre latérale de l'application :

- **Seuil de Confiance** : Plage de 0.01 à 1.0 (valeur par défaut : 0.05). Détermine la probabilité minimale pour qu'une détection soit considérée comme valide.
- **Seuil IoU** : Plage de 0.1 à 1.0 (valeur par défaut : 0.2). Contrôle la suppression non maximale pour éviter les détections redondantes.

Classes d'Instruments Détectés
------------------------------

Le modèle est entraîné pour reconnaître les classes suivantes :

- Right_Prograsp_Forceps_labels
- Other_labels
- Maryland_Bipolar_Forceps_labels
- Left_Prograsp_Forceps_labels
- Right_Large_Needle_Driver_labels
- Left_Large_Needle_Driver_labels
- Prograsp_Forceps_labels

Chaque classe est associée à un identifiant unique pour le suivi.

Performance
===========

- **Temps de Chargement** : Enregistré lors du chargement initial (dépend du matériel).
- **FPS** : Mesuré en temps réel et affiché dans l'interface (objectif : maintenir > 10 FPS).
- **Taille du Modèle** : Indiquée en Mo après chargement.

Utilisation
===========

1. **Chargement** : Sélectionnez le chemin du fichier modèle et cliquez sur "Load Model".
2. **Configuration** : Ajustez les seuils de détection selon les besoins.
3. **Analyse** : Chargez une vidéo ou un flux et démarrez l'analyse avec "Start Analysis".
4. **Suivi** : Les instruments détectés sont suivis avec des identifiants de piste et des niveaux de risque (normal, warning, danger, critical).

Limites
=======

- Nécessite un fichier modèle pré-entraîné valide.
- Performance dépendante des ressources matérielles (recommandé : GPU avec CUDA).
- Peut ne pas détecter des instruments dans des conditions d'éclairage extrêmes ou avec des occlusions importantes.

Améliorations Futures
=====================

- Ajout de la détection d'instruments supplémentaires.
- Optimisation pour des FPS plus élevés sur du matériel léger.
- Intégration d'une validation manuelle pour les alertes critiques.

Contact
=======

Pour toute question ou suggestion, contactez l'équipe de développement via [houda.bgh99@gmail.com].

