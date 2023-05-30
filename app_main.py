import tkinter as tk
from tkinter import ttk
import app_train
import app_classify
import app_analyze

# Create the main window
root = tk.Tk()
root.title("EDUSIM")

# Create a tab control
tab_control = ttk.Notebook(root)

# Create the three tabs
tab_train = ttk.Frame(tab_control)
tab_classify = ttk.Frame(tab_control)
tab_analyze = ttk.Frame(tab_control)

# Add the tabs to the tab control
tab_control.add(tab_train, text="Train Model")
tab_control.add(tab_classify, text="Classify")
tab_control.add(tab_analyze, text="Analyze")

# Pack the tab control
tab_control.pack(expand=1, fill="both")

# Load the contents of each tab
app_train.load_train_tab(tab_train, root)
app_classify.load_classify_tab(tab_classify, root)
app_analyze.load_analyze_tab(tab_analyze, root)

# Start the main loop
root.mainloop()