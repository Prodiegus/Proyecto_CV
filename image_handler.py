# Logica modular para el manejo de imagenes
from PIL import Image, ImageTk
import cv2

def convert_cv_to_tk(frame, width=None, height=None):
    """Convierte frame BGR de OpenCV a PhotoImage de Tkinter, ajustado al tamaño dado manteniendo la relación de aspecto."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)

    if width and height:
        # Mantener la relación de aspecto de la imagen original
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        container_ratio = width / height
        
        if container_ratio > aspect_ratio:  # El contenedor es más ancho
            new_height = height
            new_width = int(height * aspect_ratio)
        else:  # El contenedor es más alto o igual
            new_width = width
            new_height = int(width / aspect_ratio)
            
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Crear una imagen en blanco del tamaño del contenedor
        background = Image.new('RGB', (width, height), (0, 0, 0))
        
        # Calcular posición para centrar la imagen redimensionada
        offset_x = (width - new_width) // 2
        offset_y = (height - new_height) // 2
        
        # Pegar la imagen redimensionada en el centro
        background.paste(img, (offset_x, offset_y))
        img = background

    return ImageTk.PhotoImage(image=img)
