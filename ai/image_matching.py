import os
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def calculate_image_similarity(image_path1, image_path2):
    """
    Computes image similarity between two uploaded item photos.
    Returns float between 0.0 and 1.0, or None if images are unavailable/invalid.
    """
    if not image_path1 or not image_path2:
        return None
        
    if not os.path.exists(image_path1) or not os.path.exists(image_path2):
        return None

    # OpenCV HSV Color Histogram & Feature Matcher
    if OPENCV_AVAILABLE:
        try:
            img1 = cv2.imread(image_path1)
            img2 = cv2.imread(image_path2)
            
            if img1 is None or img2 is None:
                return None

            # Resize to standard analysis size
            img1 = cv2.resize(img1, (256, 256))
            img2 = cv2.resize(img2, (256, 256))

            # Convert to HSV color space for lighting-invariant color matching
            hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
            hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

            # Compute Hue-Saturation histogram
            hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 60], [0, 180, 0, 256])
            hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 60], [0, 180, 0, 256])

            # Normalize histograms
            cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

            # Calculate histogram correlation
            hist_sim = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            hist_sim = max(0.0, float(hist_sim))

            return hist_sim
        except Exception as e:
            print(f"[AI Image Matching Error]: {e}")

    # Fallback using Pillow average RGB distance
    if PIL_AVAILABLE:
        try:
            p1 = Image.open(image_path1).convert('RGB').resize((64, 64))
            p2 = Image.open(image_path2).convert('RGB').resize((64, 64))
            
            arr1 = np.array(p1, dtype=np.float32)
            arr2 = np.array(p2, dtype=np.float32)
            
            diff = np.mean(np.abs(arr1 - arr2))
            sim = max(0.0, 1.0 - (diff / 255.0))
            return float(sim)
        except Exception as e:
            print(f"[Pillow Fallback Error]: {e}")

    return None
