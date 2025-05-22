Interface et Déploiement de l'Analyseur Chirurgical
===================================================

Vue d'ensemble
--------------

L'application de suivi chirurgical et détection d'outils est une interface web interactive développée avec Streamlit. Elle permet la détection en temps réel des instruments chirurgicaux via un modèle YOLOv8 personnalisé, offrant un retour visuel instantané et des alertes en cas d'anomalies (oubli d’outils, etc.). Cette interface vise à faciliter la surveillance des interventions et améliorer la sécurité patient.

Architecture de l'Interface
---------------------------

L'interface est organisée autour de plusieurs modules clés :

- **Module d'entrée vidéo**  
  Permet la capture et la lecture de flux vidéo en direct ou via URL (RTSP, HTTP). Ce flux est ensuite traité image par image.

- **Module de détection et suivi**  
  Intègre le modèle YOLOv8 personnalisé chargé localement pour détecter les outils chirurgicaux dans chaque frame.Ensuite un algorithme de tracking (DeepSORT)  pour suivre les objets dans le temps.


- **Système d’alerte**  
  En cas de détection d’un outil potentiellement oublié, une alerte sonore est déclenchée pour notifier l'équipe médicale.

- **Personnalisation et configuration**  
  La sidebar permet de configurer les paramètres tels que la source vidéo, la sensibilité de détection, et l’activation/désactivation des alertes.

Déploiement
-----------

L’application est déployée localement ou sur un serveur accessible via un navigateur web :

1. **Pré-requis**  
   - Python 3.11  
   - Librairies : Streamlit, Ultralytics (YOLO), OpenCV, autres dépendances listées dans ``requirements.txt``.

2. **Installation**  
   .. code-block:: bash

      pip install -r requirements.txt

3. **Lancement de l’application**  
   Depuis le terminal, exécuter :

   .. code-block:: bash

      streamlit run app.py

   où ``app.py`` est le script principal de l’interface.

4. **Accès à l’interface**  
   Ouvrir un navigateur à l’adresse ``http://localhost:8501`` pour accéder à l’application.

5. **Connexion caméra externe**  
   L’interface supporte la connexion à des caméras via URL réseau (RTSP) ou via scrcpy pour capter des flux d’une tablette Android en direct.

Exemple d'interface (capture d'écran)
-------------------------------------

.. image:: Documentation/Images/streamlit.png
   :alt: Exemple d’interface Streamlit avec détection d’outils chirurgicaux
   :align: center
   :width: 600px

Perspectives futures
-------------------

- Intégration d’un module d’analyse prédictive pour classifier la gravité de l’opération selon les outils détectés.
- Ajout d’un tableau de bord centralisé pour historique des interventions et statistiques.
- Amélioration de l’interface avec des alertes visuelles et sonores avancées et notifications push.
- Support multi-utilisateurs avec authentification et gestion des sessions.

---

Cette architecture garantit une application robuste, facile à utiliser par le personnel médical, et évolutive pour intégrer de nouvelles fonctionnalités selon les besoins cliniques.
