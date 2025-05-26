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

Al instalar las dependencias, puede arrojar error el instalar face_recognition, ya que, se debe instalar dlib.
Para resolver esto, hay que ir a:

```
https://github.com/z-mahmud22/Dlib_Windows_Python3.x
```

Y elegir el archivo que corresponda a la versión de Python que se esté usando.

Se deja el link con el archivo de acuerdo a la versión de python:

- Python 3.12: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.99-cp312-cp312-win_amd64.whl#sha256=20c62e606ca4c9961305f7be3d03990380d3e6c17f8d27798996e97a73271862
- Python 3.11: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl#sha256=20c62e606ca4c9961305f7be3d03990380d3e6c17f8d27798996e97a73271862
- Python 3.10: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.22.99-cp310-cp310-win_amd64.whl#sha256=20c62e606ca4c9961305f7be3d03990380d3e6c17f8d27798996e97a73271862
- Python 3.9: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.22.99-cp39-cp39-win_amd64.whl#sha256=20c62e606ca4c9961305f7be3d03990380d3e6c17f8d27798996e97a73271862
- Python 3.8: https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.22.99-cp38-cp38-win_amd64.whl#sha256=20c62e606ca4c9961305f7be3d03990380d3e6c17f8d27798996e97a73271862

Luego hay que reemplazar la línea de dlib en el archivo `requirements.txt` por la que se encuentra en el link de arriba.

Ejemplo:

```
dlib @ https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.99-cp312-cp312-win_amd64.whl#sha256=20c62e606ca4c9961305f7be3d03990380d3e6c17f8d27798996e97a73271862
```

Y luego instalar las dependencias con el siguiente comando:

```bash
pip install -r requirements.txt
```

Esto instalará las siguientes bibliotecas:

- pillow: Para el procesamiento de imágenes
- opencv-python: Para visión por computadora y manejo de cámaras
- face-recognition: Para el reconocimiento facial
- face_recognition_models: Para el reconocimiento facial
- numpy: Para el procesamiento de imágenes
- dlib: Para el reconocimiento facial

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
- `database_manager.py`: Gestiona la base de datos SQLite
- `init_database.py`: Inicializa la base de datos SQLite

## Configuración de la base de datos

1. Ejecutar el archivo `init_database.py` para crear la base de datos.

Este creará la base de datos y las tablas necesarias en el archivo `database/proyecto_cv.db`.

## Configuración de la cámara

La cámara se encuentra en el archivo `camera_handler.py`.
