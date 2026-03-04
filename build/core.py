import ctypes
import os

PIPELINES_FILE = "pipelines.json"
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 800
MAX_DISPLAY_WIDTH = 350

# --- THE SINGLE SOURCE OF TRUTH ---
# To add a new filter: Just add its C++ function name and parameters here.
FILTER_REGISTRY = {
    "Grayscale": {"func": "gray_scale", "category": "Filters", "params": []},
    "Inverted": {"func": "inverted", "category": "Filters", "params": []},
    "Blur Filter": {
        "func": "blured", "category": "Filters", 
        "params": [{"name": "radius", "label": "Radius", "type": "int", "default": 1, "min": 1, "max": 20}]
    },
    "Max Filter": {
        "func": "max_filter", "category": "Filters", 
        "params": [{"name": "radius", "label": "Radius", "type": "int", "default": 1, "min": 1, "max": 20}]
    },
    "Min Filter": {
        "func": "min_filter", "category": "Filters", 
        "params": [{"name": "radius", "label": "Radius", "type": "int", "default": 1, "min": 1, "max": 20}]
    },
    "Median Filter": {
        "func": "median_filter", "category": "Filters", 
        "params": [{"name": "radius", "label": "Radius", "type": "int", "default": 1, "min": 1, "max": 20}]
    },
    "Mode Filter": {
        "func": "mode_filter", "category": "Filters", 
        "params": [{"name": "radius", "label": "Radius", "type": "int", "default": 1, "min": 1, "max": 20}]
    },
    "1st X Derivative": {"func": "first_derivative_x", "category": "Filters", "params": []},
    "1st Y Derivative": {"func": "first_derivative_y", "category": "Filters", "params": []},
    "2nd X Derivative": {"func": "second_derivative_x", "category": "Filters", "params": []},
    "2nd Y Derivative": {"func": "second_derivative_y", "category": "Filters", "params": []},
    "Threshold": {
        "func": "threshold", "category": "Transforms", 
        "params": [{"name": "threshold", "label": "Val", "type": "int", "default": 128, "min": 0, "max": 255}]
    },
    "Log Transform": {
        "func": "log_transform", "category": "Transforms", 
        "params": [{"name": "c", "label": "C", "type": "int", "default": 30}]
    },
    "Power Transform": {
        "func": "power_transform", "category": "Transforms", 
        "params": [
            {"name": "c", "label": "C", "type": "int", "default": 1},
            {"name": "gamma", "label": "G", "type": "float", "default": 1.2}
        ]
    },
    "Multiply": {
        "func": "multiply", "category": "Transforms", 
        "params": [{"name": "factor", "label": "Factor", "type": "float", "default": 1.0, "min": 0.0, "max": 10.0}]
    },
    "Bit Plane Slice": {
        "func": "bitslice", "category": "Transforms",
        "params": [{"name": "bit_place", "label": "Bit Place", "type": "int", "default": 7, "min": 1, "max": 7}]
    }
}

ARITHMETIC_NODES = ["Add Images", "Sub Images"]

try:
    dll_path = os.path.abspath("process.dll")
    process_lib = ctypes.CDLL(dll_path)
    
    # Standard setup for all filters in registry
    for name, info in FILTER_REGISTRY.items():
        func = getattr(process_lib, info["func"])
        # Base arguments: data, width, height, channel
        argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
        
        # Add dynamic parameters
        for p in info["params"]:
            if p["type"] == "int": argtypes.append(ctypes.c_int)
            elif p["type"] == "float": argtypes.append(ctypes.c_float)
            elif p["type"] == "double": argtypes.append(ctypes.c_double)
            elif p["type"] == "uchar": argtypes.append(ctypes.c_ubyte)
            
        func.argtypes = argtypes
        func.restype = None

    # Special case: Arithmetic (needs two pointers)
    process_lib.add_images.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    process_lib.sub_images.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    DLL_LOADED = True
    print("[INFO] DLL loaded and registry initialized.")
except Exception as e:
    print(f"[ERROR] Registry init failed: {e}")
    DLL_LOADED = False
    process_lib = None
