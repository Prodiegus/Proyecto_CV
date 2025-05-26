import cv2
from PIL import Image, ImageTk

def convert_cv_to_tk(cv_img, width=None, height=None):
    img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    if width and height:
        # Mantener aspect ratio
        orig_width, orig_height = img_pil.size
        ratio = min(width / orig_width, height / orig_height)
        new_size = (int(orig_width * ratio), int(orig_height * ratio))
        img_pil = img_pil.resize(new_size, Image.LANCZOS)
    return ImageTk.PhotoImage(img_pil)