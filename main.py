from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import *
from tkinter import filedialog,messagebox
import os
from os import walk
import sys


#amount of human lifetime spent on this script
#2021/11/01 : 12:30 PM ==> 12:52 PM 
#2021/11/02 : 11:55 PM ==> 12:45 PM
#2021/11/03 : 05:50 PM ==> 7:56  PM 
#2021/11/04 : 08:07 PM ==> 9:45  PM (fixed some file path bugs and added a label to display files names)
#2021/11/07 : 05:12 PM ==> 11:52 PM 
#2021/11/08 : 10:22 AM ==> 11:44 AM
#2021/11/09 : 7:00  PM ==> 09:25 PM
#2021/11/11 : 5:30  PM ==> 7:03  PM (mostly perfect)

#main vars
data = []
dirpath = "" 
dirnames =list()
filenames = list()
res = False

        ################################### BACKEND FUNCTIONS ################################### 

#To create / generate a key in a specific path (whom user will pick)
def create_key():
    messagebox.showinfo("Select key path","please select where you want your key to be saved at")
    key = Fernet.generate_key()
    keyDir = filedialog.askdirectory()
    if len(keyDir) == 0:
        okcancel = messagebox.askokcancel("ERROR!","You didn't pick where you want your key to be at, try again?")
        if okcancel:
            create_key()
        else:
            return
    keyDir = keyDir +"/mykey.key"
    open(keyDir, "wb").write(key)
    print("key was created and saved .")
    return key

#To load a key from a specific path
def load_key():
    messagebox.showinfo("Load key.","Please Select Your Key")

    keyPath = filedialog.askopenfilename(filetypes=(('Key file', '*.key'),)) #import only a file with ".key" extension
    if keyPath == "":
        okcancel = messagebox.askokcancel("Invalid path","You didn't select your key, try again?")
        if okcancel:
            load_key()
        else:
            return

    key = open(keyPath,"rb").read()
    print("this is the key path:",keyPath)
    print("key loaded .")
    return key

#To start encrypting files in the wanted directory
def Encrypt(data,dirpath):
    if len(data) == 0 or dirpath == "":
        messagebox.showerror("ERROR: Folder Was not selected","Please select where's your files first.")
        return
    #check if user wants to encrypt a previouse key found in the same folder
    if "mykey.key" in data:
        yesno = messagebox.askyesno("Alert!", "This folder contains a key, do you want to encrypt it too?")
        if yesno:
            pass
        else:
            data.remove("mykey.key")
            messagebox.showwarning("BE AWARE!","Please save your new key in another folder, or else the old one will get replaced.")

    f = Fernet(create_key())
    for file in data:
        #read data and store it as original
        with open(dirpath+"/"+file,"rb") as original_file:
            original_file = original_file.read()

        #then we encrypt the data using the fernet object that has our key, and store the encrypted data as "encrypted"
        encrypted = f.encrypt(original_file)

        #we'll store the files in a new ones with ".ef" extension
        with open(dirpath+"/"+file+".ef","wb") as encrypted_file:
            encrypted_file.write(encrypted)

        os.remove(dirpath+"/"+file)
        data[data.index(file)] = file+".ef"
    draw_data()
    messagebox.showinfo("Success","Files encrypted successfully!")

#this function will start decrypting files in the selected path using an already generated key
def Decrypt(data,dirpath):
    if len(data) == 0 or dirpath == "":
        messagebox.showerror("ERROR: Folder Was not selected","Please select where's your encrypted files first.")
        return
  

    key = load_key()
    f = Fernet(key)

    #User could be kinda drunk and want to decrypt an un-encrypted files, so we gotta be prepared for it
    #This try-except statement will handle this specific exception out of the loop, so the message won't be repeated foreach file
    try:

        for file in data:
            path = dirpath+"/"+file
            if path.endswith(".key"):
                continue

            #write the decrypted data in a new file
            #In another words, returning data into its first format
            #the if-else statement tho will look after the files names, so we can decrypt the renamed files too
            if path.endswith(".ef"):
                #read the encrypted data and store it as encrypted
                with open(path,"rb") as encrypted_data:
                    encrypted = encrypted_data.read()
                decrypted = f.decrypt(encrypted)

                os.remove(dirpath+"/"+file) #Deleting encrypted files because they're needed no more

                open(path[:-3],'wb').write(decrypted) #Creating file with its original form
            else:
                encrypted = open(path,"rb").read()
                decrypted = f.decrypt(encrypted)
                os.remove(dirpath+"/"+file)
                open(path,'wb').write(decrypted)
    except:
        messagebox.showerror("Wrong action","Normal files can't be decrypted.")
        return
    messagebox.showinfo("Success!","Files decrypted successfully!")            

#using the "openFilesPath" function to read data from user's selected path
#It also grabs the rest valuable data, like files names, sub-folders names and directory path 
def openFilesPath():
    global data
    data = [] #to avoid data overflow
    global dirpath
    global dirnames
    global filenames,res 
    #get the files path using the askdirectory() methode
    filepath = filedialog.askdirectory()

    if filepath == "":
        tryAgain = messagebox.askokcancel("Directory Error.","You didn\'t select a folder, try again?")
        if tryAgain:
            openFilesPath()
        else:
            res = True
            return 
            

    for (dirpath, dirnames, filenames) in walk(filepath):
        data.extend(filenames)
        break
    #to avoid the stupidity of the user, we should keep this 'res' variable false if it ran this far
    res = False
    #check if the directory has at least one file within
    if len(data) == 0 and len(dirnames) == 0 and not res:
        messagebox.showinfo("No files in here.","No files found here :(")
        openFilesPath() 

    #check if the folder has multiple folders within, and if so it'll ask for selecting olny one folder at the time
    elif len(dirnames) > 0:
        messagebox.showinfo("Folder Selection.","Your directory contains multiple folders, please select only one at once")
        return
    
    else:
        print("found this "+"".join(filenames[0:]))
        return

#Will call the openFilesPath function and prints the files names into the UI within a specified label
def draw_data():
    #the following if will check if the user picked a folder or not
    if not res:
        #add files names into the label
        posX = -150 #we need to put this value to make sure that file names will be dislayed from the top left edge
        files_count = 0
        for i in range(len(data)):
            #check if file names can fit into the canvas 
            #the minimum possible length is 9 (because len("mykey.key") == 9 
            if len(data[i]) <= 9:
                file_names = Label(files, text=data[i], height=1, font=("Arial",20), padx=5,pady=10, bg = "black", fg="white", justify=LEFT)    
            else:
                file_names = Label(files, text=data[i][:5]+"..."+data[i][-5:], height=1, font=("Arial",20), padx=5,pady=10, bg = "black", fg="white", justify=LEFT)

            #First case 
            if files_count < 3 :
                posX += 150
                file_names.place(x=posX , y = 2) 
            #Second case 
            elif files_count >= 3 and files_count < 6:
                    posX = posX-300
                    file_names.place(x=posX , y = 60) 
                    posX += 450
            #Third case
            elif files_count >= 6 and files_count < 9:
                    posX = posX - 750
                    file_names.place(x=posX , y = 120) 
                    posX += 900
            #Fourth case
            elif files_count >= 9 :
                posX = posX - 1200
                file_names.place(x=posX, y = 180) 
                posX += 1350
            files_count += 1    
        messagebox.showinfo("Folder info","Your folder was successfully selected.")
    else:
        return

    print("data : \n"+ str(data)+"\n")
    print("dirnames :\n"+str(dirnames)+"\n")
    print("dirpath :\n"+str(dirpath))
    
        ################################### GUI FUNCTIONS ###################################


#GUI:

#The frame and its demensions
HEIGHT = 700
WIDTH = 450

root = Tk()
root.geometry(str(WIDTH)+"x"+str(HEIGHT))
root.resizable(height = FALSE, width = FALSE) 

#Set a canvas and its dimensions within the window
canvas = Canvas(root,height=HEIGHT, width=WIDTH, bg="white")
canvas.pack() 

#Add a frame within the GUI canvas where the user's files names will be displayed
files = Frame(root,bg="#1fa1b3")
files.place(relwidth=1,relheight=0.45, rely = 0.60, relx=0)


#the main UI buttons

#Will make user pick Their specific folder
file_path = Button(root, text="Pick your file(s) folder", padx=2, pady=18, font=("Arial", 23,'bold'),bg="#e36464", command=lambda :[openFilesPath(), draw_data()]) 
file_path.place(x=55,y=55)

#Will make user pick where They want to save Their encryption key
#Also will encrypt the first files found within that folder
Ecrypt_btn = Button(root, text="Ecrypt me", padx=9, pady=14, font=("Arial", 17,'bold',UNDERLINE),bg="#e36464",fg="yellow", command=lambda : Encrypt(data,dirpath)) 
Ecrypt_btn.place(x=2,y=190)

#Will Make user import their key
#Will decrypt !ONLY! the files who have got encrypted with this app
#Won't take action on an existend key in the same path
decrypt_btn = Button(root, text="Decrypt me", padx=9, pady=14, font=("Arial", 17,'bold',UNDERLINE),bg="#e36464",fg="yellow", command=lambda:Decrypt(data,dirpath))
decrypt_btn.place(x=287,y=190)

#Keep the app running
root.mainloop()