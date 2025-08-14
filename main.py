import customtkinter as ctk
from AppState import AppState
from Canvas import ImageCanvasView
from ControlPanel import ControlPanel
from Controller import AppController
from ImageProcessor import ImageProcessor
from Genetic import GeneticAlgorithm 

class App(ctk.CTk):
    """The main application class that orchestrates the components."""
    def __init__(self):
        super().__init__()
        self.title("Beacon Grid Editor")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 1. Create the core non-UI components
        app_state = AppState()
        image_processor = ImageProcessor()
        ga_solver = GeneticAlgorithm() # Using your provided GA class
        controller = AppController(app_state, image_processor, ga_solver)
        self.bind("<Escape>", controller.cancel_current_mode)

        # 2. Configure the main window grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=250)

        # 3. Create the UI components (Views)
        canvas_view = ImageCanvasView(self, app_state)
        canvas_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        control_panel = ControlPanel(self, controller)
        control_panel.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)

        # 4. Link the controller to the views so it can call their methods
        controller.canvas_view = canvas_view
        controller.control_panel = control_panel

if __name__ == "__main__":
    app = App()
    app.mainloop()