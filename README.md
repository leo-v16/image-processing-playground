# 🎨 IIP (Image Processing Playground)

IIP is a **vibe-coded** project that combines the high performance of **C++** with the flexibility of **Python 3**.
It aims to make **image processing experimental, educational, and fun**.

Through an interactive interface, you can apply complex image processing algorithms in **real time**. The project is designed to be **easily extensible**: write your pixel-manipulation logic in C++ and register it in Python to see the results instantly.

---

# 📑 Table of Contents

* [Prerequisites](#-prerequisites)
* [Getting Started](#-getting-started)
* [Windows Quick Start](#-windows-quick-start)
* [Adding Your Own Functions](#-adding-your-own-functions)
* [Project Structure](#-project-structure)
* [Troubleshooting](#-troubleshooting)
* [License](#-license)

---

# 🛠 Prerequisites

Before you begin, ensure your system has the following tools installed:

| Requirement           | Description                                                                                  |
| --------------------- | -------------------------------------------------------------------------------------------- |
| **g++ Compiler**      | Needed to compile the C++ logic into a shared library. *(MinGW-w64 recommended for Windows)* |
| **Python 3.x**        | Main language used for the UI and orchestration                                              |
| **pip**               | Python package manager for installing dependencies                                           |
| **make** *(optional)* | Useful for automated builds                                                                  |

---

# 🚀 Getting Started

## 1️⃣ Build the Shared Library

The core image processing logic is written in **C++**. You must compile it into a shared library so the Python frontend can use it.

Run the following command in your terminal:

```bash
g++ --shared process.cpp -o process.dll
```

---

## 2️⃣ Run the Application

Once `process.dll` is generated, start the interactive interface:

```bash
python launcher.py
```

---

# 🪟 Windows Quick Start

Windows users can automate the build and launch process.

1. Navigate to the `build` folder.
2. Double-click:

```
iip.bat
```

This script will:

* Check if the dependencies Pillow and numpy are installed
* Launch the Python application

---

# 👨‍💻 Adding Your Own Functions

IIP is designed for experimentation. You can easily add your own **filters or transformations**.

## Step 1 — Write the C++ Logic

Open `process.cpp` and add your function.

Your function **must follow this signature**:

```cpp
// Write the code inside extern "C" to prevent name mangling so Python can find the function
// EXPORT is #defined __declspec(dllexport) 
extern "C" {

EXPORT void your_function_name(
    unsigned char* image_data,
    int width,
    int height,
    int channels,
    ...other_params
){
    // Your image processing logic here
    // image_data is a flat array of pixels (usually R, G, B, [A])
}

}
```

---

## Step 2 — Register the Function in Python

Open `core.py` and locate the `FILTER_REGISTRY` dictionary.

Register your function like this:

```python
FILTER_REGISTRY = {
    "Your Operation Name": {
        "func": "your_function_name",
        "category": "Filters",  # Options: Filters, Transforms, ARITHMETIC_NODE
        "params": [
            {
                "name": "param_name",
                "label": "Display Label",
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 10.0
            }
        ]
    }
}
```

### 🧠 Note on `ARITHMETIC_NODE`

`ARITHMETIC_NODE` is a **multi-input node type** that currently requires manual configuration.

Simplified support is planned in future updates.

---

# 📂 Project Structure

```
IIP/
│
├── process.cpp             # C++ source containing image processing algorithms
├── Makefile                # Compilation instructions for process.cpp
├── core.py                 # Bridge between Python and the C++ shared library (ctypes)
├── engine.py               # Graph traversal and processing logic
├── image_utils.py          # Pillow and texture conversion utilities
├── launcher.py             # Entry point / Bootstrap script
├── main.py                 # Main ImageNodeApp class
├── node_manager.py         # Node creation and linking logic
├── persistence.py          # Saving and loading pipelines
├── ui_manager.py           # Dear PyGui window layouts
├── pipelines.json          # Saved user pipeline data
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
│
└── build/
    ├── process.dll         # Your compiled C++ library
    ├── iip.bat             # Windows automation/run script
    ├── ...copy of the python files in the main directory 😅
    └── output/             # Folder for exported processed images
```

---

# 🔍 Troubleshooting

### g++ is not recognized

Ensure your compiler (such as **MinGW-w64**) is added to your system's **PATH environment variable**.

---

### DLL Not Found

Make sure `process.dll` is generated **in the same directory as `launcher.py`**.

---

### Python Errors

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---
