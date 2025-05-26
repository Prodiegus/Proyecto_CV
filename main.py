#interfaz principal con tkinter
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from camera_handler import CameraHandler
from image_handler import convert_cv_to_tk
from database_manager import DatabaseManager
import cv2
import face_recognition

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial")
        self.root.geometry("800x700")

        self.camera = CameraHandler()
        self.db = DatabaseManager()
        self.frame = None
        self.face_detection_active = False  
        
        # Variables para rostros conocidos
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        
        self.cargar_rostros_conocidos()

        self.create_widgets()
        self.update_loop()

    def create_widgets(self):
        # Frame para botones principales
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_start = tk.Button(btn_frame, text="Activar Cámara", command=self.start_camera)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(btn_frame, text="Desactivar Cámara", command=self.stop_camera)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.btn_open_image = tk.Button(btn_frame, text="Abrir Imagen", command=self.open_image)
        self.btn_open_image.pack(side=tk.LEFT, padx=10)

        self.btn_cargar_rostro = tk.Button(btn_frame, text="Cargar Rostro Conocido", 
                                         command=self.cargar_rostro_conocido, bg="lightgreen")
        self.btn_cargar_rostro.pack(side=tk.LEFT, padx=10)

        # Frame para funciones de detección facial
        detection_frame = tk.Frame(self.root)
        detection_frame.pack(pady=5)

        self.btn_toggle_detection = tk.Button(
            detection_frame, 
            text="Activar Detección Facial", 
            command=self.toggle_face_detection,
            bg="lightblue"
        )
        self.btn_toggle_detection.pack(side=tk.LEFT, padx=10)

        # Etiqueta de estado
        self.status_label = tk.Label(
            detection_frame, 
            text="Estado: Detección facial desactivada", 
            fg="red"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Frame para mostrar información de detección
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)

        self.info_label = tk.Label(
            info_frame, 
            text="Información: Activa la cámara y la detección facial para comenzar",
            fg="blue"
        )
        self.info_label.pack()

        self.video_label = tk.Label(self.root)
        self.video_label.pack(fill=tk.BOTH, expand=True)

    def start_camera(self):
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
        if not self.camera.is_active:
            messagebox.showwarning("Advertencia", "Primero debes activar la cámara")
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
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                # Obtener dimensiones del contenedor
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()
                
                # Valores por defecto en caso de que tkinter aún no haya calculado tamaño
                if label_width < 10 or label_height < 10:
                    label_width, label_height = 640, 480
                
                # Convertir y redimensionar la imagen manteniendo la relación de aspecto
                img_tk = convert_cv_to_tk(img, width=label_width, height=label_height)
                self.video_label.configure(image=img_tk)
                self.video_label.image = img_tk
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
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de rostro",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
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
        
        except Exception as e:
            print(f"Error al cargar rostros conocidos: {e}")
            self.known_encodings = []
            self.known_names = []
            self.known_ids = []

    def update_loop(self):
        if self.camera.is_active:
            frame = self.camera.read_frame()
            if frame is not None:
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()

                # Valores por defecto en caso de que tkinter aún no haya calculado tamaño
                if label_width < 10 or label_height < 10:
                    label_width, label_height = 640, 480

                try:
                    img_tk = convert_cv_to_tk(frame, width=label_width, height=label_height)
                    self.video_label.configure(image=img_tk)
                    self.video_label.image = img_tk
                except Exception as e:
                    print(f"Error al convertir la imagen: {e}")

        self.root.after(180, self.update_loop)  # 60 ms ≈ 16 fps (ajustable)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
