# Sistema de Reconocimiento Facial

Este proyecto implementa un sistema de reconocimiento facial utilizando OpenCV y Tkinter para la interfaz gráfica.

## Requisitos previos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)

### 1. Crear un entorno virtual (opcional pero recomendado)

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
# source venv/bin/activate
```

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto instalará las siguientes bibliotecas:
- pillow: Para el procesamiento de imágenes
- opencv-python: Para visión por computadora y manejo de cámaras

## Ejecutar la aplicación

```bash
python main.py
```

## Funcionalidades (por ahora la principales)

La aplicación ofrece las siguientes funcionalidades:

- **Activar Cámara**: Inicia la captura de video desde la cámara por defecto
- **Desactivar Cámara**: Detiene la captura de video
- **Abrir Imagen**: Permite seleccionar y mostrar una imagen desde el sistema de archivos

## Estructura del proyecto

- `main.py`: Contiene la interfaz principal de usuario con Tkinter
- `camera_handler.py`: Gestiona la conexión con la cámara usando OpenCV
- `image_handler.py`: Proporciona funciones para el procesamiento y visualización de imágenes

