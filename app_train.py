import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import glob
import cv2
import math
import csv
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50
from keras.utils import np_utils
from skimage.transform import resize
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense, InputLayer, Dropout
from tensorflow.keras.models import Sequential

def load_train_tab(tab_train, root):
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
    
    def begin_training():
        # Create a progress bar popup window
        progress_window = tk.Toplevel(root)
        progress_window.title("Splitting Videos")
        progress_label = ttk.Label(progress_window, text="Training model...")
        progress_label.pack(padx=10, pady=(10, 0))
        progress = ttk.Progressbar(progress_window, mode="indeterminate", length=300)
        progress.pack(padx=10, pady=(5, 10))
        progress.start(10)
        progress_window.update()
        
        #load training excel file
        data = pd.read_csv(selected_directory + '/train/frames.csv')

        #count number of areas created in excel file:
        cnt = 0
        visited = []
        for i in range (0, len(data['Class'])):
            if data['Class'][i] not in visited:
                visited.append(data['Class'][i])
                
                cnt+=1
        X = [ ]     # creating an empty array
        for img_name in data.Image_ID:
            img = plt.imread(selected_directory + '/train/frames/' + img_name)
            X.append(img)  # storing each image in array X
        X = np.array(X)
        y = data.Class
        dummy_y = np_utils.to_categorical(y)
        image = []
        for i in range(0,X.shape[0]):
            a = resize(X[i], preserve_range=True, output_shape=(224,224)).astype(int)      # reshaping to 224*224*3
            image.append(a)
        X = np.array(image)
        X = preprocess_input(X, mode='caffe')
        X_train, X_valid, y_train, y_valid = train_test_split(X, dummy_y, test_size=0.3, random_state=42)
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3)) 
        X_train = base_model.predict(X_train)
        X_valid = base_model.predict(X_valid)
        X_train.shape, X_valid.shape
        X_train = X_train.reshape(X_train.shape[0], 7*7*2048)      # converting to 1-D
        X_valid = X_valid.reshape(X_valid.shape[0], 7*7*2048)
        train = X_train/X_train.max()      # centering the data
        X_valid = X_valid/X_train.max()
        model = Sequential()
        model.add(InputLayer((7*7*2048,)))    # input layer
        model.add(Dense(units=2048, activation='sigmoid'))   # hidden layer
        model.add(Dropout(0.5))      # adding dropout
        model.add(Dense(units=1024, activation='sigmoid'))    # hidden layer
        model.add(Dropout(0.5))      # adding dropout
        model.add(Dense(units=512, activation='sigmoid'))    # hidden layer
        model.add(Dropout(0.5))      # adding dropout
        model.add(Dense(units=256, activation='sigmoid'))    # hidden layer
        model.add(Dropout(0.5))      # adding dropout
        model.add(Dense(cnt, activation='softmax'))            # output layer
        model.summary()
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(train, y_train, epochs=15, validation_data=(X_valid, y_valid))
        model.save(selected_directory + '/train/model')
        # Close the progress bar window
        progress.stop()
        progress_window.destroy()

        # Show a new popup window that says "model training complete"
        complete_window = tk.Toplevel(root)
        complete_window.title("Complete")
        complete_label = ttk.Label(complete_window, text="Model training complete. Model has been saved to /train/model/.\nYou may begin classification of new videos in the classify tab")
        complete_label.pack(padx=10, pady=(10, 0))
        ok_button = ttk.Button(complete_window, text="OK", command=complete_window.destroy)
        ok_button.pack(padx=10, pady=(5, 10))

        # Update the main window
        root.update()

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

    #Add train text description above train button
    train_description_label = ttk.Label(tab_train, text="Begin training model (please make sure your excel file is properly filled out)")
    train_description_label.pack(padx=10, pady=(10, 0))

    # Add a train button to the "Train Model" tab
    train_button = ttk.Button(tab_train, text="Train", command=begin_training)
    train_button.pack(padx=10, pady=(5, 10))
