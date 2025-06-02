import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os
from datetime import datetime
import time
import threading

# ====== PARAMETERS ======
SKIN_LOWER = np.array([0, 20, 70], dtype=np.uint8)
SKIN_UPPER = np.array([20, 255, 255], dtype=np.uint8)
AREA_BORDER_RATIO = 0.15  # Max area ratio for a contour to be considered a vein
EDGE_MARGIN = 2           # Margin in pixels to consider a contour touching the edge
MASK_EDGE_MARGIN = 8      # Margin in pixels to consider a contour close to the hand mask edge
ALPHA = 0.6               # Overlay blending factor

class SplashScreen:
    def __init__(self, parent):
        self.parent = parent
        
        # Create splash window
        self.splash = tk.Toplevel(parent)
        self.splash.overrideredirect(True)
        
        # Get screen dimensions
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        
        # Set splash window size and position
        splash_width = 400
        splash_height = 300
        x = (screen_width - splash_width) // 2
        y = (screen_height - splash_height) // 2
        self.splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")
        
        # Configure splash window
        self.splash.configure(bg='#2c3e50')
        
        # Create splash content
        self.create_splash_content()
        
    def create_splash_content(self):
        # Title
        title_label = tk.Label(
            self.splash,
            text="Vein Detector",
            font=('Helvetica', 24, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Loading text
        self.loading_label = tk.Label(
            self.splash,
            text="Loading...",
            font=('Helvetica', 12),
            fg='white',
            bg='#2c3e50'
        )
        self.loading_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.splash,
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=20)
        
        # Version info
        version_label = tk.Label(
            self.splash,
            text="Version 1.0",
            font=('Helvetica', 8),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        version_label.pack(side=tk.BOTTOM, pady=10)
        
    def update_progress(self, value):
        self.progress['value'] = value
        self.splash.update()
        
    def destroy(self):
        self.splash.destroy()

class LoadingOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.overlay = None
        self.is_visible = False
        
    def show(self, message="Processing..."):
        if self.overlay is None:
            self.overlay = tk.Toplevel(self.parent)
            self.overlay.overrideredirect(True)
            self.overlay.attributes('-alpha', 0.8)
            self.overlay.configure(bg='#2c3e50')
            
            # Get parent window position and size
            x = self.parent.winfo_x()
            y = self.parent.winfo_y()
            width = self.parent.winfo_width()
            height = self.parent.winfo_height()
            
            self.overlay.geometry(f"{width}x{height}+{x}+{y}")
            
            # Create loading content
            frame = tk.Frame(self.overlay, bg='#2c3e50')
            frame.place(relx=0.5, rely=0.5, anchor='center')
            
            # Loading text
            self.loading_label = tk.Label(
                frame,
                text=message,
                font=('Helvetica', 12),
                fg='white',
                bg='#2c3e50'
            )
            self.loading_label.pack(pady=10)
            
            # Progress bar
            self.progress = ttk.Progressbar(
                frame,
                length=200,
                mode='indeterminate'
            )
            self.progress.pack(pady=10)
            
        self.overlay.deiconify()
        self.progress.start(10)
        self.is_visible = True
        
    def hide(self):
        if self.overlay and self.is_visible:
            self.progress.stop()
            self.overlay.withdraw()
            self.is_visible = False

class VeinDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vein Detector")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self.root)
        
        # Variables
        self.original_image = None
        self.processed_image = None
        self.enhanced_image = None
        self.vein_mask = None
        self.vein_stats = {}
        self.current_view = tk.StringVar(value="final")
        
        # Show splash screen
        self.splash = SplashScreen(self.root)
        self.root.withdraw()  # Hide main window
        
        # Simulate loading process
        self.simulate_loading()
        
    def simulate_loading(self):
        def loading_task():
            for i in range(101):
                time.sleep(0.02)
                self.splash.update_progress(i)
            self.splash.destroy()
            self.root.deiconify()  # Show main window
            self.setup_gui()
            
        threading.Thread(target=loading_task, daemon=True).start()

    def setup_gui(self):
        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for controls
        left_panel = ttk.LabelFrame(main_container, text="Controls", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Control buttons with icons and better styling
        style = ttk.Style()
        style.configure('Custom.TButton', padding=10)
        
        ttk.Button(left_panel, text="📂 Import Image", 
                  command=self.import_image, style='Custom.TButton').pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="🔍 Detect Veins", 
                  command=self.detect_veins, style='Custom.TButton').pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="💾 Save Result", 
                  command=self.save_result, style='Custom.TButton').pack(fill=tk.X, pady=5)
        
        # View selection
        view_frame = ttk.LabelFrame(left_panel, text="View Options", padding="5")
        view_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(view_frame, text="Original", variable=self.current_view, 
                       value="original", command=self.update_view).pack(anchor=tk.W)
        ttk.Radiobutton(view_frame, text="Enhanced", variable=self.current_view, 
                       value="enhanced", command=self.update_view).pack(anchor=tk.W)
        ttk.Radiobutton(view_frame, text="Vein Mask", variable=self.current_view, 
                       value="veinmask", command=self.update_view).pack(anchor=tk.W)
        ttk.Radiobutton(view_frame, text="Final Result", variable=self.current_view, 
                       value="final", command=self.update_view).pack(anchor=tk.W)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(left_panel, textvariable=self.status_var, 
                                  relief=tk.SUNKEN, padding=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Create center panel for image display
        center_panel = ttk.LabelFrame(main_container, text="Image View", padding="10")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Image display with scrollbars
        self.canvas_frame = ttk.Frame(center_panel)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create right panel for statistics
        right_panel = ttk.LabelFrame(main_container, text="Statistics", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Statistics display with better formatting
        self.stats_text = tk.Text(right_panel, height=20, width=30, 
                                 font=('Consolas', 10), wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Add timestamp to statistics
        self.timestamp_label = ttk.Label(right_panel, text="")
        self.timestamp_label.pack(pady=5)
        
    def import_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.status_var.set(f"Loading image: {os.path.basename(file_path)}")
            self.original_image = cv2.imread(file_path)
            self.current_view.set("original")  # Default to original view
            self.display_image(self.original_image)
            self.status_var.set("Image loaded successfully")
            
    def display_image(self, cv_image):
        if cv_image is None:
            return
            
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image)
        
        # Resize image to fit the window while maintaining aspect ratio
        display_size = (800, 600)
        pil_image.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(pil_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
    def update_view(self):
        if self.original_image is None:
            return
        view = self.current_view.get()
        if view == "original":
            self.display_image(self.original_image)
        elif view == "enhanced" and self.enhanced_image is not None:
            self.display_image(self.enhanced_image)
        elif view == "final" and self.vein_mask is not None:
            # Show the black-and-white vein mask as the final result
            mask_rgb = cv2.cvtColor(self.vein_mask, cv2.COLOR_GRAY2BGR)
            self.display_image(mask_rgb)
        elif view == "veinmask" and self.processed_image is not None:
            # Optionally, show the overlay in the 'Vein Mask' view
            self.display_image(self.processed_image)
            
    def detect_veins(self):
        if self.original_image is None:
            self.status_var.set("Please import an image first")
            return
            
        self.loading_overlay.show("Detecting veins...")
        self.root.update()
        
        try:
            # Process image
            hand_mask = get_hand_mask(self.original_image)
            self.vein_mask, enhanced = detect_veins(self.original_image, hand_mask)
            self.enhanced_image = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            self.processed_image = draw_veins_on_image(self.original_image, self.vein_mask, hand_mask)
            
            # Calculate vein statistics
            self.calculate_vein_stats(self.vein_mask)
            
            # Update display
            self.current_view.set("final")  # Set view to final result
            self.update_view()
            self.update_stats_display()
            self.status_var.set("Vein detection completed")
            
        except Exception as e:
            self.status_var.set(f"Error during processing: {str(e)}")
            print(f"Error: {str(e)}")
        finally:
            self.loading_overlay.hide()
        
    def calculate_vein_stats(self, vein_mask):
        contours, _ = cv2.findContours(vein_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            self.vein_stats = {"No veins detected": 0}
            return
        areas = [cv2.contourArea(cnt) for cnt in contours]
        perimeters = [cv2.arcLength(cnt, True) for cnt in contours]
        largest_vein_idx = np.argmax(areas)
        largest_vein = contours[largest_vein_idx]
        largest_vein_perimeter = perimeters[largest_vein_idx]
        # Calculate centroid of largest vein
        M = cv2.moments(largest_vein)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = 0, 0
        # Calculate hand area for percentage
        hand_mask = get_hand_mask(self.original_image)
        self.hand_area = np.count_nonzero(hand_mask)
        self.vein_stats = {
            "Total veins detected": len(contours),
            "Largest vein area": max(areas),
            "Average vein area": sum(areas) / len(areas),
            "Total vein area": sum(areas),
            "Longest vein perimeter": max(perimeters),
            "Average vein perimeter": sum(perimeters) / len(perimeters),
            "Largest vein perimeter": largest_vein_perimeter,
            "Largest vein centroid": (cx, cy)
        }
        
    def update_stats_display(self):
        self.stats_text.delete(1.0, tk.END)
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.config(text=f"Analysis Time: {timestamp}")
        # Format and display statistics
        if not self.vein_stats or "No veins detected" in self.vein_stats:
            self.stats_text.insert(tk.END, "No veins detected.\n")
            return
        # Improved stats formatting
        self.stats_text.insert(tk.END, f"Total veins detected: {self.vein_stats['Total veins detected']}\n")
        self.stats_text.insert(tk.END, f"Largest vein area: {self.vein_stats['Largest vein area']:.2f} px²\n")
        self.stats_text.insert(tk.END, f"Largest vein perimeter: {self.vein_stats['Largest vein perimeter']:.2f} px\n")
        self.stats_text.insert(tk.END, f"Average vein area: {self.vein_stats['Average vein area']:.2f} px²\n")
        self.stats_text.insert(tk.END, f"Average vein perimeter: {self.vein_stats['Average vein perimeter']:.2f} px\n")
        self.stats_text.insert(tk.END, f"Total vein area: {self.vein_stats['Total vein area']:.2f} px²\n")
        # Add hand area and percentage if available
        if hasattr(self, 'hand_area') and self.hand_area > 0:
            percent = 100 * self.vein_stats['Total vein area'] / self.hand_area
            self.stats_text.insert(tk.END, f"Total vein area / hand: {percent:.2f}%\n")
        # Add centroid of largest vein if available
        if 'Largest vein centroid' in self.vein_stats:
            cx, cy = self.vein_stats['Largest vein centroid']
            self.stats_text.insert(tk.END, f"Largest vein centroid: ({cx}, {cy})\n")
        
    def save_result(self):
        if self.current_view.get() == "final" and self.vein_mask is not None:
            # Save the black-and-white vein mask
            img_to_save = self.vein_mask
            is_mask = True
        elif self.current_view.get() == "veinmask" and self.processed_image is not None:
            # Save the overlay if in 'Vein Mask' view
            img_to_save = self.processed_image
            is_mask = False
        elif self.current_view.get() == "enhanced" and self.enhanced_image is not None:
            img_to_save = cv2.cvtColor(self.enhanced_image, cv2.COLOR_BGR2RGB)
            is_mask = False
        elif self.current_view.get() == "original" and self.original_image is not None:
            img_to_save = self.original_image
            is_mask = False
        else:
            self.status_var.set("No image to save")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"vein_detection_{timestamp}.png"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            if is_mask:
                cv2.imwrite(file_path, img_to_save)
            else:
                cv2.imwrite(file_path, cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR) if len(img_to_save.shape) == 3 else img_to_save)
            self.status_var.set(f"Image saved: {os.path.basename(file_path)}")

# ====== FUNCTIONS ======
def get_hand_mask(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, SKIN_LOWER, SKIN_UPPER)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.medianBlur(mask, 5)
    # Find the largest contour (assume it's the hand)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.zeros_like(mask)
    hand_contour = max(contours, key=cv2.contourArea)
    hand_mask = np.zeros_like(mask)
    cv2.drawContours(hand_mask, [hand_contour], -1, 255, -1)
    hand_mask = cv2.erode(hand_mask, np.ones((MASK_EDGE_MARGIN, MASK_EDGE_MARGIN), np.uint8), iterations=1)
    return hand_mask

def detect_veins(image, hand_mask):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 10)
    vein_mask = cv2.bitwise_and(thresh, thresh, mask=hand_mask)
    kernel = np.ones((3, 3), np.uint8)
    morph = cv2.morphologyEx(vein_mask, cv2.MORPH_CLOSE, kernel)
    return morph, enhanced

def draw_veins_on_image(original, vein_mask, hand_mask):
    contours, _ = cv2.findContours(vein_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    overlay = original.copy()
    height, width = vein_mask.shape
    # Find hand mask edge for border check
    hand_edges = cv2.Canny(hand_mask, 100, 200)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > AREA_BORDER_RATIO * (height * width):
            continue
        # Check if contour is close to hand mask edge
        mask_cnt = np.zeros_like(hand_mask)
        cv2.drawContours(mask_cnt, [cnt], -1, 255, 2)
        # Dilate hand edge for margin
        hand_edges_dilated = cv2.dilate(hand_edges, np.ones((MASK_EDGE_MARGIN, MASK_EDGE_MARGIN), np.uint8), iterations=1)
        if np.any(cv2.bitwise_and(mask_cnt, hand_edges_dilated)):
            continue
        cv2.drawContours(overlay, [cnt], -1, (0, 255, 0), 2, lineType=cv2.LINE_AA)
    output = cv2.addWeighted(overlay, ALPHA, original, 1 - ALPHA, 0)
    return output

# ====== MAIN SCRIPT ======
if __name__ == "__main__":
    root = tk.Tk()
    app = VeinDetectorGUI(root)
    root.mainloop()
