import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
import cv2

class ImageCanvasView(ctk.CTkFrame):
    """The view class for the main image canvas and its interactions."""
    def __init__(self, master, app_state):
        super().__init__(master)
        self.app_state = app_state

        # Local view state
        self.image_tk = None
        self.drag_data = {'x': 0, 'y': 0}
        self.resizing = False
        self.moving = False
        self.resize_dir = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas = ctk.CTkCanvas(self, bg="black")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Bind events
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

    def update_display(self):
        if self.app_state.original_pil_img is None: 
            return

        display_pil = self.app_state.original_pil_img.copy()
        if self.app_state.danger_mask is not None:
            display_cv = cv2.cvtColor(np.array(display_pil), cv2.COLOR_RGB2BGR)
            red_layer = np.zeros_like(display_cv, np.uint8)
            red_layer[:] = (0, 0, 255)

            h, w, _ = display_cv.shape
            mask_resized = cv2.resize(self.app_state.danger_mask, (w, h))
            bool_mask = mask_resized.astype(bool)
            
            display_cv[bool_mask] = cv2.addWeighted(display_cv[bool_mask], 0.7, red_layer[bool_mask], 0.3, 0)
            display_pil = Image.fromarray(cv2.cvtColor(display_cv, cv2.COLOR_BGR2RGB))

        w, h = display_pil.size
        zoom = self.app_state.zoom_level
        new_w, new_h = int(w * zoom), int(h * zoom)
        
        scaled_pil = display_pil.resize((new_w, new_h), Image.LANCZOS)
        self.image_tk = ImageTk.PhotoImage(scaled_pil)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.canvas.configure(scrollregion=(0, 0, new_w, new_h))

        if self.app_state.crop_coords:
            x0, y0, x1, y1 = [c * zoom for c in self.app_state.crop_coords]
            self.canvas.create_rectangle(x0, y0, x1, y1, outline='dodgerblue', width=2)

        if self.app_state.danger_coords:
            x0, y0, x1, y1 = [c * zoom for c in self.app_state.danger_coords]
            self.canvas.create_rectangle(x0, y0, x1, y1, outline='red', width=2)
        
        r = 10  # Beacon radius in pixels
        if self.app_state.beacon_indices:
            for idx in self.app_state.beacon_indices:
                x, y = self.app_state.target_centers[idx]
                x_scaled, y_scaled = x * zoom, y * zoom
                self.canvas.create_oval(x_scaled - r, y_scaled - r, x_scaled + r, y_scaled + r, outline='cyan', width=3)
        
        if self.app_state.grid_w and self.app_state.grid_h:
            step_x_px = (w/self.app_state.grid_w)*zoom
            step_y_px = (h/self.app_state.grid_h)*zoom

            # draw vertical lines
            for i in range(1, self.app_state.grid_w):
                x = i * step_x_px
                self.canvas.create_line(x, 0, x, new_h, fill='gray', dash=(2, 2))

            for i in range(1, self.app_state.grid_h):
                y = i * step_y_px
                self.canvas.create_line(0, y, new_w, y, fill='gray', dash=(2, 2))

    def on_mouse_wheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        new_zoom = self.app_state.zoom_level * factor
        
        if self.app_state.min_zoom <= new_zoom <= self.app_state.max_zoom:
            self.app_state.zoom_level = new_zoom
            self.update_display()

    def on_press(self, e):
        if self.app_state.mode is None: 
            return
        
        mx_img = self.canvas.canvasx(e.x) / self.app_state.zoom_level
        my_img = self.canvas.canvasy(e.y) / self.app_state.zoom_level
        
        coords = self.app_state.crop_coords if self.app_state.mode == 'crop' else self.app_state.danger_coords
        if not coords: 
            return
        
        x0, y0, x1, y1 = coords
        self.drag_data = {'x': mx_img, 'y': my_img}
        self.resizing, self.moving = False, False
        edge_size = 5 / self.app_state.zoom_level
        
        if abs(mx_img - x0) <= edge_size and y0 < my_img < y1: 
            self.resizing, self.resize_dir = True, 'left'
        elif abs(mx_img - x1) <= edge_size and y0 < my_img < y1: 
            self.resizing, self.resize_dir = True, 'right'
        elif abs(my_img - y0) <= edge_size and x0 < mx_img < x1: 
            self.resizing, self.resize_dir = True, 'top'
        elif abs(my_img - y1) <= edge_size and x0 < mx_img < x1: 
            self.resizing, self.resize_dir = True, 'bottom'
        elif x0 < mx_img < x1 and y0 < my_img < y1: 
            self.moving = True

    def on_drag(self, e):
        if not self.moving and not self.resizing: 
            return
        
        mx_img = self.canvas.canvasx(e.x) / self.app_state.zoom_level
        my_img = self.canvas.canvasy(e.y) / self.app_state.zoom_level
        dx_img, dy_img = mx_img - self.drag_data['x'], my_img - self.drag_data['y']
        
        coords = self.app_state.crop_coords if self.app_state.mode == 'crop' else self.app_state.danger_coords
        x0, y0, x1, y1 = coords

        if self.resizing:
            if self.resize_dir == 'left': 
                coords[0] += dx_img
            elif self.resize_dir == 'right': 
                coords[2] += dx_img
            elif self.resize_dir == 'top': 
                coords[1] += dy_img
            elif self.resize_dir == 'bottom': 
                coords[3] += dy_img
        elif self.moving:
            coords[0] += dx_img
            coords[1] += dy_img
            coords[2] += dx_img
            coords[3] += dy_img

        self.drag_data = {'x': mx_img, 'y': my_img}
        self.update_display()

    def on_release(self, e):
        self.resizing = self.moving = False
        self.resize_dir = None