import os
import time
from io import BytesIO

import cv2
from dotenv import load_dotenv
from msrest.exceptions import HttpOperationError
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceAttributeType
from azure.core.credentials import AzureKeyCredential

# ── Carga variables de entorno ──────────────────────────────────────────────
load_dotenv()  
KEY      = os.getenv("AZURE_FACE_KEY")
ENDPOINT = os.getenv("AZURE_FACE_ENDPOINT")  # e.g. https://recofacial.cognitiveservices.azure.com/

# ── Cliente Azure Face API ─────────────────────────────────────────────────
client = FaceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

# ── Atributos sensibles (edad, género, sonrisa, gafas, emoción) ───────────
USE_SENSITIVE     = False  # False para detección básica sin atributos
ATTRS_SENSITIVE = [
    FaceAttributeType.AGE,
    FaceAttributeType.SMILE,
    FaceAttributeType.GLASSES,
]

# ── Inicialización de cámara ────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la cámara.")

FRAME_SKIP  = 15
frame_count = 0
last_faces  = []

def detect(frame):
    """
    Detecta caras en `frame`.
    Si USE_SENSITIVE=True pide además atributos.
    Maneja rate-limit y deshabilita atributos si no están aprobados.
    """
    global USE_SENSITIVE

    # Reducir tamaño al 50% para aligerar la petición
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (w // 2, h // 2))

    # Codificar JPEG en memoria
    # (cv2.imencode devuelve un array de bytes)
    success, buf = cv2.imencode('.jpg', small, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    if not success:
        return []

    stream = BytesIO(buf.tobytes())
    stream.seek(0)

    params = {
        "image": stream,
        "detection_model": "detection_01",
    }
    if USE_SENSITIVE:
        params["return_face_attributes"] = ATTRS_SENSITIVE

    try:
        return client.detect(
            image_content=stream,
            detection_model="detection_01",
            recognition_model="recognition_04",  # Usa el modelo recomendado
            return_face_id=False,
            return_face_attributes=None
        )
    except Exception as err:
        print("Error Face API:", err)
        return []
try:
    while True:
        ret, img = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP == 0:
            last_faces = detect(img)

        # Dibujar cada detección
        for face in last_faces:
            r = face.face_rectangle
            # Multiplicamos por 2 porque detectamos sobre la versión reducida
            x, y, w, h = r.left * 2, r.top * 2, r.width * 2, r.height * 2
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if USE_SENSITIVE and face.face_attributes:
                a   = face.face_attributes
                emo = a.emotion.as_dict()
                dom = max(emo.items(), key=lambda kv: kv[1])[0]
                text = f"{int(a.age)}y/{a.gender} Sm:{a.smile:.2f} Emo:{dom}"
            else:
                text = "Face detected"

            cv2.putText(
                img, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )

        cv2.imshow("Azure Face", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
