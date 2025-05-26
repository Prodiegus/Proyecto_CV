# Lógica modular de la cámara con detección facial
import cv2
import face_recognition
import numpy as np

class CameraHandler:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_active = False
        self.enable_face_detection = False  
        self.frame_count = 0 
        self.last_face_locations = []  
        
        # Variables para rostros conocidos
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        self.last_recognitions = []  

    def start_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.is_active = True
        return self.is_active

    def set_face_detection(self, enabled):
        self.enable_face_detection = enabled

    def set_known_faces(self, encodings, names, ids):
        self.known_encodings = encodings
        self.known_names = names
        self.known_ids = ids

    def detect_faces_in_frame(self, frame):
        try:
            # Reducir resolución para detección más rápida
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convertir de BGR (OpenCV) a RGB (face_recognition)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detectar caras en el frame pequeño
            face_locations = face_recognition.face_locations(rgb_small_frame)

            # Escalar las coordenadas de vuelta al tamaño original
            scaled_face_locations = []
            for (top, right, bottom, left) in face_locations:
                scaled_face_locations.append((top * 4, right * 4, bottom * 4, left * 4))
            
            return scaled_face_locations
        except Exception as e:
            print(f"Error al detectar caras en camera_handler: {e}")
            return []

    def draw_face_rectangles(self, frame, face_locations):
        for (top, right, bottom, left) in face_locations:
            # Dibujar rectángulo verde alrededor de la cara
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Agregar etiqueta "Rostro detectado"
            cv2.putText(frame, 'Rostro detectado', (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame

    def read_frame(self):
        try:
            if self.cap is None:
                return None
            
            ret, frame = self.cap.read()
            if ret:
                # Si la detección facial está habilitada, procesar el frame
                frame = cv2.flip(frame, 1)

                if self.enable_face_detection:
                    # Procesar detección solo cada 3 frames para mejor rendimiento
                    if self.frame_count % 8 == 0:
                        if self.known_encodings:
                            # Si hay rostros conocidos, hacer reconocimiento
                            self.last_recognitions = self.recognize_faces_in_frame(frame)
                        else:
                            # Si no hay rostros conocidos, solo detección básica
                            self.last_face_locations = self.detect_faces_in_frame(frame)
                    
                    # Dibujar resultados
                    if self.known_encodings and self.last_recognitions:
                        frame = self.draw_recognition_results(frame, self.last_recognitions)
                    elif self.last_face_locations:
                        frame = self.draw_face_rectangles(frame, self.last_face_locations)
                    
                    self.frame_count += 1
                
                return frame
            else:
                return None
        except Exception as e:
            print(f"Error al leer el frame en camera_handler: {e}")
            return None
        
    def recognize_faces_in_frame(self, frame):
        if not self.known_encodings:
            return []
        
        try:
            # Reducir resolución para reconocimiento más rápido
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detectar ubicaciones y encodings de rostros
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, model="hog")
            
            recognitions = []
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Comparar con rostros conocidos
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.6)
                distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                
                nombre = "Desconocido"
                distancia = 1.0
                persona_id = None
                
                if True in matches:
                    # Encontrar la mejor coincidencia
                    best_match_index = np.argmin(distances)
                    
                    if matches[best_match_index] and distances[best_match_index] < 0.6:
                        nombre = self.known_names[best_match_index]
                        distancia = distances[best_match_index]
                        persona_id = self.known_ids[best_match_index]
                
                # Escalar coordenadas de vuelta al tamaño original
                top, right, bottom, left = face_location
                scaled_location = (top * 4, right * 4, bottom * 4, left * 4)
                
                recognitions.append((nombre, distancia, scaled_location, persona_id))
            
            return recognitions
            
        except Exception as e:
            print(f"Error en reconocimiento facial: {e}")
            return []

    def release_camera(self):
        if self.cap:
            self.cap.release()
            self.is_active = False

    def draw_recognition_results(self, frame, recognitions):
        for nombre, distancia, (top, right, bottom, left), persona_id in recognitions:
            if nombre == "Desconocido":
                color = (0, 0, 255)  # Rojo para desconocidos
                texto = "Desconocido"
                acceso = "Acceso denegado"
                # Convertir la región de la cara a blanco y negro
                face_roi = frame[top:bottom, left:right]
                if face_roi.size > 0:
                    gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                    gray_face = cv2.cvtColor(gray_face, cv2.COLOR_GRAY2BGR)
                    frame[top:bottom, left:right] = gray_face
            else:
                color = (0, 255, 0)  # Verde para conocidos
                confianza = max(0, (1 - distancia) * 100)
                texto = f"{nombre} ({confianza:.0f}%)"
                acceso = "Acceso permitido"
    
            # Dibujar rectángulo
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            # Fondo para el texto principal
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            # Texto principal (nombre o desconocido)
            cv2.putText(frame, texto, (left + 6, bottom - 18), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            # Texto de acceso debajo del recuadro
            cv2.putText(frame, acceso, (left, bottom + 25), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
        return frame
