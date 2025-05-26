import cv2
import face_recognition
import numpy as np

class ImageHandler:
    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []

    def set_known_faces(self, encodings, names, ids):
        self.known_encodings = encodings
        self.known_names = names
        self.known_ids = ids

    def detect_faces_in_image(self, image):
        try:
            small_img = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
            rgb_small_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_img)
            scaled_face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]
            return scaled_face_locations
        except Exception as e:
            print(f"Error al detectar caras en image_handler: {e}")
            return []

    def recognize_faces_in_image(self, image):
        if not self.known_encodings:
            return []
        try:
            small_img = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
            rgb_small_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_img)
            face_encodings = face_recognition.face_encodings(rgb_small_img, face_locations, model="hog")
            recognitions = []
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.6)
                distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                nombre = "Desconocido"
                distancia = 1.0
                persona_id = None
                if True in matches:
                    best_match_index = np.argmin(distances)
                    if matches[best_match_index] and distances[best_match_index] < 0.6:
                        nombre = self.known_names[best_match_index]
                        distancia = distances[best_match_index]
                        persona_id = self.known_ids[best_match_index]
                top, right, bottom, left = face_location
                scaled_location = (top*4, right*4, bottom*4, left*4)
                recognitions.append((nombre, distancia, scaled_location, persona_id))
            return recognitions
        except Exception as e:
            print(f"Error en reconocimiento facial (imagen): {e}")
            return []

    def draw_face_rectangles(self, image, face_locations):
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(image, 'Rostro detectado', (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return image

    def draw_recognition_results(self, image, recognitions):
        for nombre, distancia, (top, right, bottom, left), persona_id in recognitions:
            if nombre == "Desconocido":
                color = (0, 0, 255)
                texto = "Desconocido"
                acceso = "Acceso denegado"
                face_roi = image[top:bottom, left:right]
                if face_roi.size > 0:
                    gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                    gray_face = cv2.cvtColor(gray_face, cv2.COLOR_GRAY2BGR)
                    image[top:bottom, left:right] = gray_face
            else:
                color = (0, 255, 0)
                confianza = max(0, (1 - distancia) * 100)
                texto = f"{nombre} ({confianza:.0f}%)"
                acceso = "Acceso permitido"
            cv2.rectangle(image, (left, top), (right, bottom), color, 2)
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(image, texto, (left + 6, bottom - 18),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(image, acceso, (left, bottom + 25),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
        return image