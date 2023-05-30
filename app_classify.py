import tkinter as tk
from tkinter import ttk
from tensorflow import keras
from app_train import *

def load_classify_tab(tab_classify, root):
    def browse_directory():
        global selected_directory
        filepath = filedialog.askdirectory(title="Select a directory")
        if filepath:
            print("Selected file:", filepath)
            selected_directory = filepath # Save the directory name to the global variable
            directory_entry.delete(0, tk.END)
            directory_entry.insert(0, filepath)
    
    def classify():
        model = keras.models.load_model(selected_directory)
    
    # Add description text above the browse button
    description_label = ttk.Label(tab_classify, text="Select trained model directory. This should be inside your train folder:")
    description_label.pack(padx=10, pady=(10, 0))

    # Create a frame to hold the directory entry and browse button
    entry_browse_frame = ttk.Frame(tab_classify)
    entry_browse_frame.pack(padx=10, pady=(5, 10))

    # Add an empty text box for manual directory input
    directory_entry = ttk.Entry(entry_browse_frame, width=50)
    directory_entry.pack(side="left")

    # Add a browse button to the "Train Model" tab
    browse_button = ttk.Button(entry_browse_frame, text="Browse", command=browse_directory)
    browse_button.pack(side="left", padx=(10, 0))

    # Add description text above the classify button
    classify_description_label = ttk.Label(tab_classify, text="Begin classification of areas:")
    classify_description_label.pack(padx=10, pady=(10, 0))

    # Add a browse button to the "Train Model" tab
    classify_button = ttk.Button(tab_classify, text="Classify", command=classify)
    classify_button.pack(padx=10, pady=(5, 10))

    return