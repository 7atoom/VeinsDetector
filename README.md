# Vein Detector

A Python-based application for detecting and analyzing veins in hand images using computer vision techniques.

## Description

The Vein Detector is a sophisticated tool that uses computer vision and image processing techniques to detect and analyze veins in hand images. It provides various features including:

- Real-time vein detection
- Multiple visualization modes (Original, Enhanced, Vein Mask, Final Result)
- Detailed vein statistics
- User-friendly GUI interface
- Image saving capabilities

## Features

- **Multiple View Modes:**
  - Original Image View
  - Enhanced Image View
  - Vein Mask View
  - Final Result View
  
- **Statistics Analysis:**
  - Total number of veins detected
  - Vein areas and perimeters
  - Largest vein measurements
  - Vein-to-hand ratio analysis

## Installation

### Option 1: Running the Executable (Windows)

1. Download the executable from the `build/veinDetect` directory
2. Double-click `veinDetect.exe` to run the application
3. No additional installation required

### Option 2: Running from Source

1. Clone the repository:
```bash
git clone https://github.com/7atoom/VeinsDetector.git
cd VeinsDetector
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python veinDetect.py
```

## Usage

1. Launch the application using either the executable or Python script
2. Click "Import Image" to load a hand image
3. Click "Detect Veins" to process the image
4. Use the view options to switch between different visualization modes
5. View statistics in the right panel
6. Save results using the "Save Result" button

## System Requirements

### For Executable:
- Windows Operating System
- No additional dependencies required

### For Source Code:
- Python 3.8 or higher
- OpenCV
- NumPy
- Pillow (PIL)
- Tkinter (usually comes with Python)

## Technical Details

The application uses several image processing techniques:
- HSV color space conversion for skin detection
- Adaptive thresholding for vein detection
- Morphological operations for noise reduction
- Contour detection and analysis
- CLAHE (Contrast Limited Adaptive Histogram Equalization) for image enhancement

## License

This project is open source and available under the MIT License.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.

## Author

7atoom

## Acknowledgments

Special thanks to the OpenCV community for providing the computer vision tools that made this project possible.
