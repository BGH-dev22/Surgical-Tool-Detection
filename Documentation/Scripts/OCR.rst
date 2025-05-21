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
   .red {color: red;}
   .green {color: green;}
   .blue {color: blue;}
   .orange {color: orange;}
   </style>

Benchmark OCR d'Analyses Sanguines
================================

Introduction
-----------

Dans le domaine médical, l'exactitude des données est primordiale. C'est dans cette optique que nous avons réalisé un benchmark approfondi de trois systèmes OCR sur nos analyses sanguines. Notre objectif était simple : déterminer quel système de reconnaissance de caractères offre la meilleure fiabilité pour la numérisation des résultats d'analyses médicales.

`Notebook Jupyter </Documentation/notebooks/benchmark__ocripynb.ipynb>`_


Architecture du Benchmark
------------------------

.. image:: /Documentation/Images/image4.png
   :alt: Structure des fichiers

Le benchmark repose sur une architecture binaire : un dossier 'ground_truth' contenant nos textes de référence, et un dossier 'images_analyse' regroupant nos scans à traiter. Cette approche nous permet de comparer directement les résultats OCR avec les données originales de nos 20 analyses sanguines.

Résultats de notre étude
------------------------

:blue:`Doctr : L'équilibriste`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /Documentation/Images/image1.png
   :alt: Résultats Doctr

Doctr se révèle être le système le plus équilibré de notre benchmark. Sur nos 20 analyses sanguines, il atteint une :green:`précision de 84%` et un temps de traitement de :blue:`24,75 secondes` par document. Son F1 Score de :green:`0,79` confirme sa constance dans le traitement de nos documents médicaux.

.. code-block:: python
    :emphasize-lines: 1,2

    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor

    model = ocr_predictor(pretrained=True)
    for i in range(1, 21):  # Pour nos 20 analyses
        image_path = f"images_analyse/{i}.jpg"
        doc = DocumentFile.from_images(image_path)
        result = model(doc)

:green:`EasyOCR : Le champion de la précision`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /Documentation/Images/image2.png
   :alt: Résultats EasyOCR

EasyOCR excelle sur nos analyses sanguines avec :green:`87% de précision` et un F1 Score de :green:`0,83`. Son temps de traitement de :orange:`54,36 secondes` par document est plus long, mais sa précision sur nos paramètres biologiques est remarquable.

.. code-block:: python
    :emphasize-lines: 1

    import easyocr
    import os

    reader = easyocr.Reader(['fr'])
    image_dir = 'images_analyse'
    for img in sorted(os.listdir(image_dir)):
        result = reader.readtext(os.path.join(image_dir, img))

:red:`PaddleOCR : La rapidité au détriment de la précision`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /Documentation/Images/image3.png
   :alt: Résultats PaddleOCR

Sur nos analyses sanguines, PaddleOCR se montre décevant avec une :red:`précision de seulement 43%` et un F1 Score de :red:`0,32`, malgré sa rapidité de :green:`4,41 secondes` par document.

.. code-block:: python
    :emphasize-lines: 1

    from paddleocr import PaddleOCR
    import glob

    ocr = PaddleOCR(use_angle_cls=True, lang='fr')
    for img_path in glob.glob('images_analyse/*.jpg'):
        result = ocr.ocr(img_path)

Implications pratiques
--------------------

Nos résultats sur ces 20 analyses sanguines orientent clairement les choix technologiques :

- Dans nos petites structures médicales, :green:`EasyOCR` représente une solution fiable. Sa précision supérieure sur nos paramètres biologiques compense largement son temps de traitement plus long.

- Nos grands centres médicaux trouvent en :blue:`Doctr` un allié précieux. Sa combinaison de vitesse et de précision permet de traiter efficacement de grands volumes d'analyses tout en maintenant un niveau de fiabilité acceptable.

- Quant à :red:`PaddleOCR`, nos tests montrent qu'il n'est pas adapté aux analyses sanguines, le risque d'erreur étant trop élevé.

Configuration matérielle
----------------------

Pour nos tests, nous avons utilisé une configuration robuste qui s'est révélée nécessaire pour des performances optimales :

- RAM : :blue:`16 GB minimum`
- GPU : :blue:`Carte graphique dédiée requise`
- OS : Linux/Windows/MacOS

Notre choix final
---------------

Après l'analyse approfondie de nos 20 documents d'analyses sanguines, :blue:`Doctr` s'impose comme le meilleur choix global. Cette décision s'appuie sur plusieurs facteurs clés :

- :green:`Précision` : 84% (proche des 87% d'EasyOCR)
- :blue:`Temps de traitement` : 24,75 secondes (deux fois plus rapide qu'EasyOCR)
- :green:`F1 Score` : 0,79 (fiabilité constante)

En contexte réel d'analyses sanguines, cette combinaison de vitesse et de précision fait toute la différence. Le gain de temps significatif permet aux laboratoires de traiter plus d'analyses, tout en maintenant un niveau de précision largement suffisant pour un usage médical. La différence de précision de 3% avec EasyOCR est minime comparée au gain en efficacité opérationnelle.

Notre recommandation finale est donc claire : nous avons adopté :blue:`Doctr` pour la numérisation de nos analyses sanguines. Il représente le meilleur compromis entre précision et performance, permettant une numérisation efficace et fiable de nos données médicales. Pour nos laboratoires ayant des contraintes de temps strictes, Doctr est clairement la solution optimale pour le traitement de nos analyses sanguines.
