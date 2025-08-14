# Ochimamo
This is a repository for an application that defines danger areas in high-place work sites. This application is part of the Ochimamo Project-Based Learning (PBL) initiative.

**日本語のREADME**
> <a href="./README/README_jp.md">日本語のREADME</a>"

## 1. Overview
The Beacon Grid Editor is a GUI application for optimally placing devices, such as BLE beacons, on a rooftop floor plan image.

Users can specify danger zones and use a genetic algorithm (GA) to automatically calculate a beacon placement plan that maximizes coverage. The final placement plan can be exported in JSON format for use with an M5Stack device.

## 2. Key Features
Image Loading: Load and display floor plan images (PNG, JPG) on the canvas.

- Image Editing:
    - Crop: Cut out and use only the necessary parts of the image.
    - Danger Zone Configuration: Specify multiple rectangular areas where beacons should not be placed.
- Grid Settings: Set the image scale to actual dimensions (in meters) to generate a virtual grid of potential placement points.
- Optimal Beacon Placement: Utilizes a genetic algorithm (GA) to calculate beacon placements that maximize coverage while avoiding danger zones.
- Settings Export: Save the calculated beacon coordinates, grid information, dimensions, and more as a JSON file.

## 3. Requirements
To run this application, the following Python libraries are required:
- `customtkinter`
- `Pillow`
- `opencv-python`
- `numpy`

## 4. Installation
Install the required libraries by running the following command:
```bash
pip install customtkinter Pillow opencv-python numpy
```

## 5. Usage
1. Clone or download the repository and navigate to the project directory in your terminal.

2. Launch the application with the following command:
```bash
python main.py
```
3. Basic Workflow:

    1. Open Image: Open a floor plan image file.

    2. Set Grid: Enter the actual width and height of the image in meters into the Grid W (m) and Grid H (m) fields, then press the Set Grid button.

    3. Toggle Danger Zone: Displays a red rectangle for specifying a danger zone (an area where you do not want to place beacons). The rectangle can be moved and resized by dragging.

    4. Apply Danger Zone: Applies the rectangle's location as a danger zone mask. This operation can be repeated multiple times.

    5. Run Estimation: Once all settings are configured, press this button to execute the optimal placement calculation using the genetic algorithm. When the calculation is complete, the beacon placement locations will be indicated by blue circles.

    6. Export JSON: Save the final placement information as a JSON file.

## 6. File Structure
This project is divided into the following files based on the Model-View-Controller (MVC) architectural pattern.

- `main.py`: The main file that launches the entire application. It initializes each component (Model, View, Controller) and builds the window.

- `AppState.py`: Model: Manages the application's state (loaded image, zoom level, various coordinates, etc.) in a centralized way.

- `Controller.py`: Controller: Handles the application's core logic. It processes actions from button presses and executes algorithms.

- `ControlPanel.py`: View: Builds the UI for the control panel on the right side of the window.

- `Canvas.py`: View: Builds the main canvas UI that displays the image and accepts mouse interactions (zoom, drag, etc.).

- `ImageProcessor.py`: A class that contains helper functions for image processing (such as automatic detection of danger zones and creating building masks).

- `Genetic.py`: A class that implements the genetic algorithm for calculating the optimal placement of beacons.