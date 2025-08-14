from tkinter import filedialog, messagebox
from PIL import Image
import cv2
import numpy as np
import json

COVERAGE = 5

class AppController:
    """The controller class holding all application logic."""
    def __init__(self, app_state, image_processor, ga_solver):
        self.state = app_state
        self.image_processor = image_processor
        self.ga_solver = ga_solver
        self.canvas_view = None
        self.control_panel = None

    def browse_image(self):
        self.state.reset()
        self.control_panel.clear_grid_entries()
        path = filedialog.askopenfilename(filetypes=[('Image Files', '*.png *.jpg *.jpeg')])
        if not path:
            return
        
        self.state.history.clear()
        self.state.cv_img = cv2.imread(path)
        rgb_img = cv2.cvtColor(self.state.cv_img, cv2.COLOR_BGR2RGB)
        self.state.original_pil_img = Image.fromarray(rgb_img)
        
        self.state.zoom_level = 1.0
        self.state.mode = None
        self.state.danger_mask = None
        self.state.building_mask = None
        self.state.beacon_indices.clear()
        
        self.canvas_view.update_display()
        self.control_panel.set_status(f"Loaded: {path.split('/')[-1]}")

    def apply_crop(self):
        if not self.state.crop_coords:
            messagebox.showwarning('Warning', 'Please toggle and position a crop region first.')
            return
        
        x0, y0, x1, y1 = map(int, self.state.crop_coords)
        if x1 <= x0 or y1 <= y0:
            return

        self.state.history.append(self.state.cv_img.copy())
        
        self.state.cv_img = self.state.cv_img[y0:y1, x0:x1]
        
        rgb_img = cv2.cvtColor(self.state.cv_img, cv2.COLOR_BGR2RGB)
        self.state.original_pil_img = Image.fromarray(rgb_img)
        self.state.zoom_level = 1.0
        self.state.mode = None
        self.state.crop_coords = None
        
        self.canvas_view.update_display()
        self.control_panel.set_status(f'Image cropped to {x1-x0}x{y1-y0}.')
    
    def _toggle_region(self, region_type):
        if self.state.original_pil_img is None:
            return

        canvas = self.canvas_view.canvas
        canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()
        view_x0 = canvas.canvasx(0)
        view_y0 = canvas.canvasy(0)

        center_x = (view_x0 + canvas_w / 2) / self.state.zoom_level
        center_y = (view_y0 + canvas_h / 2) / self.state.zoom_level
        
        if region_type == 'crop':
            rect_size = 100
            self.state.crop_coords = [center_x - rect_size, center_y - rect_size, center_x + rect_size, center_y + rect_size]
            self.state.mode = 'crop'
            self.control_panel.set_status('Crop edit mode.')
        elif region_type == 'danger':
            rect_size = 50
            self.state.danger_coords = [center_x - rect_size, center_y - rect_size, center_x + rect_size, center_y + rect_size]
            self.state.mode = 'danger'
            self.control_panel.set_status('Danger zone edit mode.')
        
        self.canvas_view.update_display()

    def toggle_crop_region(self):
        self._toggle_region('crop')

    def toggle_danger_region(self):
        self._toggle_region('danger')

    def apply_danger_overlay(self):
        if not self.state.danger_coords:
            messagebox.showwarning('Warning', 'Please toggle a danger region first.')
            return
            
        x0, y0, x1, y1 = map(int, self.state.danger_coords)
        h, w, _ = self.state.cv_img.shape
        
        if self.state.danger_mask is None:
            self.state.danger_mask = np.zeros((h, w), dtype=np.uint8)

        if self.state.danger_mask.shape[0] != h or self.state.danger_mask.shape[1] != w:
            self.state.danger_mask = cv2.resize(self.state.danger_mask, (w, h))
            
        cv2.rectangle(self.state.danger_mask, (x0, y0), (x1, y1), 255, thickness=-1)
        
        self.state.mode = None
        self.state.danger_coords = None
        
        self.canvas_view.update_display()
        self.control_panel.set_status('Danger zone applied and visualized.')

    def set_grid(self):
        if self.state.cv_img is None:
            return
        real_w_str, real_h_str = self.control_panel.get_grid_entries()
        try:
            rw, rh = float(real_w_str), float(real_h_str)
            if rw <= 0 or rh <= 0: 
                raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror('Error', 'Please enter valid, positive numbers for real-world size.')
            return

        h, w, _ = self.state.cv_img.shape
        self.state.ppm_x, self.state.ppm_y = w / rw, h / rh
        step_x, step_y = self.state.ppm_x * 0.5, self.state.ppm_y * 0.5
        self.state.grid_w, self.state.grid_h = int(rw / 0.5), int(rh / 0.5)
        
        self.state.target_centers = [
            (j * step_x + step_x / 2, i * step_y + step_y / 2)
            for i in range(self.state.grid_h) for j in range(self.state.grid_w)
        ]
        self.control_panel.set_status(f'Grid set: {self.state.grid_w}x{self.state.grid_h}')
        self.canvas_view.update_display()
    
    def cancel_current_mode(self, event=None):
        if self.state.mode == "crop":
            self.state.crop_coords = None
            self.state.mode = None
            self.control_panel.set_status('Crop operation cancelled.')
            self.canvas_view.update_display()
        elif self.state.mode == "danger":
            self.state.danger_coords = None
            self.state.mode = None
            self.control_panel.set_status("Danger zone operation cancelled.")
            self.canvas_view.update_display()

    def run_ga(self):
        if not self.state.target_centers:
            messagebox.showwarning('Warning', 'Please set the grid first.')
            return

        self.control_panel.set_status('Running analysis...')
        self.state.building_mask = self.image_processor.detect_building_mask(self.state.cv_img)
        
        if self.state.danger_mask is None:
            self.state.danger_mask = self.image_processor.detect_danger_zones(self.state.cv_img)
        
        h, w = self.state.building_mask.shape
        danger_mask_resized = cv2.resize(self.state.danger_mask, (w, h))

        placements = [
            i for i, (x, y) in enumerate(self.state.target_centers)
            if self.state.building_mask[int(y), int(x)] > 0 and danger_mask_resized[int(y), int(x)] == 0
        ]
        if not placements:
            messagebox.showerror('Error', 'No valid placement locations found in the building mask.')
            return
            
        centers_arr = np.array(self.state.target_centers)
        cand_arr = centers_arr[placements]
        dist = np.linalg.norm(centers_arr[:, None, :] - cand_arr[None, :, :], axis=2)
        ble_px = COVERAGE * self.state.ppm_x
        coverage_sets = [set(np.where(dist[:, j] <= ble_px)[0]) for j in range(len(placements))]
        
        self.state.beacon_indices = self.ga_solver.run(placements, self.state.target_centers, coverage_sets, ble_px)
        
        self.canvas_view.update_display()
        self.control_panel.set_status(f'Beacon estimation complete. {len(self.state.beacon_indices)} beacons placed.')
        messagebox.showinfo('Complete', 'Beacon estimation complete.')

    def export_json(self):
        if not self.state.beacon_indices or self.state.danger_mask is None or self.state.grid_w is None:
            messagebox.showwarning('Warning', 'Prerequisites not met. Run Grid Setup, Danger Application, and GA.')
            return

        h, w, _ = self.state.cv_img.shape
        danger_mask_resized = cv2.resize(self.state.danger_mask, (w, h))
        safe_coords = [
            [divmod(idx, self.state.grid_w)[0], divmod(idx, self.state.grid_w)[1]]
            for idx, (x, y) in enumerate(self.state.target_centers)
            if danger_mask_resized[int(y), int(x)] == 0
        ]
        
        parent_devices = []
        for idx in self.state.beacon_indices:
            i, j = divmod(idx, self.state.grid_w)
            px, py = self.state.target_centers[idx]
            parent_devices.append({"grid_coords": [i, j], "pixel_coords": [int(px), int(py)]})
            
        real_w, real_h = self.control_panel.get_grid_entries()
        export_data = {
            "real_world_dimensions": {"width_m": float(real_w), "height_m": float(real_h)},
            "pixel_dimensions": {"width_px": w, "height_px": h},
            "pixels_per_meter": {"x": self.state.ppm_x, "y": self.state.ppm_y},
            "grid_dimensions": {"width": self.state.grid_w, "height": self.state.grid_h},
            "parent_devices": parent_devices,
            "safe_grid_coordinates": safe_coords
        }
        
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not path: 
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=4)
        messagebox.showinfo('Success', 'JSON file exported.')

    def undo(self):
        if not self.state.history: 
            return
        self.state.cv_img = self.state.history.pop()
        rgb_img = cv2.cvtColor(self.state.cv_img, cv2.COLOR_BGR2RGB)
        self.state.original_pil_img = Image.fromarray(rgb_img)
        self.state.zoom_level = 1.0
        self.canvas_view.update_display()
        self.control_panel.set_status('Last crop undone.')

    def _zoom(self, factor):
        if self.state.original_pil_img is None:
            return
        
        new_zoom = self.state.zoom_level * factor

        if self.state.min_zoom <= new_zoom <= self.state.max_zoom:
            self.state.zoom_level = new_zoom
            self.canvas_view.update_display()
    
    def zoom_in(self):
        self._zoom(1.2)

    def zoom_out(self):
        self._zoom(0.8)