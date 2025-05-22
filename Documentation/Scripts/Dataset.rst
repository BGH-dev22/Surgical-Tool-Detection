Suivi Chirurgical et Détection d'Outils
=======================================

Présentation
------------

.. note::

   Ce projet a pour objectif la **détection et le suivi des outils chirurgicaux en temps réel**, dans le but de prévenir les oublis d'instruments lors des interventions chirurgicales. Il s'inscrit dans une démarche d'amélioration de la sécurité des soins grâce à l'intelligence artificielle.

Collecte des Données
====================

Le dataset utilisé dans ce projet provient de plusieurs sources complémentaires, sélectionnées afin d'assurer une diversité représentative des contextes chirurgicaux.

Sources principales :
---------------------

- **Flux vidéo de robots chirurgicaux (Robot Flow)**  
  Séquences vidéo issues de chirurgies assistées par robot, capturant des cas réels avec une grande variété d’outils.

- **Vidéos annotées de procédures chirurgicales**  
  Vidéos issues de bases de données publiques et privées, déjà annotées pour l’apprentissage supervisé.

- **Simulations en environnement contrôlé**  
  Données générées artificiellement avec des outils de simulation pour renforcer la diversité et la robustesse du modèle.

Cette approche multi-sources permet une **meilleure généralisation du modèle** à divers environnements opératoires.

Catégories d’Outils Chirurgicaux
--------------------------------

1. Pinces  
2. Ciseaux  
3. Écarteurs  
4. Aiguilles  
5. Autres instruments spécifiques...

Structure des Données
---------------------

Exemple d'annotation d'une image :

.. code-block:: json
   :caption: Structure d'une annotation JSON

   {
       "frame": 266,
       "objects": [
           {"class": "pince", "bbox": [x1, y1, x2, y2]},
           {"class": "ciseaux", "bbox": [x1, y1, x2, y2]}
       ]
   }

Exemple visuel du dataset
--------------------------

.. image:: /Documentation/Images
/bisturi1_jpg.rf.07e2b0050d29fcc4b426c1f8a96b7b57.jpg
   :width: 500px
   :alt: Exemple d’image annotée du dataset
   :align: center

Spécifications Techniques
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Format des données
     - Images JPG + fichiers d’annotation YAML / TXT / JSON
   * - Nombre total d'images
     - Environ 4000 images
   * - Résolution typique
     - 640x640 pixels
  

Utilisation du Modèle
---------------------

.. code-block:: python
   :linenos:

    from ultralytics import YOLO

    # Chargement du modèle pré-entraîné
    model = YOLO('yolov8n.pt')

    # Entraînement sur le dataset chirurgical
    results = model.train(
        data=r'C:\Users\Hp\Desktop\docs\data\detectsurgical\data.yaml',
        epochs=10,
        imgsz=640,
        batch=16
    )

Interface Utilisateur
---------------------

Une interface graphique a été développée à l'aide de **Streamlit**, facilitant l’utilisation du système pour le personnel médical.

.. image:: /Documentation/Images/streamlit.png
   :width: 600px
   :alt: Interface Streamlit de détection
   :align: center

Cette interface permet :
- de **lancer une détection en temps réel** à partir d’un flux vidéo ou d’une URL,
- de **visualiser les résultats image par image**,
- d’afficher une **alerte** en cas de détection d’un outil persistant.

Perspectives Futures
--------------------

.. note::

   Les améliorations envisagées pour les futures versions du système incluent :

   - Intégration d’un **module d’alerte audio/visuelle** en cas de détection anormale
   - Ajout d’un **module de classification des opérations** selon la complexité ou le risque
   - Exportation automatique de **rapports de suivi** pour les dossiers médicaux

Contact et Support
------------------

.. tip::

   Pour toute question, suggestion ou demande de collaboration, veuillez nous contacter via :

   - Email : *[houda.bgh99@exemple.com]*

