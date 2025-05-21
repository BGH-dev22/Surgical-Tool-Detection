=================================================
Fine-Tuning du Modèle Mistral pour l'Analyse Médicale
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

:blue:`Vue d'Ensemble et Objectifs`
--------------------------------
Le projet vise à optimiser le modèle Mistral-7B pour l'interprétation d'analyses médicales en français. Cette optimisation utilise une architecture Matryoshka innovante et le framework unsloth pour un fine-tuning accéléré.

:green:`Configuration Technique`
---------------------------
**Infrastructure Requise**

* GPU: Tesla T4
* RAM: 16GB minimum
* Python: 3.8+
* Framework: unsloth

**Bibliothèques Principales**

.. code-block:: python

    import torch
    from unsloth import FastLanguageModel
    from datasets import load_dataset
    from transformers import TrainingArguments
    from trl import SFTTrainer
    import evaluate

:blue:`Architecture et Implémentation`
---------------------------------

Configuration du Modèle
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/mistral-7b-v0.3",
        max_seq_length=2048,
        load_in_4bit=True
    )

Configuration LoRA
~~~~~~~~~~~~~~~~
.. code-block:: python

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_alpha=16,
        lora_dropout=0,
        bias="none"
    )

:orange:`Préparation des Données`
----------------------------

Template de Prompt
~~~~~~~~~~~~~~~~
.. code-block:: python

    alpaca_prompt = """Vous êtes un médecin professionnel spécialisé dans l'analyse des résultats de laboratoire médical pour évaluer la santé des patients. Examinez les valeurs de test fournies, comparez-les aux plages de référence normales, et déterminez si elles sont normales ou anormales. Fournissez une évaluation diagnostique basée sur les anomalies. Priorisez toujours la précision et le professionnalisme dans votre réponse.

    ### Instruction:
    {}

    ### Input:
    {}

    ### Response:
    {}"""

Dataset
~~~~~~~
* Source: MedAnalyzer
* Taille: 2,182 paires Q/R
* Format: JSON
* Langue: Français

:green:`Processus de Fine-Tuning`
----------------------------

Configuration d'Entraînement
~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            num_train_epochs=1,
            learning_rate=2e-4,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=1,
            optim="adamw_8bit"
        )
    )

Paramètres Optimaux
~~~~~~~~~~~~~~~~
* Batch Size: 2
* Accumulation Gradient: 4
* Learning Rate: 2e-4
* Epochs: 1
* Warmup Steps: 5

:blue:`Évaluation et Métriques`
---------------------------

Méthodologie d'Évaluation
~~~~~~~~~~~~~~~~~~~~~~
* Métrique: BLEU Score
* Échantillon: 100 exemples
* Comparaison avant/après fine-tuning

:green:`Résultats Pré-Fine-Tuning`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Score BLEU: 0.0009
* Précisions n-grammes:
    - 1-gramme: 0.97%
    - 2-grammes: 0.08%
    - 3-grammes: 0.06%
    - 4-grammes: 0.04%
* Brevity Penalty: 0.73

:green:`Résultats Post-Fine-Tuning`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Score BLEU: 0.0511 (×50)
* Précisions n-grammes:
    - 1-gramme: 21.05%
    - 2-grammes: 6.39%
    - 3-grammes: 3.09%
    - 4-grammes: 1.63%
* Brevity Penalty: 1.0
* Ratio Longueur: 1.33

:red:`Limitations et Points d'Attention`
----------------------------------
1. Scores n-grammes élevés encore insuffisants
2. Besoin d'optimisation continue
3. Dépendance matérielle importante

:orange:`Perspectives d'Amélioration`
--------------------------------
1. Augmentation du dataset
2. Optimisation des hyperparamètres
3. Exploration architectures alternatives
4. Implémentation curriculum learning
5. Enrichissement données médicales

:blue:`Guide d'Utilisation`
----------------------
Pour utiliser le modèle fine-tuné:

.. code-block:: python

    model = FastLanguageModel.from_pretrained(
        "chemin/vers/modele_finetuned",
        device="cuda",
        load_in_4bit=True
    )

    # Exemple d'inférence
    response = model.generate(
        tokenizer.encode(prompt, return_tensors="pt"),
        max_new_tokens=512
    )

:green:`Conclusion`
--------------
Le fine-tuning a significativement amélioré les capacités d'analyse médicale du modèle, avec une augmentation notable des scores BLEU et des précisions n-grammes. Les résultats démontrent l'efficacité de l'approche tout en identifiant des axes d'amélioration futurs.
