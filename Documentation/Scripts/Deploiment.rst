=================================================
Interface et Déploiement de l'Analyseur Médical
=================================================

.. role:: red
   :class: red

.. role:: green
   :class: green

.. role:: blue
   :class: blue

.. role:: orange
   :class: orange

.. raw:: html

   <style>
   .red {color: #FF4444;}
   .green {color: #2ECC71;}
   .blue {color: #3498DB;}
   .orange {color: #E67E22;}
   </style>

:blue:`Vue d'Ensemble`
--------------------
L'interface d'analyse d'examens médicaux est une application web développée avec Streamlit qui permet l'analyse automatisée des résultats d'analyses sanguines. Elle intègre nos modèles OCR et d'analyse précédemment développés.

.. figure::  /Documentation/Images/interface_principale.jpeg
   :alt: Interface Principale de l'Application
   :align: center
   :width: 100%

   Interface principale de l'application d'analyse d'examens médicaux

:green:`Architecture de l'Interface`
--------------------------------
L'interface se compose de plusieurs modules interconnectés:

1. **Module d'Upload**
   - Limite de taille: 200MB par fichier
   - Formats supportés: PNG, JPG, JPEG, PDF, TXT, DOCX
   - Interface drag & drop intuitive

.. figure::  /Documentation/Images/extraction_text.jpeg
   :alt: Interface d'upload et d'extraction
   :align: center
   :width: 100%

   Module d'upload avec extraction de texte

:orange:`Workflow de l'Application`
-------------------------------

Processus d'Analyse
~~~~~~~~~~~~~~~~~~

1. **Upload et Extraction du Texte**

.. figure::  /Documentation/Images/biochimie_scan.jpeg
   :alt: Exemple de scan d'analyse biochimique
   :align: center
   :width: 100%

   Exemple de document d'analyse biochimique scanné

2. **Organisation des Données**

.. figure::  /Documentation/Images/organisation_data.jpeg
   :alt: Organisation des données extraites
   :align: center
   :width: 100%

   Interface d'organisation des données extraites

3. **Analyse et Résultats**

.. figure::  /Documentation/Images/analyse_results.jpeg
   :alt: Résultats de l'analyse
   :align: center
   :width: 100%

   Affichage des résultats de l'analyse

4. **Génération du Rapport**

.. figure::  /Documentation/Images/rapport_success.jpeg
   :alt: Génération du rapport
   :align: center
   :width: 100%

   Confirmation de génération du rapport

:blue:`Fonctionnalités Détaillées`
------------------------------

1. **Extraction de Texte**
   L'interface permet l'extraction automatique du texte à partir des documents scannés. Le système utilise notre modèle OCR optimisé pour garantir une reconnaissance précise des données médicales.

2. **Organisation des Données**
   Les données extraites sont automatiquement structurées selon les catégories d'analyses (biochimie, hématologie, etc.).

3. **Analyse Automatique**
   Le système analyse les valeurs extraites en les comparant aux normes médicales standard et identifie les anomalies potentielles.

4. **Génération de Rapports**
   L'interface permet de générer des rapports détaillés incluant l'analyse complète des résultats.

:green:`Guide d'Utilisation`
------------------------

1. **Téléchargement du Document**
   - Utilisez l'interface drag & drop ou le bouton "Browse files"
   - Formats acceptés: PNG, JPG, JPEG, PDF, TXT, DOCX
   - Taille limite: 200MB par fichier

2. **Extraction et Vérification**
   - Cliquez sur "Extraire le texte"
   - Vérifiez les données extraites
   - Utilisez "Organiser" pour structurer l'information

3. **Analyse des Résultats**
   - Lancez l'analyse avec le bouton "Analyser"
   - Examinez les résultats et les alertes
   - Générez le rapport final

:red:`Points d'Attention`
---------------------
- Qualité des scans requise: minimum 300 DPI
- Orientation correcte des documents
- Vérification manuelle des valeurs critiques
- Sauvegarde systématique des rapports générés




:green:`Conclusion`
--------------
Cette interface représente l'aboutissement de notre travail sur l'OCR médical et l'analyse automatisée. Elle combine nos différents modules dans une solution intégrée et facile d'utilisation, tout en maintenant la rigueur nécessaire au domaine médical.
