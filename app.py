from tkinter import *
from tkinter import filedialog
import os
import glob


def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    files = os.listdir(filename)
    for f in files:
        filelist.insert(0, f)
    
#set main window parameters
root = Tk()
root.title("EDUSIM")
root.geometry('800x600')
folder_path = StringVar()

#browse for recorded videos section
header1 = Label(root, text="Select user video folder:")
header1.grid(row=0, column = 0)
browse = Entry(master=root, textvariable=folder_path)
browse.grid(row=1, column = 0)
browse_videos = Button(text="Browse", command=browse_button)
browse_videos.grid(row=1,column = 2)
filelist = Listbox(root)
filelist.grid(row=2,column=0)
header2 = Label(root, text="")

#start frame split loop
splitframes = Button(text="Split videos", command=frame_split)

mainloop()