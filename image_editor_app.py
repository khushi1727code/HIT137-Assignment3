import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper and Resizer")

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack()

        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()

        self.image = None
        self.tk_image = None
        self.start_x = self.start_y = 0
        self.crop_rect = None

        # Bind mouse events for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def load_image(self):
        # Pick image file from device
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.image = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
            self.display_image(self.image)

    def display_image(self, img):
        self.pil_image = Image.fromarray(img)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def on_mouse_press(self, event):
        # Start crop rectangle
        self.start_x = event.x
        self.start_y = event.y
        self.crop_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        # Update crop rectangle as mouse drags
        self.canvas.coords(self.crop_rect, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_release(self, event):
        # Finalize cropping on mouse release
        end_x, end_y = event.x, event.y
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

        if self.image is not None:
            cropped = self.image[y1:y2, x1:x2]
            if cropped.size > 0:
                self.show_cropped(cropped)

    def show_cropped(self, cropped_img):
        # Display cropped image in new window with resize slider
        top = tk.Toplevel(self.root)
        top.title("Cropped Image")

        self.original_cropped_pil = Image.fromarray(cropped_img)
        self.resized_image_to_save = self.original_cropped_pil.copy()

        self.cropped_tk = ImageTk.PhotoImage(self.resized_image_to_save)
        self.cropped_label = tk.Label(top, image=self.cropped_tk)
        self.cropped_label.image = self.cropped_tk
        self.cropped_label.pack()

        self.scale_display = tk.Label(top, text="Resize: 100%")
        self.scale_display.pack()

        self.slider = tk.Scale(top, from_=10, to=200, orient=tk.HORIZONTAL, label="Resize %")
        self.slider.set(100)
        self.slider.pack()

        # Update image only when slider released to avoid lag
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

        save_btn = tk.Button(top, text="Save Image", command=self.save_image)
        save_btn.pack()

    def on_slider_release(self, event):
        scale_val = self.slider.get()
        self.scale_display.config(text=f"Resize: {scale_val}%")
        self.resize_image(scale_val)

    def resize_image(self, scale_val):
        scale = scale_val / 100.0
        new_width = int(self.original_cropped_pil.width * scale)
        new_height = int(self.original_cropped_pil.height * scale)
        resized = self.original_cropped_pil.resize((new_width, new_height), Image.LANCZOS)

        self.resized_image_to_save = resized
        self.cropped_tk = ImageTk.PhotoImage(resized)
        self.cropped_label.config(image=self.cropped_tk)
        self.cropped_label.image = self.cropped_tk

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg")])
        if file_path:
            self.resized_image_to_save.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()