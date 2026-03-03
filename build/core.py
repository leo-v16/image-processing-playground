import ctypes
import os

PIPELINES_FILE = "pipelines.json"
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 800
MAX_DISPLAY_WIDTH = 350

try:
    # Use absolute path for DLL if possible or ensure it's in the working directory
    dll_path = os.path.abspath("process.dll")
    process_lib = ctypes.CDLL(dll_path)
    
    # 1. Grayscale
    process_lib.gray_scale.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.gray_scale.restype = None
    
    # 2. Blur (Updated with radius)
    process_lib.blured.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.blured.restype = None

    # 3. Arithmetic
    process_lib.add_images.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.add_images.restype = None
    
    process_lib.sub_images.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.sub_images.restype = None

    # 4. Filters & Transforms
    # Fixed multiply signature: added missing channel (int) argument
    process_lib.multiply.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float]
    process_lib.multiply.restype = None

    process_lib.inverted.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.inverted.restype = None

    process_lib.threshold.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ubyte]
    process_lib.threshold.restype = None

    process_lib.log_transform.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.log_transform.restype = None

    process_lib.power_transform.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double]
    process_lib.power_transform.restype = None

    # radius-based filters
    process_lib.max_filter.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.max_filter.restype = None

    process_lib.min_filter.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.min_filter.restype = None

    process_lib.median_filter.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.median_filter.restype = None

    process_lib.mode_filter.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.mode_filter.restype = None

    # New Derivative Filters
    process_lib.first_derivative_x.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.first_derivative_x.restype = None

    process_lib.first_derivative_y.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.first_derivative_y.restype = None

    process_lib.second_derivative_x.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.second_derivative_x.restype = None

    process_lib.second_derivative_y.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.second_derivative_y.restype = None
    
    DLL_LOADED = True
    print("[INFO] process.dll loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load process.dll: {e}")
    DLL_LOADED = False
    process_lib = None
