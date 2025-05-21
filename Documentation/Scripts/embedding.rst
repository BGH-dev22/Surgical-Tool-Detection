=======================================================
Fine-tuning des Embeddings pour l'Analyse Médicale
=======================================================

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

:green:`Objectifs et Vue d'Ensemble`
--------------------------------
Le fine-tuning des embeddings constitue une étape cruciale dans l'optimisation des applications RAG (Retrieval-Augmented Generation). Notre processus utilise le modèle :blue:`multilingual-e5-large` comme base et exploite une architecture Matryoshka innovante pour générer des embeddings de différentes dimensions.

:blue:`Configuration Technique`
--------------------------
**Environnement Requis**

L'infrastructure nécessaire comprend un GPU avec support CUDA, un minimum de 16GB de RAM, ainsi qu'une installation de Python 3.8 ou supérieur.

**Bibliothèques Essentielles**

.. code-block:: python

    import torch
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.evaluation import (
        InformationRetrievalEvaluator,
        SequentialEvaluator
    )
    from sentence_transformers.losses import (
        MatryoshkaLoss, 
        MultipleNegativesRankingLoss
    )

:blue:`Architecture et Implémentation`
---------------------------------
**Configuration des Dimensions**

.. code-block:: python

    matryoshka_dimensions = [1024, 768, 512, 256, 128, 64]

    # Configuration de la loss
    inner_train_loss = MultipleNegativesRankingLoss(model)
    train_loss = MatryoshkaLoss(
        model, 
        inner_train_loss, 
        matryoshka_dims=matryoshka_dimensions
    )

**Paramètres d'Entraînement**

.. code-block:: python

    args = SentenceTransformerTrainingArguments(
        output_dir="bge-finetuned",
        num_train_epochs=1,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=16,
        warmup_ratio=0.1,
        learning_rate=2e-5,
        lr_scheduler_type="cosine",
        optim="adamw_torch_fused",
        bf16=True
    )

:green:`Résultats et Performances`
-----------------------------
.. image:: /Documentation/Images/evaluation.png

:green:`Dimension 1024 (Haute Précision)`
Le score NDCG@10 s'est amélioré de 0.7967 à 0.8484, montrant une progression de 5.17%.

:green:`Dimension 512 (Standard)`
La performance a augmenté de 0.7897 à 0.8471, représentant une amélioration de 5.74%.

:green:`Dimension 128 (Légère)`
Une progression remarquable de 0.6081 à 0.8253, soit une augmentation de 21.72%.

:orange:`Guide d'Utilisation`
------------------------
**Intégration du Modèle**

.. code-block:: python

    # Chargement du modèle
    model = SentenceTransformer(
        'bge-finetuned',
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

    # Génération d'embeddings
    embeddings = model.encode(texts)

**Recommandations par Cas d'Usage**

:green:`Applications Critiques`
La dimension 1024 offre une performance NDCG@10 de 0.8484. Cette configuration convient parfaitement aux cas nécessitant une précision maximale dans la recherche médicale.

:blue:`Applications Standard`
La dimension 512 maintient un excellent NDCG@10 de 0.8471. Elle représente un choix optimal pour les systèmes d'information généraux.

:orange:`Applications Légères`
La dimension 128 atteint un NDCG@10 de 0.8253. Cette configuration s'adapte idéalement aux applications mobiles et aux systèmes avec ressources limitées.

:red:`Points d'Attention`
--------------------
**Surveillance Système**
Le monitoring continu de l'utilisation GPU et de la consommation mémoire s'avère essentiel. Une attention particulière doit être portée aux temps de réponse en production.

**Maintenance**
Un plan de maintenance régulier doit inclure la sauvegarde des états du modèle et la documentation des changements de performance. Les mises à jour doivent être planifiées selon l'évolution des besoins.

:green:`Conclusion`
--------------
Le fine-tuning avec architecture Matryoshka offre une flexibilité exceptionnelle pour les applications RAG. Les améliorations significatives des performances, particulièrement impressionnantes pour les dimensions réduites, démontrent l'efficacité de cette approche. La possibilité d'adapter la dimension des embeddings permet de répondre précisément aux contraintes spécifiques de chaque projet.
