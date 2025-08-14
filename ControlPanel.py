import customtkinter as ctk

class ControlPanel(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, width=250)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Controls")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.scrollable_frame, text="View Controls", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), padx=10, anchor="w")
        
        zoom_frame = ctk.CTkFrame(self.scrollable_frame)
        zoom_frame.pack(fill="x", padx=10, pady=2)
        zoom_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(zoom_frame, text="Zoom In (+)", command=self.controller.zoom_in).grid(row=0, column=0, padx=(0,2), sticky="ew")
        ctk.CTkButton(zoom_frame, text="Zoom Out (-)", command=self.controller.zoom_out).grid(row=0, column=1, padx=(2,0), sticky="ew")
        
        # file & undo
        ctk.CTkLabel(self.scrollable_frame, text="File Operations", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), padx=10, anchor="w")
        ctk.CTkButton(self.scrollable_frame, text="Open Image", command=self.controller.browse_image).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(self.scrollable_frame, text="Export JSON", command=self.controller.export_json).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(self.scrollable_frame, text="Undo", command=self.controller.undo).pack(fill="x", padx=10, pady=2)

        # grid settings
        ctk.CTkLabel(self.scrollable_frame, text="Grid Settings", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), padx=10, anchor="w")
        ctk.CTkLabel(self.scrollable_frame, text="Grid W (m):").pack(padx=10, anchor="w")
        self.e_real_w = ctk.CTkEntry(self.scrollable_frame)
        self.e_real_w.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(self.scrollable_frame, text="Grid H (m):").pack(padx=10, anchor="w")
        self.e_real_h = ctk.CTkEntry(self.scrollable_frame)
        self.e_real_h.pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(self.scrollable_frame, text="Set Grid", command=self.controller.set_grid).pack(fill="x", padx=10, pady=2)

        # crop
        ctk.CTkLabel(self.scrollable_frame, text="Crop Tool", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), padx=10, anchor="w")
        ctk.CTkButton(self.scrollable_frame, text="Toggle Crop Region", command=self.controller.toggle_crop_region).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(self.scrollable_frame, text="Apply Crop", command=self.controller.apply_crop).pack(fill="x", padx=10, pady=2)

        # Danger Zone
        ctk.CTkLabel(self.scrollable_frame, text="Danger Zone Tool", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), padx=10, anchor="w")
        ctk.CTkButton(self.scrollable_frame, text="Toggle Danger Zone", command=self.controller.toggle_danger_region).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(self.scrollable_frame, text="Apply Danger Zone", command=self.controller.apply_danger_overlay).pack(fill="x", padx=10, pady=2)

        # GA
        ctk.CTkLabel(self.scrollable_frame, text="Beacon Placement", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), padx=10, anchor="w")
        ctk.CTkButton(self.scrollable_frame, text="Run Estimation", command=self.controller.run_ga, fg_color="#28a745", hover_color="#218838").pack(fill="x", padx=10, pady=2)

        self.status_label = ctk.CTkLabel(self, text="Open an image to start.", wraplength=230, justify="left")
        self.status_label.grid(row=1, column=0, padx=10, pady=10, sticky="sw")

    def get_grid_entries(self):
        return self.e_real_w.get(), self.e_real_h.get()
    
    def set_status(self, message):
        self.status_label.configure(text=message)

    def clear_grid_entries(self):
        self.e_real_w.delete(0, 'end')
        self.e_real_h.delete(0, 'end')