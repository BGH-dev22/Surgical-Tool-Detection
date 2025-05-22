import streamlit as st
from ultralytics import YOLO
import cv2

# CSS pour la déco médicale (bleu clair, police sympa)
st.markdown("""
    <style>
    body {
        background-color: #f0f8ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .title {
        color: #005f73;
        font-weight: bold;
        font-size: 40px;
        margin-bottom: 0;
    }
    .subtitle {
        color: #0a9396;
        margin-top: 5px;
        font-size: 20px;
    }
    .footer {
        font-size: 12px;
        color: #94a1b2;
        margin-top: 50px;
        text-align: center;
    }
    .logo {
        float: right;
        width: 80px;
        margin-top: -60px;
    }
    </style>
""", unsafe_allow_html=True)

# Logo Hugging Face cliquable à droite
st.markdown("""
    <a href="https://huggingface.co" target="_blank">
        <img src="https://huggingface.co/front/assets/huggingface_logo-noshadow.svg" class="logo">
    </a>
""", unsafe_allow_html=True)

# Titre et description
st.markdown('<h1 class="title">Détection d\'outils chirurgicaux en temps réel</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Entrez un lien URL de vidéo ou flux en direct pour lancer la détection automatique.</p>', unsafe_allow_html=True)

# Input URL vidéo
video_url = st.text_input("🔗 Entrez le lien URL de la vidéo (ex: rtsp://, http://, etc)")

if st.button("▶️ Démarrer la détection") and video_url:
    st.write(f"Traitement de la vidéo depuis : {video_url}")

    model = YOLO('yolov8n.pt')
    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        st.error("🚫 Impossible d'ouvrir la vidéo à partir de cette URL")
    else:
        frame_count = 0
        progress_bar = st.progress(0)
        while cap.isOpened() and frame_count < 100:  # limite à 100 frames ici
            ret, frame = cap.read()
            if not ret:
                break
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(img_rgb)
            annotated_frame = results[0].plot()

            st.image(annotated_frame, caption=f"Frame {frame_count + 1}")

            frame_count += 1
            progress_bar.progress(frame_count / 100)

        cap.release()
        st.success("✅ Traitement terminé.")

# Pied de page
st.markdown('<div class="footer">Projet MedAnalyzer - Assistance à la chirurgie avec IA • Powered by Ultralytics YOLO & Streamlit</div>', unsafe_allow_html=True)
