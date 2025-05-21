#interfaz principal con tkinter
import tkinter as tk
from tkinter import filedialog
from camera_handler import CameraHandler
from image_handler import convert_cv_to_tk
import cv2

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial")
        self.root.geometry("800x600")

        self.camera = CameraHandler()
        self.frame = None

        self.create_widgets()
        self.update_loop()

    def create_widgets(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_start = tk.Button(btn_frame, text="Activar Cámara", command=self.start_camera)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(btn_frame, text="Desactivar Cámara", command=self.stop_camera)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.btn_open_image = tk.Button(btn_frame, text="Abrir Imagen", command=self.open_image)
        self.btn_open_image.pack(side=tk.LEFT, padx=10)

        self.video_label = tk.Label(self.root)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        self.video_label.pack(expand=True)

    def start_camera(self):
        if self.camera.start_camera():
            self.update_loop()

    def stop_camera(self):
        self.camera.release_camera()
        self.video_label.config(image='')

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

    def update_loop(self):
        if self.camera.is_active:
            frame = self.camera.read_frame()
            if frame is not None:
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()

                # Valores por defecto en caso de que tkinter aún no haya calculado tamaño
                if label_width < 10 or label_height < 10:
                    label_width, label_height = 640, 480

                img_tk = convert_cv_to_tk(frame, width=label_width, height=label_height)
                self.video_label.configure(image=img_tk)
                self.video_label.image = img_tk

        self.root.after(60, self.update_loop)  # 60 ms ≈ 60 fps (ajustable)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
