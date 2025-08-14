class AppState:
    """A model class to hold all application state variables."""
    def __init__(self):
        # Image and history state
        self.cv_img = None
        self.original_pil_img = None
        self.history = []

        # Zoom and view state
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Interactive editing state
        self.mode = None  # Can be 'crop', 'danger', or None
        self.crop_coords = None
        self.danger_coords = None
        
        # GA and Grid state
        self.danger_mask = None
        self.building_mask = None
        self.ppm_x = None
        self.ppm_y = None
        self.grid_w = None
        self.grid_h = None
        self.target_centers = []
        self.beacon_indices = []

    def reset(self):
        self.__init__()