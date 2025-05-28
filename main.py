#interfaz principal con tkinter
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from camera_handler import CameraHandler
from imagen_handler import ImageHandler
from imagen import convert_cv_to_tk
from database_manager import DatabaseManager
import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk
import subprocess  
import os
import argparse

class App:
    def __init__(self, root, split=False):
        self.root = root
        self.split = split
        self.root.title("Sistema de Acceso Empresarial")
        self.root.geometry("900x750")
        self.root.configure(bg="#eaf6fb")

        self.camera = CameraHandler()
        self.imagen = ImageHandler()
        self.db = DatabaseManager()
        self.frame = None
        self.face_detection_active = False

        # Variables para rostros conocidos
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []

        self.imagen_mostrada = None  # Nueva variable para imagen cargada
        self.imagen_reconocida = None  # Para guardar la imagen con resultados
        
        self.cargar_rostros_conocidos()
        self.create_widgets()
        self.update_loop()
        
        

    def create_widgets(self):
        # Título grande
        self.title_label = tk.Label(
            self.root, text="Sistema de Acceso Empresarial",
            font=("Segoe UI", 24, "bold"), bg="#eaf6fb", fg="#1a4d6b"
        )
        self.title_label.pack(pady=(20, 10))

        # Frame para botones principales
        btn_frame = tk.Frame(self.root, bg="#eaf6fb")
        btn_frame.pack(pady=10)

        self.btn_start = tk.Button(
            btn_frame, text="Activar Cámara", command=self.start_camera,
            font=("Segoe UI", 11), bg="#4CAF50", fg="white", activebackground="#388e3c",
            width=14, height=1, bd=0, cursor="hand2"
        )
        self.btn_start.pack(side=tk.LEFT, padx=8)

        self.btn_stop = tk.Button(
            btn_frame, text="Desactivar Cámara", command=self.stop_camera,
            font=("Segoe UI", 11), bg="#f44336", fg="white", activebackground="#b71c1c",
            width=14, height=1, bd=0, cursor="hand2"
        )
        self.btn_stop.pack(side=tk.LEFT, padx=8)

        self.btn_open_image = tk.Button(
            btn_frame, text="Abrir Imagen", command=self.open_image,
            font=("Segoe UI", 11), bg="#2196F3", fg="white", activebackground="#1565c0",
            width=14, height=1, bd=0, cursor="hand2"
        )
        self.btn_open_image.pack(side=tk.LEFT, padx=8)

        self.btn_cargar_rostro = tk.Button(
            btn_frame, text="Cargar Rostro Conocido", command=self.cargar_rostro_conocido,
            font=("Segoe UI", 11), bg="#ffb300", fg="#333", activebackground="#ff8f00",
            width=18, height=1, bd=0, cursor="hand2"
        )
        self.btn_cargar_rostro.pack(side=tk.LEFT, padx=8)

        # Frame para funciones de detección facial
        detection_frame = tk.Frame(self.root, bg="#eaf6fb")
        detection_frame.pack(pady=10)

        self.btn_toggle_detection = tk.Button(
            detection_frame, text="Activar Detección Facial", command=self.toggle_face_detection,
            font=("Segoe UI", 11), bg="#00bcd4", fg="white", activebackground="#008ba3",
            width=20, height=1, bd=0, cursor="hand2"
        )
        self.btn_toggle_detection.pack(side=tk.LEFT, padx=8)

        self.status_label = tk.Label(
            detection_frame, text="Estado: Detección facial desactivada",
            font=("Segoe UI", 12, "bold"), bg="#eaf6fb", fg="#d32f2f"
        )
        self.status_label.pack(side=tk.LEFT, padx=8)

        # Info label
        self.info_label = tk.Label(
            self.root, text="Información: Activa la cámara y la detección facial para comenzar",
            font=("Segoe UI", 12), bg="#eaf6fb", fg="#1976d2"
        )
        self.info_label.pack(pady=(10, 5))

        if self.split:
            self.video_window = tk.Toplevel(self.root)
            self.video_window.title("Video en Vivo")
            self.video_window.geometry("820x500")
            self.video_window.configure(bg="#222")
            self.video_label = tk.Label(self.video_window, bg="#222", width=800, height=480)
            self.video_label.pack(pady=10, fill=tk.BOTH, expand=True)
        else:
            # Layout clásico: video en la ventana principal
            self.video_label = tk.Label(self.root, bg="#222", width=800, height=480)
            self.video_label.pack(pady=10, fill=tk.BOTH, expand=True)
        

    def open_image(self):
        if self.imagen_mostrada is not None:
            # Si ya hay imagen, desmontar (cerrar)
            self.imagen_mostrada = None
            self.imagen_reconocida = None
            self.btn_open_image.config(text="Abrir Imagen")
            self.info_label.config(text="Imagen desmontada. Puedes abrir otra imagen o activar la cámara.")
            return
        file_path = None
        #Si es linux usar zenity
        if os.name == 'posix':
            try:
                result = subprocess.run(
                    ['zenity', '--file-selection'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                file_path = result.stdout.strip()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el selector de archivos: {e}")
        else:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                self.imagen_mostrada = img.copy()
                self.btn_open_image.config(text="Cerrar Imagen")
                self.info_label.config(text="Imagen cargada. Puedes desmontarla o activar la cámara.")
                # Realizar reconocimiento facial sobre la imagen cargada
                img_resultado = img.copy()
                if self.known_encodings:
                    recognitions = self.camera.recognize_faces_in_frame(img_resultado)
                    img_resultado = self.camera.draw_recognition_results(img_resultado, recognitions)
                else:
                    face_locations = self.camera.detect_faces_in_frame(img_resultado)
                    img_resultado = self.camera.draw_face_rectangles(img_resultado, face_locations)
                self.imagen_reconocida = img_resultado  # Guarda la imagen con resultados

                # Mostrar la imagen con resultados en el área de video
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()
                if label_width < 10 or label_height < 10:
                    label_width, label_height = 640, 480
                img_tk = convert_cv_to_tk(img_resultado, width=label_width, height=label_height)
                self.video_label.configure(image=img_tk)
                self.video_label.image = img_tk
            else:
                messagebox.showerror("Error", "No se pudo cargar la imagen")

    
    def start_camera(self):
        if not self.camera.seleccionar_camara(self.root):
            return 
        if self.camera.start_camera():
            self.update_loop()
            messagebox.showinfo("Éxito", "Cámara activada correctamente")
        else:
            messagebox.showerror("Error", "No se pudo activar la cámara")

    def stop_camera(self):
        self.camera.release_camera()
        self.video_label.config(image='')
        # Si se detiene la cámara, también desactivar detección
        if self.face_detection_active:
            self.toggle_face_detection()
        messagebox.showinfo("Información", "Cámara desactivada")

    def toggle_face_detection(self):
        if not self.camera.is_active and self.imagen_mostrada is None:
            messagebox.showwarning("Advertencia", "Primero debes activar la cámara o abrir una imagen")
            return
        
        self.face_detection_active = not self.face_detection_active
        self.camera.set_face_detection(self.face_detection_active)
        
        if self.face_detection_active:
            self.btn_toggle_detection.config(text="Desactivar Detección Facial", bg="lightcoral")
            self.status_label.config(text="Estado: Detección facial activada", fg="green")
            self.info_label.config(text="Información: Detección facial en tiempo real activa")
        else:
            self.btn_toggle_detection.config(text="Activar Detección Facial", bg="lightblue")
            self.status_label.config(text="Estado: Detección facial desactivada", fg="red")
            self.info_label.config(text="Información: Detección facial desactivada")

    def open_image(self):
        if self.imagen_mostrada is not None:
            # Si ya hay imagen, desmontar (cerrar)
            self.imagen_mostrada = None
            self.imagen_reconocida = None
            self.btn_open_image.config(text="Abrir Imagen", bg="#2196F3")
            self.info_label.config(text="Imagen desmontada. Puedes abrir otra imagen o activar la cámara.")
            return
        file_path = None
        #Si es linux usar zenity
        if os.name == 'posix':
            try:
                result = subprocess.run(
                    ['zenity', '--file-selection'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                file_path = result.stdout.strip()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el selector de archivos: {e}")
        else:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                self.imagen_mostrada = img.copy()
                self.btn_open_image.config(text="Cerrar Imagen", bg="#b71c1c")
                self.info_label.config(text="Imagen cargada. Puedes desmontarla o activar la cámara.")
            else:
                messagebox.showerror("Error", "No se pudo cargar la imagen")

    def cargar_rostro_conocido(self):
        # 1. Intentar capturar rostro desde la cámara
        if self.camera.is_active:
            frame = self.camera.read_frame()
            if frame is not None:
                # Convertir de BGR a RGB para face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_frame)
                if len(encodings) == 0:
                    resp = messagebox.askyesno(
                        "No se detectó rostro",
                        "No se detectó ningún rostro en la cámara.\n¿Quieres seleccionar una imagen desde archivo?"
                    )
                    if not resp:
                        return
                elif len(encodings) > 1:
                    messagebox.showwarning("Advertencia", "Se detectaron múltiples rostros en la cámara. Se usará el primero.")
                    encoding = encodings[0]
                else:
                    encoding = encodings[0]
    
                if len(encodings) >= 1:
                    nombre = simpledialog.askstring("Nombre", "Ingresa el nombre de la persona:")
                    if not nombre:
                        return
                    # Guardar en base de datos (sin imagen de referencia)
                    persona_id = self.db.agregar_persona(nombre, encoding, None)
                    if persona_id:
                        self.cargar_rostros_conocidos()
                        messagebox.showinfo("Éxito", f"Rostro de '{nombre}' guardado correctamente desde cámara")
                    else:
                        messagebox.showerror("Error", "No se pudo guardar el rostro en la base de datos")
                    return  # Ya terminó, no sigue a cargar desde archivo
    
        # 2. Si no hay cámara o no se detectó rostro, cargar desde archivo
        file_path = None
        #Si es linux usar zenity
        if os.name == 'posix':
            try:
                result = subprocess.run(
                    ['zenity', '--file-selection'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                file_path = result.stdout.strip()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el selector de archivos: {e}")
        else:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return
        try:
            imagen = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(imagen)
            if len(encodings) == 0:
                messagebox.showerror("Error", "No se detectó ningún rostro en la imagen")
                return
            if len(encodings) > 1:
                messagebox.showwarning("Advertencia", "Se detectaron múltiples rostros. Se usará el primero.")
            nombre = simpledialog.askstring("Nombre", "Ingresa el nombre de la persona:")
            if not nombre:
                return
            encoding = encodings[0]
            persona_id = self.db.agregar_persona(nombre, encoding, file_path)
            if persona_id:
                self.cargar_rostros_conocidos()
                messagebox.showinfo("Éxito", f"Rostro de '{nombre}' guardado correctamente desde archivo")
            else:
                messagebox.showerror("Error", "No se pudo guardar el rostro en la base de datos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la imagen: {e}")


    def cargar_rostros_conocidos(self):
        try:
            encodings, names, ids = self.db.obtener_encodings_conocidos()
            self.known_encodings = encodings
            self.known_names = names
            self.known_ids = ids
            
            # Pasar rostros conocidos a camera_handler
            self.camera.set_known_faces(encodings, names, ids)
            self.imagen.set_known_faces(encodings, names, ids)
        
        except Exception as e:
            print(f"Error al cargar rostros conocidos: {e}")
            self.known_encodings = []
            self.known_names = []
            self.known_ids = []

    def update_loop(self):
        label_width = self.video_label.winfo_width()
        label_height = self.video_label.winfo_height()
        if label_width < 10 or label_height < 10:
            label_width, label_height = 640, 480
    
        if self.camera.is_active:
            frame = self.camera.read_frame()
            if frame is not None:
                # Reconocimiento facial en cámara si está activo
                if self.face_detection_active:
                    if self.known_encodings:
                        recognitions = self.camera.recognize_faces_in_frame(frame)
                        frame = self.camera.draw_recognition_results(frame, recognitions)
                    else:
                        face_locations = self.camera.detect_faces_in_frame(frame)
                        frame = self.camera.draw_face_rectangles(frame, face_locations)
                img_tk = convert_cv_to_tk(frame, width=label_width, height=label_height)
                self.video_label.configure(image=img_tk)
                self.video_label.image = img_tk
        elif self.imagen_mostrada is not None:
            # Reconocimiento facial en imagen cargada (igual que en cámara)
            img_resultado = self.imagen_mostrada.copy()
            if self.face_detection_active:
                if self.known_encodings:
                    recognitions = self.imagen.recognize_faces_in_image(img_resultado)
                    img_resultado = self.imagen.draw_recognition_results(img_resultado, recognitions)
                else:
                    face_locations = self.imagen.detect_faces_in_image(img_resultado)
                    img_resultado = self.imagen.draw_face_rectangles(img_resultado, face_locations)
                    img_resultado = self.camera.draw_face_rectangles(img_resultado, face_locations)
            img_tk = convert_cv_to_tk(img_resultado, width=label_width, height=label_height)
            self.video_label.configure(image=img_tk)
            self.video_label.image = img_tk
            self.imagen_reconocida = img_resultado  # Guarda la última imagen reconocida
        else:
            # Mostrar ruido sal y pimienta animado
            ruido = self.generar_ruido_salpimienta(label_width, label_height)
            img_ruido = Image.fromarray(ruido)
            img_tk = ImageTk.PhotoImage(img_ruido)
            self.video_label.configure(image=img_tk)
            self.video_label.image = img_tk
    
        self.root.after(180, self.update_loop)
        
    def generar_ruido_salpimienta(self, width, height):
        # Genera una imagen de ruido blanco y negro (sal y pimienta)
        ruido = np.random.choice([0, 255], (height, width, 1), p=[0.5, 0.5]).astype('uint8')
        ruido = np.repeat(ruido, 3, axis=2)  # Convertir a RGB
        return ruido

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-split', action='store_true', help='Divide el panel administrativo de la imagen de la cámara')
    args = parser.parse_args()
    root = tk.Tk()
    app = App(root, split=args.split)
    root.mainloop()
