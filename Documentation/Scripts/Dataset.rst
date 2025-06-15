Jeu de Données
==============

Présentation Générale
----------------------

Le jeu de données utilisé dans ce projet est composé d’images stéréo issues de procédures chirurgicales réelles, réalisées avec un robot chirurgical **da Vinci Xi**. Les données ont été préparées dans le but de détecter, segmenter et suivre les instruments chirurgicaux à partir d’une séquence vidéo capturée en salle opératoire.

 Télécharger le Dataset
-------------------------

Vous pouvez télécharger le jeu de données depuis ce lien :

`<https://endovissub2017-roboticinstrumentsegmentation.grand-challenge.org/Downloads/>`_

Structure du Dataset
----------------------

Le dataset est organisé en **4 dossiers principaux**, chacun représentant une séquence vidéo ou une procédure distincte. À l’intérieur de chaque dossier, on retrouve :

- `left_frames` : Images issues de la caméra gauche (format RGB, recadrées et redimensionnées)

  .. image:: Surgical-Tool-Detection/Documentation/Images/left.png
     :alt: Exemple d'image de la caméra gauche
     :width: 400px
     :align: center

- `right_frames` : Images issues de la caméra droite
   .. image:: Surgical-Tool-Detection/Documentation/Images/right.png
     :alt: Exemple d'image de la caméra droite
     :width: 400px
     :align: center

- `ground_truth` : Dossiers contenant les annotations (masques) pour chaque instrument

  .. image:: Surgical-Tool-Detection/Documentation/Images/ground.png
     :alt: Exemple de masque binaire
     :width: 400px
     :align: center

  

- `camera_calibration.json` : Fichier de calibration stéréo spécifique à chaque séquence

Chaque dossier `ground_truth/` contient des sous-dossiers nommés selon les instruments annotés dans la vidéo, par exemple :

- `Right_Prograsp_Forceps_labels`
- `Left_Prograsp_Forceps_labels`
- `Maryland_Bipolar_Forceps_labels`
- `Right_Large_Needle_Driver_labels`
- `Left_Large_Needle_Driver_labels`
- `Prograsp_Forceps_labels`
- `Other_labels`

Fichiers d'Annotation
----------------------

Les annotations sont disponibles sous forme de **masques d’images**, encodant la présence et le type d’instruments :

- **Masque binaire** : chaque pixel = 255 si outil, 0 sinon.
- **Masque multi-classe** : chaque pixel correspond à un index de type d’instrument ou de partie anatomique.

Deux fichiers JSON sont également fournis pour le mapping des annotations :

- `parts_mapping.json` : pour associer chaque partie de l'instrument à un identifiant numérique
- `type_mapping.json` : pour associer chaque type d'instrument à un identifiant unique

Format des Images et Échantillonnage
--------------------------------------

- Les images sont extraites de vidéos à une fréquence de **2 Hz** (images/seconde), depuis des vidéos capturées initialement à 30 Hz.
- Résolution : **1280×1024 pixels**
- Recadrage appliqué depuis le point (320, 28)
- Chaque image possède une version gauche et droite, permettant une reconstruction 3D ou estimation de profondeur.

Calibration des Caméras
------------------------

Le fichier `camera_calibration.json` contient les paramètres intrinsèques et extrinsèques des caméras gauche et droite, permettant :

- Reconstruction 3D à partir de la disparité
- Alignement des vues pour améliorer la segmentation
- Rectification des distorsions d’image

Utilisation pour l’Entraînement
-------------------------------

Les données suivantes sont utilisées pour entraîner le modèle :

- Images : `left_frames/`
- Masques d’annotation : `ground_truth/`
- Mapping JSON : `type_mapping.json`, `parts_mapping.json`
- Calibration : `camera_calibration.json` (optionnel selon le modèle utilisé)

Classes d’Instruments Chirurgicaux
----------------------------------

Le dataset comprend les instruments suivants :

- **Prograsp Forceps** (droite et gauche)
- **Maryland Bipolar Forceps**
- **Large Needle Driver** (droite et gauche)
- **Instruments divers** (`Other_labels`)

Ces classes sont les cibles principales pour les tâches de détection, segmentation ou suivi d’instruments chirurgicaux.

