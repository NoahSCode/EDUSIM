import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import glob
import cv2
import math
import csv
import re

def browse_directory():
    global selected_directory
    filepath = filedialog.askdirectory(title="Select a directory")
    if filepath:
        print("Selected file:", filepath)
        selected_directory = filepath # Save the directory name to the global variable
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, filepath)

        # Update the video files list
        video_files.config(state="normal")  # Set the state to normal before inserting text
        video_files.delete(1.0, tk.END)
        for file in os.listdir(filepath):
            if file.endswith(".mp4") or file.endswith(".avi") or file.endswith(".mkv"):
                video_files.insert(tk.END, file + "\n")
        video_files.config(state="disabled")  # Set the state back to disabled after inserting text



def frame_split():
    # Create a progress bar popup window
    progress_window = tk.Toplevel(root)
    progress_window.title("Splitting Videos")
    progress_label = ttk.Label(progress_window, text="Splitting video into frames...")
    progress_label.pack(padx=10, pady=(10, 0))
    progress = ttk.Progressbar(progress_window, mode="indeterminate", length=300)
    progress.pack(padx=10, pady=(5, 10))
    progress.start(10)
    progress_window.update()

    #check if train/frames path exists, if not, create it
    if os.path.exists(selected_directory + "/train/frames/") == False:
        print("/train/frames folder does not exist. Creating...")
        os.makedirs(selected_directory + "/train/frames/")
    else:
        print("train/frames folder already exists")
    
    #capture video files in chosen directory
    count = 0
    cap = [cv2.VideoCapture(videoFile) for videoFile in glob.glob(os.path.join(selected_directory, "*.mp4"))] # capturing the video from the given path

    #split the frames from each video then output to train/frames folder
    for i in cap:
        print(str(i))
        frameRate = i.get(5)
        while (i.isOpened()):
            frameID = i.get(1)
            ret, frame = i.read()
            if (ret != True):
                break
            if (frameID % math.floor(frameRate) == 0):
                filename = selected_directory + "/train/frames/frame%d.jpg" % (count); count +=1
                cv2.imwrite(filename, frame)
        i.release()
    
    #create the excel file from split frames
    print("Creating excel file for classification...")
    header = ['Image_ID', 'Class']
    data = []
    for i in os.listdir(selected_directory + "/train/frames"):
        data.append(str(i))
    data.sort(key=lambda f: int(re.sub('\D', '', f)))
    data2 = []
    for i in data:
        data2.append([i])
    with open(selected_directory + '/train/frames.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data2)
    print("Done! Please label frames accordingly in 'frames.csv' ")

    
    # Close the progress bar window
    progress.stop()
    progress_window.destroy()

    # Show a new popup window that says "frame split complete"
    complete_window = tk.Toplevel(root)
    complete_window.title("Complete")
    complete_label = ttk.Label(complete_window, text="Frame splitting complete. \nYour training frames are located in /train/frames/ in your selected directory. \nPlease update your excel file located in the /train/ folder with the necessary labels")
    complete_label.pack(padx=10, pady=(10, 0))
    ok_button = ttk.Button(complete_window, text="OK", command=complete_window.destroy)
    ok_button.pack(padx=10, pady=(5, 10))

    # Update the main window
    root.update()

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

# Add description text above the browse button
description_label = ttk.Label(tab_train, text="Select user video folder:")
description_label.pack(padx=10, pady=(10, 0))

# Create a frame to hold the directory entry and browse button
entry_browse_frame = ttk.Frame(tab_train)
entry_browse_frame.pack(padx=10, pady=(5, 10))

# Add an empty text box for manual directory input
directory_entry = ttk.Entry(entry_browse_frame, width=50)
directory_entry.pack(side="left")

# Add a browse button to the "Train Model" tab
browse_button = ttk.Button(entry_browse_frame, text="Browse", command=browse_directory)
browse_button.pack(side="left", padx=(10, 0))

# Create a text box to show a list of video files in the chosen directory
video_files = tk.Text(tab_train, wrap="none", width=50, height=10, state="normal")
video_files.pack(padx=10, pady=(5, 10))

# Add split text description above the split button
split_description_label = ttk.Label(tab_train, text="Split videos into frames and output to a train folder:")
split_description_label.pack(padx=10, pady=(10, 0))

# Add a split button to the "Train Model" tab
split_button = ttk.Button(tab_train, text="Split", command=frame_split)
split_button.pack(padx=10, pady=(5, 10))

# Start the main loop
root.mainloop()