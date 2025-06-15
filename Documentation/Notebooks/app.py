import streamlit as st
import cv2
from ultralytics import YOLO
import time
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
import os
import torch
import tempfile
import logging
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="SurgiSafe Pro - Advanced Surgical Instrument Tracking",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .video-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 500px;
        margin-bottom: 20px;
        border: 3px solid #e0e0e0;
        border-radius: 15px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        box-shadow: inset 0 4px 8px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .alert-critical {
        background-color: #fee;
        border-left: 4px solid #f56565;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .alert-danger {
        background-color: #fef5e7;
        border-left: 4px solid #ed8936;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .alert-warning {
        background-color: #fffbf0;
        border-left: 4px solid #ecc94b;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .instrument-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active { background-color: #48bb78; }
    .status-warning { background-color: #ecc94b; }
    .status-danger { background-color: #ed8936; }
    .status-critical { background-color: #f56565; }
    .status-lost { background-color: #a0aec0; }
    .confirmation-button {
        background-color: #48bb78;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
    }
    .confirmation-button:hover {
        background-color: #38a169;
    }
</style>
""", unsafe_allow_html=True)

class SurgiSafeStateManager:
    def __init__(self):
        self.detected_instruments = {}
        self.alerts_queue = deque(maxlen=100)  # Increased capacity
        self.model_info = {}
        self.tracking_stats = defaultdict(int)
        self.processed_frames = 0
        self.fps_counter = deque(maxlen=30)
        self.system_status = 'idle'
        self.last_frame = None
        self.bbox_history = defaultdict(lambda: deque(maxlen=5))
        self.pending_confirmations = {}  # For storing instruments awaiting confirmation
        
        # Enhanced tracking
        self.session_start_time = datetime.now()
        self.performance_metrics = defaultdict(list)
        self.detection_history = deque(maxlen=1000)  # Store detection history
        self.alert_history = []
        self.export_data = []

class InstrumentInfo:
    def __init__(self, instrument_id, name, bbox, confidence, track_id):
        self.id = instrument_id
        self.name = name
        self.bbox = bbox
        self.confidence = confidence
        self.track_id = track_id
        self.first_detected = datetime.now()
        self.last_seen = datetime.now()
        self.detection_count = 1
        self.status = 'active'
        self.risk_level = 'normal'
        self.confidence_history = deque([confidence], maxlen=20)
        self.position_history = deque([bbox], maxlen=50)
        self.max_duration = 0
    
    def update_position(self, bbox, confidence):
        self.bbox = bbox
        self.confidence = confidence
        self.last_seen = datetime.now()
        self.detection_count += 1
        self.confidence_history.append(confidence)
        self.position_history.append(bbox)
    
    def get_duration_minutes(self):
        duration_minutes = (datetime.now() - self.first_detected).total_seconds() / 60
        self.max_duration = max(self.max_duration, duration_minutes)
        return duration_minutes
    
    def get_average_confidence(self):
        return np.mean(list(self.confidence_history)) if self.confidence_history else 0
    
    def get_movement_distance(self):
        if len(self.position_history) < 2:
            return 0
        distances = []
        for i in range(1, len(self.position_history)):
            prev_center = self._get_bbox_center(self.position_history[i-1])
            curr_center = self._get_bbox_center(self.position_history[i])
            distance = np.sqrt((curr_center[0] - prev_center[0])**2 + (curr_center[1] - prev_center[1])**2)
            distances.append(distance)
        return np.sum(distances) if distances else 0
    
    def _get_bbox_center(self, bbox):
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    
    def update_risk_level(self):
        duration = self.get_duration_minutes()
        if duration > 30:
            self.risk_level = 'critical'
        elif duration > 20:
            self.risk_level = 'danger'
        elif duration > 10:
            self.risk_level = 'warning'
        else:
            self.risk_level = 'normal'
    
    def to_dict(self):
        """Convert instrument info to dictionary for export"""
        return {
            'id': self.id,
            'name': self.name,
            'track_id': self.track_id,
            'first_detected': self.first_detected.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'duration_minutes': self.get_duration_minutes(),
            'max_duration': self.max_duration,
            'detection_count': self.detection_count,
            'status': self.status,
            'risk_level': self.risk_level,
            'average_confidence': self.get_average_confidence(),
            'movement_distance': self.get_movement_distance(),
            'final_bbox': self.bbox
        }

class AlertManager:
    def __init__(self):
        self.alert_thresholds = {
            'warning': 10, 
            'danger': 20, 
            'critical': 30,
            'extended': 45  # New threshold for extended procedures
        }
        self.sent_alerts = set()
        self.alert_sounds = {
            'warning': '🔔',
            'danger': '⚠️',
            'critical': '🚨',
            'extended': '💀'
        }
    
    def check_and_generate_alerts(self, instruments):
        current_time = datetime.now()
        new_alerts = []
        
        for instrument in instruments.values():
            duration = instrument.get_duration_minutes()
            instrument_key = f"{instrument.id}_{instrument.track_id}"
            
            # Check for extended duration alert
            if duration > self.alert_thresholds['extended'] and f"extended_{instrument_key}" not in self.sent_alerts:
                new_alerts.append({
                    'timestamp': current_time, 
                    'level': 'extended', 
                    'message': f"EXTENDED: {instrument.name} (ID:{instrument.track_id}) > 45min - Review required",
                    'instrument_id': instrument_key,
                    'duration': duration
                })
                self.sent_alerts.add(f"extended_{instrument_key}")
            
            elif duration > self.alert_thresholds['critical'] and f"critical_{instrument_key}" not in self.sent_alerts:
                new_alerts.append({
                    'timestamp': current_time, 
                    'level': 'critical', 
                    'message': f"CRITICAL: {instrument.name} (ID:{instrument.track_id}) > 30min",
                    'instrument_id': instrument_key,
                    'duration': duration
                })
                self.sent_alerts.add(f"critical_{instrument_key}")
            
            elif duration > self.alert_thresholds['danger'] and f"danger_{instrument_key}" not in self.sent_alerts:
                new_alerts.append({
                    'timestamp': current_time, 
                    'level': 'danger', 
                    'message': f"DANGER: {instrument.name} (ID:{instrument.track_id}) > 20min",
                    'instrument_id': instrument_key,
                    'duration': duration
                })
                self.sent_alerts.add(f"danger_{instrument_key}")
            
            elif duration > self.alert_thresholds['warning'] and f"warning_{instrument_key}" not in self.sent_alerts:
                new_alerts.append({
                    'timestamp': current_time, 
                    'level': 'warning', 
                    'message': f"WARNING: {instrument.name} (ID:{instrument.track_id}) > 10min",
                    'instrument_id': instrument_key,
                    'duration': duration
                })
                self.sent_alerts.add(f"warning_{instrument_key}")
        
        return new_alerts
    
    def clear_alerts_for_instrument(self, instrument_key):
        """Clear all alerts for a specific instrument when it's removed"""
        alerts_to_remove = [alert for alert in self.sent_alerts if instrument_key in alert]
        for alert in alerts_to_remove:
            self.sent_alerts.discard(alert)

class YOLOModelManager:
    def __init__(self):
        self.model = None
        self.class_names = {
            0: "Right_Prograsp_Forceps_labels",
            1: "Other_labels",
            2: "Maryland_Bipolar_Forceps_labels",
            3: "Left_Prograsp_Forceps_labels",
            4: "Right_Large_Needle_Driver_labels",
            5: "Left_Large_Needle_Driver_labels",
            6: "Prograsp_Forceps_labels"
        }
        self.class_id_map = {
            "Right_Prograsp_Forceps_labels": 1,
            "Other_labels": 2,
            "Maryland_Bipolar_Forceps_labels": 3,
            "Left_Prograsp_Forceps_labels": 4,
            "Right_Large_Needle_Driver_labels": 5,
            "Left_Large_Needle_Driver_labels": 6,
            "Prograsp_Forceps_labels": 7
        }
        self.model_info = {}
        self.model_performance = defaultdict(list)
    
    def load_model(self, model_path):
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found: {model_path}")
            
            start_time = time.time()
            self.model = YOLO(model_path)
            load_time = time.time() - start_time
            
            self.model_info = {
                'path': model_path,
                'classes': self.class_names,
                'num_classes': len(self.class_names),
                'device': 'cuda' if torch.cuda.is_available() else 'cpu',
                'load_time': load_time,
                'model_size': os.path.getsize(model_path) / (1024 * 1024)  # MB
            }
            
            logger.info(f"Model loaded successfully: {self.model_info}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def predict_and_track(self, frame, conf_threshold=0.3, iou_threshold=0.4):
        if self.model is None:
            logger.error("No model loaded")
            return []
        
        try:
            start_time = time.time()
            
            # Use YOLOv8 tracking method
            results = self.model.track(frame, conf=conf_threshold, iou=iou_threshold, persist=True, verbose=False)
            tracks = []
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                if boxes.id is not None:  # Check if tracking IDs are available
                    track_ids = boxes.id
                    for box, track_id in zip(boxes, track_ids):
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        if class_id in self.class_names:
                            class_name = self.class_names[class_id]
                            fixed_track_id = self.class_id_map[class_name]
                            tracks.append({
                                'track_id': fixed_track_id,
                                'bbox': [x1, y1, x2, y2],
                                'class_name': class_name,
                                'confidence': confidence
                            })
            
            # Record performance metrics
            inference_time = time.time() - start_time
            self.model_performance['inference_times'].append(inference_time)
            self.model_performance['detections_per_frame'].append(len(tracks))
            
            # Keep only last 100 measurements
            if len(self.model_performance['inference_times']) > 100:
                self.model_performance['inference_times'].pop(0)
                self.model_performance['detections_per_frame'].pop(0)
            
            return tracks
            
        except Exception as e:
            logger.error(f"YOLOv8 Tracking Error: {str(e)}")
            return []

class SurgiSafeCore:
    def __init__(self):
        self.model_manager = YOLOModelManager()
        self.alert_manager = AlertManager()
    
    def process_frame(self, frame, conf_threshold=0.3, iou_threshold=0.4):
        try:
            start_time = time.time()
            
            # Get tracks from model
            tracks = self.model_manager.predict_and_track(frame, conf_threshold, iou_threshold)
            
            # Update instrument tracking
            self._update_detected_instruments(tracks)
            self._update_risk_levels()
            
            # Generate alerts
            new_alerts = self.alert_manager.check_and_generate_alerts(
                st.session_state.state_manager.detected_instruments
            )
            
            # Add alerts to queue and history
            for alert in new_alerts:
                st.session_state.state_manager.alerts_queue.append(alert)
                st.session_state.state_manager.alert_history.append(alert)
            
            # Update statistics
            self._update_stats(tracks)
            
            # Calculate FPS
            processing_time = time.time() - start_time
            if processing_time > 0:
                st.session_state.state_manager.fps_counter.append(1.0 / processing_time)
            
            # Store detection data for export
            detection_data = {
                'timestamp': datetime.now().isoformat(),
                'frame_number': st.session_state.state_manager.processed_frames,
                'detections': len(tracks),
                'processing_time': processing_time,
                'tracks': tracks
            }
            st.session_state.state_manager.detection_history.append(detection_data)
            
            # Annotate frame
            annotated_frame = self._annotate_frame(frame, tracks)
            
            return annotated_frame
            
        except Exception as e:
            logger.error(f"Frame processing error: {str(e)}")
            return frame
    
    def _update_detected_instruments(self, tracks):
        current_time = datetime.now()
        active_ids = set()
        
        for track in tracks:
            instrument_id = f"{track['class_name']}_{track['track_id']}"
            active_ids.add(instrument_id)
            
            if instrument_id in st.session_state.state_manager.detected_instruments:
                # Update existing instrument
                instrument = st.session_state.state_manager.detected_instruments[instrument_id]
                bbox_history = st.session_state.state_manager.bbox_history[instrument_id]
                bbox_history.append(track['bbox'])
                
                # Calculate averaged bbox for smoother tracking
                avg_bbox = [
                    int(sum(b[i] for b in bbox_history) / len(bbox_history))
                    for i in range(4)
                ]
                instrument.update_position(avg_bbox, track['confidence'])
            else:
                # Create new instrument
                instrument = InstrumentInfo(
                    instrument_id=instrument_id,
                    name=track['class_name'],
                    bbox=track['bbox'],
                    confidence=track['confidence'],
                    track_id=track['track_id']
                )
                st.session_state.state_manager.detected_instruments[instrument_id] = instrument
                st.session_state.state_manager.bbox_history[instrument_id].append(track['bbox'])
        
        # Mark instruments as lost if not seen for too long, with confirmation for critical cases
        for instrument_id, instrument in list(st.session_state.state_manager.detected_instruments.items()):
            if instrument_id not in active_ids:
                time_since_last_seen = (current_time - instrument.last_seen).total_seconds()
                if time_since_last_seen > 5:  # 5 seconds threshold
                    if instrument.risk_level == 'critical' and instrument_id not in st.session_state.state_manager.pending_confirmations:
                        st.session_state.state_manager.pending_confirmations[instrument_id] = instrument
                        instrument.status = 'pending'
                    elif instrument_id not in st.session_state.state_manager.pending_confirmations:
                        instrument.status = 'lost'
                        self.alert_manager.clear_alerts_for_instrument(instrument_id)
    
    def _update_risk_levels(self):
        for instrument in st.session_state.state_manager.detected_instruments.values():
            if instrument.status == 'active':
                instrument.update_risk_level()
    
    def _update_stats(self, tracks):
        st.session_state.state_manager.tracking_stats['total_detections'] += len(tracks)
        st.session_state.state_manager.tracking_stats['active_tracks'] = len(tracks)
        st.session_state.state_manager.processed_frames += 1
        
        # Update performance metrics
        current_time = datetime.now()
        st.session_state.state_manager.performance_metrics['timestamps'].append(current_time)
        st.session_state.state_manager.performance_metrics['detections'].append(len(tracks))
        
        # Keep only last 1000 measurements
        if len(st.session_state.state_manager.performance_metrics['timestamps']) > 1000:
            st.session_state.state_manager.performance_metrics['timestamps'].pop(0)
            st.session_state.state_manager.performance_metrics['detections'].pop(0)
    
    def _annotate_frame(self, frame, tracks):
        annotated_frame = frame.copy()
        colors = {
            'normal': (0, 255, 0),      # Green
            'warning': (0, 255, 255),   # Yellow
            'danger': (0, 165, 255),    # Orange
            'critical': (0, 0, 255),    # Red
            'extended': (128, 0, 128),  # Purple
            'lost': (128, 128, 128),    # Gray
            'pending': (255, 165, 0)    # Orange for pending confirmation
        }
        
        for track in tracks:
            instrument_id = f"{track['class_name']}_{track['track_id']}"
            if instrument_id in st.session_state.state_manager.detected_instruments:
                instrument = st.session_state.state_manager.detected_instruments[instrument_id]
                color = colors.get(instrument.risk_level if instrument.status != 'pending' else 'pending', (255, 255, 255))
                
                x1, y1, x2, y2 = instrument.bbox
                
                # Draw bounding box with thickness based on risk level
                thickness = 3 if instrument.risk_level in ['critical', 'extended'] else 2
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
                
                # Prepare labels
                duration = instrument.get_duration_minutes()
                confidence = instrument.get_average_confidence()
                
                # Main label
                label = f"{instrument.name.replace('_labels', '')} (ID:{instrument.track_id})"
                status_text = f"{duration:.1f}min | {confidence:.2f} ({instrument.risk_level.upper() if instrument.status != 'pending' else 'PENDING'})"
                
                # Draw labels with background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                status_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                
                # Draw background rectangles
                cv2.rectangle(annotated_frame, (x1, y1 - 35), (x1 + max(label_size[0], status_size[0]) + 10, y1), color, -1)
                
                # Draw text
                cv2.putText(annotated_frame, label, (x1 + 5, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(annotated_frame, status_text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add system information overlay
        self._add_system_overlay(annotated_frame)
        
        return annotated_frame
    
    def _add_system_overlay(self, frame):
        """Add system information overlay to the frame"""
        # System stats
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        fps = np.mean(list(st.session_state.state_manager.fps_counter)) if st.session_state.state_manager.fps_counter else 0
        active_instruments = len([i for i in st.session_state.state_manager.detected_instruments.values() if i.status == 'active'])
        
        # Session duration
        session_duration = datetime.now() - st.session_state.state_manager.session_start_time
        session_minutes = int(session_duration.total_seconds() / 60)
        
        # Overlay background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # System information
        info_lines = [
            f"Time: {timestamp}",
            f"FPS: {fps:.1f} | Frame: {st.session_state.state_manager.processed_frames}",
            f"Active Instruments: {active_instruments}",
            f"Session Duration: {session_minutes}min"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (15, 30 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (102, 126, 234), 1)

# Initialize session state
def initialize_session_state():
    try:
        if 'state_manager' not in st.session_state:
            st.session_state.state_manager = SurgiSafeStateManager()
        if 'surgisafe_core' not in st.session_state:
            st.session_state.surgisafe_core = SurgiSafeCore()
        if 'is_running' not in st.session_state:
            st.session_state.is_running = False
        if 'video_source' not in st.session_state:
            st.session_state.video_source = None
        if 'cap' not in st.session_state:
            st.session_state.cap = None
        if 'conf_threshold' not in st.session_state:
            st.session_state.conf_threshold = 0.05
        if 'iou_threshold' not in st.session_state:
            st.session_state.iou_threshold = 0.2
        if 'target_width' not in st.session_state:
            st.session_state.target_width = 640
        if 'auto_export' not in st.session_state:
            st.session_state.auto_export = False
        if 'alert_sound' not in st.session_state:
            st.session_state.alert_sound = True
        if 'show_confidence' not in st.session_state:
            st.session_state.show_confidence = True
            
    except Exception as e:
        logger.error(f"Error initializing session state: {str(e)}")
        st.error(f"Error initializing session state: {str(e)}")

def create_performance_dashboard():
    """Create enhanced performance dashboard"""
    st.subheader("📊 Performance Dashboard")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Real-time Stats", "🔍 Instrument Analysis", "⚠️ Alert History", "📋 Export Data"])
    
    with tab1:
        # Real-time metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            active_instruments = len([i for i in st.session_state.state_manager.detected_instruments.values() if i.status == 'active'])
            st.markdown(f"""
            <div class="stat-card">
                <h3>🔧 Active Instruments</h3>
                <h2 style="color: #667eea;">{active_instruments}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            fps = np.mean(list(st.session_state.state_manager.fps_counter)) if st.session_state.state_manager.fps_counter else 0
            st.markdown(f"""
            <div class="stat-card">
                <h3>⚡ FPS</h3>
                <h2 style="color: #667eea;">{fps:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_alerts = len(st.session_state.state_manager.alert_history)
            st.markdown(f"""
            <div class="stat-card">
                <h3>🚨 Total Alerts</h3>
                <h2 style="color: #667eea;">{total_alerts}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            session_duration = datetime.now() - st.session_state.state_manager.session_start_time
            session_minutes = int(session_duration.total_seconds() / 60)
            st.markdown(f"""
            <div class="stat-card">
                <h3>⏱️ Session Duration</h3>
                <h2 style="color: #667eea;">{session_minutes}min</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance chart
        if st.session_state.state_manager.performance_metrics['timestamps']:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=st.session_state.state_manager.performance_metrics['timestamps'],
                y=st.session_state.state_manager.performance_metrics['detections'],
                mode='lines+markers',
                name='Detections per Frame',
                line=dict(color='#667eea')
            ))
            fig.update_layout(
                title="Detection Performance Over Time",
                xaxis_title="Time",
                yaxis_title="Number of Detections",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Instrument analysis
        if st.session_state.state_manager.detected_instruments:
            instruments_data = []
            for instrument in st.session_state.state_manager.detected_instruments.values():
                instruments_data.append({
                    'Name': instrument.name.replace('_labels', ''),
                    'Track ID': instrument.track_id,
                    'Duration (min)': f"{instrument.get_duration_minutes():.1f}",
                    'Status': instrument.status,
                    'Risk Level': instrument.risk_level,
                    'Confidence': f"{instrument.get_average_confidence():.2f}",
                    'Detections': instrument.detection_count,
                    'Movement': f"{instrument.get_movement_distance():.0f}px"
                })
            
            df = pd.DataFrame(instruments_data)
            st.dataframe(df, use_container_width=True)
            
            # Risk level distribution
            risk_counts = df['Risk Level'].value_counts()
            fig_pie = px.pie(
                values=risk_counts.values, 
                names=risk_counts.index,
                title="Risk Level Distribution",
                color_discrete_map={
                    'normal': '#48bb78',
                    'warning': '#ecc94b',
                    'danger': '#ed8936',
                    'critical': '#f56565'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No instruments detected yet.")
    
    with tab3:
        # Alert history
        if st.session_state.state_manager.alert_history:
            st.subheader("Recent Alerts")
            
            # Show recent alerts with confirmation for critical lost instruments
            recent_alerts = list(st.session_state.state_manager.alerts_queue)[-10:]
            for alert in reversed(recent_alerts):
                alert_class = f"alert-{alert['level']}"
                timestamp_str = alert['timestamp'].strftime("%H:%M:%S")
                if alert['level'] == 'critical' and alert['instrument_id'] in st.session_state.state_manager.pending_confirmations:
                    instrument = st.session_state.state_manager.pending_confirmations[alert['instrument_id']]
                    if st.button(f"✅ Confirm Loss for {instrument.name} (ID:{instrument.track_id})", key=f"confirm_{alert['instrument_id']}"):
                        instrument.status = 'lost'
                        del st.session_state.state_manager.pending_confirmations[alert['instrument_id']]
                        self.alert_manager.clear_alerts_for_instrument(alert['instrument_id'])
                        st.success(f"Confirmed loss for {instrument.name} (ID:{instrument.track_id})")
                st.markdown(f"""
                <div class="{alert_class}">
                    <strong>{timestamp_str}</strong> - {alert['message']}
                </div>
                """, unsafe_allow_html=True)
            
            # Alert statistics
            if len(st.session_state.state_manager.alert_history) > 0:
                alert_df = pd.DataFrame(st.session_state.state_manager.alert_history)
                alert_counts = alert_df['level'].value_counts()
                
                fig_bar = px.bar(
                    x=alert_counts.index,
                    y=alert_counts.values,
                    title="Alert Type Distribution",
                    color=alert_counts.index,
                    color_discrete_map={
                        'warning': '#ecc94b',
                        'danger': '#ed8936',
                        'critical': '#f56565',
                        'extended': '#805ad5'
                    }
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No alerts generated yet.")
    
    with tab4:
        # Export data
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Instrument Data"):
                if st.session_state.state_manager.detected_instruments:
                    export_data = []
                    for instrument in st.session_state.state_manager.detected_instruments.values():
                        export_data.append(instrument.to_dict())
                    
                    df_export = pd.DataFrame(export_data)
                    csv = df_export.to_csv(index=False)
                    
                    st.download_button(
                        label="⬇️ Download Instrument Data (CSV)",
                        data=csv,
                        file_name=f"instrument_data_{int(datetime.now().timestamp())}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No instrument data to export.")
        
        with col2:
            if st.button("📋 Export Alert History"):
                if st.session_state.state_manager.alert_history:
                    alert_export = []
                    for alert in st.session_state.state_manager.alert_history:
                        alert_export.append({
                            'timestamp': alert['timestamp'].isoformat(),
                            'level': alert['level'],
                            'message': alert['message'],
                            'instrument_id': alert.get('instrument_id', ''),
                            'duration': alert.get('duration', 0)
                        })
                    
                    df_alerts = pd.DataFrame(alert_export)
                    csv_alerts = df_alerts.to_csv(index=False)
                    
                    st.download_button(
                        label="⬇️ Download Alert History (CSV)",
                        data=csv_alerts,
                        file_name=f"alert_history_{int(datetime.now().timestamp())}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No alert history to export.")
        
        # Detection history export
        if st.button("📈 Export Detection History"):
            if st.session_state.state_manager.detection_history:
                detection_export = []
                for detection in st.session_state.state_manager.detection_history:
                    detection_export.append({
                        'timestamp': detection['timestamp'],
                        'frame_number': detection['frame_number'],
                        'detections_count': detection['detections'],
                        'processing_time': detection['processing_time']
                    })
                
                df_detections = pd.DataFrame(detection_export)
                csv_detections = df_detections.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download Detection History (CSV)",
                    data=csv_detections,
                    file_name=f"detection_history_{int(datetime.now().timestamp())}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No detection history to export.")

def display_active_instruments():
    """Display active instruments in an enhanced format"""
    st.subheader("🔧 Active Instruments")
    
    active_instruments = [i for i in st.session_state.state_manager.detected_instruments.values() if i.status == 'active']
    
    if not active_instruments:
        st.info("No active instruments detected.")
        return
    
    for instrument in active_instruments:
        duration = instrument.get_duration_minutes()
        confidence = instrument.get_average_confidence()
        
        # Status indicator
        status_class = f"status-{instrument.risk_level}"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="instrument-card">
                <h4>
                    <span class="status-indicator {status_class}"></span>
                    {instrument.name.replace('_labels', '')} (Track ID: {instrument.track_id})
                </h4>
                <p><strong>Duration:</strong> {duration:.1f} minutes</p>
                <p><strong>Confidence:</strong> {confidence:.2f}</p>
                <p><strong>Risk Level:</strong> {instrument.risk_level.upper()}</p>
                <p><strong>Detections:</strong> {instrument.detection_count}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Mini chart for confidence over time
            if len(instrument.confidence_history) > 1:
                fig_mini = go.Figure()
                fig_mini.add_trace(go.Scatter(
                    y=list(instrument.confidence_history),
                    mode='lines',
                    name='Confidence',
                    line=dict(color='#667eea', width=2)
                ))
                fig_mini.update_layout(
                    height=100,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=False, range=[0, 1])
                )
                st.plotly_chart(fig_mini, use_container_width=True)

def generate_comprehensive_report():
    """Generate a comprehensive report with all tracking data"""
    report_data = {
        'session_info': {
            'start_time': st.session_state.state_manager.session_start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_minutes': (datetime.now() - st.session_state.state_manager.session_start_time).total_seconds() / 60,
            'total_frames': st.session_state.state_manager.processed_frames,
            'model_info': st.session_state.state_manager.model_info
        },
        'instruments': [instrument.to_dict() for instrument in st.session_state.state_manager.detected_instruments.values()],
        'alerts': [
            {
                'timestamp': alert['timestamp'].isoformat(),
                'level': alert['level'],
                'message': alert['message'],
                'instrument_id': alert.get('instrument_id', ''),
                'duration': alert.get('duration', 0)
            }
            for alert in st.session_state.state_manager.alert_history
        ],
        'statistics': dict(st.session_state.state_manager.tracking_stats)
    }
    
    return json.dumps(report_data, indent=2)

def process_video(video_placeholder):
    """Enhanced video processing with better error handling and performance monitoring"""
    try:
        if st.session_state.cap is None:
            st.session_state.cap = cv2.VideoCapture(st.session_state.video_source)
            if not st.session_state.cap.isOpened():
                logger.error(f"Failed to open video source: {st.session_state.video_source}")
                st.error(f"Failed to open video source: {st.session_state.video_source}")
                st.session_state.is_running = False
                return
            
            logger.info(f"Video loaded: {st.session_state.video_source}")
        
        # Get video properties
        total_frames = int(st.session_state.cap.get(cv2.CAP_PROP_FRAME_COUNT)) if st.session_state.video_source != 0 else -1
        fps = st.session_state.cap.get(cv2.CAP_PROP_FPS) if st.session_state.video_source != 0 else 30
        
        logger.info(f"Video properties - Total frames: {total_frames}, FPS: {fps}")
        
        # Processing loop
        frame_skip = 1  # Process every frame by default
        frame_count = 0
        
        while st.session_state.is_running:
            ret, frame = st.session_state.cap.read()
            if not ret:
                logger.info(f"End of video or read error at frame {frame_count}")
                st.session_state.is_running = False
                break
            
            frame_count += 1
            
            # Skip frames if needed for performance
            if frame_count % frame_skip != 0:
                continue
            
            # Resize frame with aspect ratio preservation
            original_height, original_width = frame.shape[:2]
            target_width = st.session_state.get('target_width', 640)
            target_height = int(original_height * (target_width / original_width))
            frame = cv2.resize(frame, (target_width, target_height))
            
            # Process frame
            annotated_frame = st.session_state.surgisafe_core.process_frame(
                frame, st.session_state.conf_threshold, st.session_state.iou_threshold
            )
            
            # Convert to RGB for display
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            st.session_state.state_manager.last_frame = annotated_frame_rgb
            
            # Update display
            video_placeholder.image(annotated_frame_rgb, channels="RGB", use_container_width=True)
            
            # Adaptive frame rate control
            current_fps = np.mean(list(st.session_state.state_manager.fps_counter)) if st.session_state.state_manager.fps_counter else 0
            if current_fps < 10:  # If FPS is too low, start skipping frames
                frame_skip = min(frame_skip + 1, 3)
            elif current_fps > 20:  # If FPS is good, reduce frame skipping
                frame_skip = max(frame_skip - 1, 1)
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.03)  # ~30 FPS max
    
    except Exception as e:
        logger.error(f"Video processing error: {str(e)}")
        st.error(f"Video processing error: {str(e)}")
        st.session_state.is_running = False
    
    finally:
        if st.session_state.cap:
            st.session_state.cap.release()
            st.session_state.cap = None

def main():
    initialize_session_state()
    
    # Enhanced Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 SurgiSafe Pro</h1>
        <p>Advanced Intelligent Surgical Instrument Tracking & Safety System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main layout
    main_col1, main_col2 = st.columns([3, 1])
    
    with main_col1:
        # Video Display Section
        st.subheader("📺 Live Analysis")
        video_container = st.container()
        with video_container:
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            video_placeholder = st.empty()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Progress bar for video processing
        progress_placeholder = st.empty()
        
        # Video processing
        if st.session_state.is_running and st.session_state.video_source is not None:
            process_video(video_placeholder)
            
            # Update progress for video files
            if st.session_state.video_source != 0 and st.session_state.cap:
                total_frames = int(st.session_state.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if total_frames > 0:
                    progress = min(st.session_state.state_manager.processed_frames / total_frames, 1.0)
                    progress_placeholder.progress(
                        progress, 
                        f"Progress: {st.session_state.state_manager.processed_frames}/{total_frames} frames ({progress*100:.1f}%)"
                    )
        else:
            video_placeholder.info("🎬 Ready to analyze. Load a model, select video source, and start analysis.")
    
    with main_col2:
        # Real-time Statistics Panel
        st.subheader("📊 Live Statistics")
        
        # System Status
        status_color = {
            'idle': '🟡',
            'running': '🟢',
            'stopped': '🔴',
            'error': '🔴'
        }
        status = st.session_state.state_manager.system_status
        st.markdown(f"**Status:** {status_color.get(status, '⚪')} {status.upper()}")
        
        # Key Metrics
        active_instruments = len([i for i in st.session_state.state_manager.detected_instruments.values() if i.status == 'active'])
        fps = np.mean(list(st.session_state.state_manager.fps_counter)) if st.session_state.state_manager.fps_counter else 0
        total_alerts = len(st.session_state.state_manager.alert_history)
        
        st.metric("Active Instruments", active_instruments)
        st.metric("FPS", f"{fps:.1f}")
        st.metric("Total Alerts", total_alerts)
        
        # Recent Alerts
        st.subheader("🚨 Recent Alerts")
        recent_alerts = list(st.session_state.state_manager.alerts_queue)[-5:]
        if recent_alerts:
            for alert in reversed(recent_alerts):
                alert_emoji = {'warning': '⚠️', 'danger': '🔶', 'critical': '🚨', 'extended': '💀'}
                st.write(f"{alert_emoji.get(alert['level'], '📢')} {alert['message']}")
        else:
            st.info("No alerts yet")
        
        # Active Instruments Summary
        display_active_instruments()
    
    # Enhanced Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ System Configuration")
        
        # Model Configuration Section
        st.subheader("🤖 AI Model")
        model_path = st.text_input(
            "Model Path", 
            value="C:/Users/Hp/runs/train/exp_endovis_i5/weights/best.pt",
            help="Path to your trained YOLO model file (.pt)"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Load Model", type="primary"):
                with st.spinner("Loading AI model..."):
                    result = st.session_state.surgisafe_core.model_manager.load_model(model_path)
                    if result:
                        st.session_state.state_manager.model_info = st.session_state.surgisafe_core.model_manager.model_info
                        st.success(f"✅ Model loaded successfully!")
                        st.info(f"Classes: {st.session_state.state_manager.model_info['num_classes']}")
                        st.info(f"Device: {st.session_state.state_manager.model_info['device']}")
                    else:
                        st.error("❌ Failed to load model")
        
        with col2:
            if st.session_state.state_manager.model_info:
                st.success("✅ Ready")
            else:
                st.error("❌ No Model")
        
        st.divider()
        
        # Video Source Configuration
        st.subheader("📹 Video Input")
        
        # File upload option
        uploaded_file = st.file_uploader(
            "Upload Video File", 
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Supported formats: MP4, AVI, MOV, MKV"
        )
        
        if uploaded_file:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    st.session_state.video_source = tmp_file.name
                
                # Validate video file
                cap = cv2.VideoCapture(st.session_state.video_source)
                if not cap.isOpened():
                    raise Exception("Invalid video file")
                
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                duration = total_frames / fps if fps > 0 else 0
                
                cap.release()
                
                st.success("✅ Video loaded successfully")
                st.info(f"Duration: {duration:.1f}s | Frames: {total_frames} | FPS: {fps:.1f}")
                
            except Exception as e:
                st.error(f"❌ Error processing video: {str(e)}")
        
        st.divider()
        
        # Detection Parameters
        st.subheader("🎯 Detection Settings")
        
        st.session_state.conf_threshold = st.slider(
            "Confidence Threshold", 
            0.01, 1.0, 0.05, 0.01,
            help="Minimum confidence for detections"
        )
        
        st.session_state.iou_threshold = st.slider(
            "IoU Threshold", 
            0.1, 1.0, 0.2, 0.05,
            help="Intersection over Union threshold for NMS"
        )
        
        st.divider()
        
        # Video Processing Settings
        st.subheader("📏 Processing Settings")
        
        st.session_state.target_width = st.slider(
            "Video Width", 
            320, 1280, 640, 32,
            help="Target width for processing (affects performance)"
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            st.session_state.alert_sound = st.checkbox("Enable Alert Sounds", value=True)
            st.session_state.show_confidence = st.checkbox("Show Confidence Values", value=True)
            st.session_state.auto_export = st.checkbox("Auto-export data on session end", value=False)
            
            # Alert thresholds customization
            st.write("**Alert Thresholds (minutes):**")
            warning_threshold = st.number_input("Warning", min_value=1, max_value=60, value=10)
            danger_threshold = st.number_input("Danger", min_value=1, max_value=60, value=20)
            critical_threshold = st.number_input("Critical", min_value=1, max_value=60, value=30)
            
            # Update thresholds in alert manager
            if hasattr(st.session_state.surgisafe_core, 'alert_manager'):
                st.session_state.surgisafe_core.alert_manager.alert_thresholds.update({
                    'warning': warning_threshold,
                    'danger': danger_threshold,
                    'critical': critical_threshold
                })
    
    # Enhanced Control Panel
    st.subheader("🎮 Control Panel")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ Start Analysis", disabled=st.session_state.is_running, type="primary"):
            if not st.session_state.state_manager.model_info:
                st.error("❌ Please load a model first")
            elif st.session_state.video_source is None:
                st.error("❌ Please select a video source")
            else:
                st.session_state.is_running = True
                st.session_state.state_manager.system_status = 'running'
                st.success("✅ Analysis started successfully!")
                st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Analysis", disabled=not st.session_state.is_running):
            st.session_state.is_running = False
            st.session_state.state_manager.system_status = 'stopped'
            if st.session_state.cap:
                st.session_state.cap.release()
                st.session_state.cap = None
            st.success("✅ Analysis stopped")
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset Session"):
            # Reset all session data
            for key in list(st.session_state.keys()):
                if key != 'surgisafe_core' or key != 'state_manager':
                    del st.session_state[key]
            st.session_state.state_manager = SurgiSafeStateManager()
            st.success("✅ Session reset")
            st.rerun()
    
    with col4:
        if st.button("📊 Generate Report"):
            if st.session_state.state_manager.detected_instruments or st.session_state.state_manager.alert_history:
                report_data = generate_comprehensive_report()
                st.download_button(
                    label="⬇️ Download Full Report (JSON)",
                    data=report_data,
                    file_name=f"surgisafe_full_report_{int(datetime.now().timestamp())}.json",
                    mime="application/json"
                )
            else:
                st.warning("No data available for report generation")
    
    # Enhanced Dashboard
    if st.session_state.state_manager.processed_frames > 0:
        st.divider()
        create_performance_dashboard()

def simple_chatbot():
    st.sidebar.subheader("💬 Support Chatbot")
    user_input = st.sidebar.text_input("Posez-moi une question sur SurgiSafe Pro :")
    
    if user_input:
        responses = {
            "comment fonctionne-t-il ?": "SurgiSafe Pro détecte et suit les instruments chirurgicaux en temps réel avec YOLOv8, génère des alertes basées sur la durée, et offre des statistiques via une interface intuitive.",
            "quels instruments sont détectés ?": "Il détecte des instruments comme Right_Prograsp_Forceps, Maryland_Bipolar_Forceps, et d'autres listés dans le modèle.",
            "comment exporter les données ?": "Vous pouvez exporter les données des instruments, alertes, et historique via les boutons dans l'onglet 'Export Data'.",
            "aide": "Tapez une question spécifique ou consultez la barre latérale pour les réglages !"
        }
        response = responses.get(user_input.lower(), "Désolé, je n'ai pas compris. Essayez 'aide' pour plus d'options.")
        st.sidebar.write(f"🤖 Réponse : {response}")

if __name__ == "__main__":
    main()
    simple_chatbot()
