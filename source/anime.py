import csv
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os

# import json
# import urllib.request
# import discordpy > wanted to make it communicate to discord but got too lazy

# DEPENDENCIES: 
# PIL, requests 
# install with:
# pip install pillow requests (on windows, if you're on mac idk if this code even works.)
# made on python 3.12.5

# code made by kodealt on github. @a_persan on discord, if you have any questions.
# version 1 (current) made on feb 22, 2025

# feel free to modify and share code, as long as you credit me. or dont, i cant seem to care. its open source anyways. 
# crediting me would be appreciated

# NOT OPTIMIZED AS OF DATE OF CREATION.

#API URL:
#f"https://api.jikan.moe/v4/anime?q={anime}&limit=1"

#HEADERS : NAME, VALUE, TAGS
fieldnamez = ["NAME", "VALUE", "TAGS", "INDEX"]
zero = 0

#GENRE JSON
response = requests.get(f"https://api.jikan.moe/v4/genres/anime")
response.raise_for_status()
results = response.json().get("data",[])
genreJSON = {genre["mal_id"]: genre["name"] for genre in results}

#some comments are just lines of code that i was too lazy to delete. delete them if you want to

root = tk.Tk()
root.title("watch later list")
width = int(root.winfo_screenwidth()*0.75)
height = int(root.winfo_screenheight()*0.75)
root.geometry(f"{width}x{height}")
root.configure(bg="#1C1C1C")
root.wm_attributes('-alpha', 1)

#functions concerning the gui {
#onhover, the one with lookup imbedded
def onHover(widget, text=None, cover=None, waittime=150, wraplength=100, create = True):
    """a much needed hover window, for a frame, container, or whatever.
        original code from: https://stackoverflow.com/a/36221216/
        translated to a function by me. discord username: @a_persan if u have any questions. or just wanna chat
        yes, there is a hover library, but i just found out about that after i wrote this comment.
        if you wanna use that instead: from idlelib.tooltip import Hovertip
        idfk how to use it, but it's there ¯\_ (ツ)_/¯ 
        
        widget: the widget or label you want to hover over
        text: the text you want to display
        cover: the image you want to display
        waittime: how long to wait before displaying the hover window (in ms) default is 250ms
        wraplength: how long the text can be before it wraps to the next line default is 100px

        just keep in mind the jikan api has rate limits, which being 3 per seconds and 60 per min
    """
    
    #first instance of mouse hovering over the "widget"
    def enter(event=None):
        #nonlocal text, cover, title, score, genres, cover
        nonlocal fetching, text
        schedule()
        fetching = widget.after(waittime, lambda: fetch(text))
        #title, score, genres, cover, duration, episodes, year = lookup(text)
        #cover.show()
        #text = f"{title} : {score}/10\ngenres: {', '.join(genres)}"
        #infoUpdate(title, score, genres, cover, duration, episodes, year)

    def fetch(text):
        nonlocal fetching
        if fetching is None:
            return
        title, score, genres, cover, duration, episodes, year = lookup(text)
        infoUpdate(title, score, genres, cover, duration, episodes, year)
        fetching = None
    
    #when it does leave
    def leave(event=None):
        unschedule()
        hide()
    
    #create a "id" or what it really is is just another window
    def schedule():
        nonlocal hoverID
        unschedule()
        #hoverID = widget.after(waittime, showHover)

    #remove the "id" or window if there was one
    def unschedule():
        nonlocal hoverID, fetching
        """
        if hoverID:
            widget.after_cancel(hoverID)
            hoverID = None
        """
            
        if fetching:
            widget.after_cancel(fetching)
            fetching = None
    
    #update the position of the hover window while mouse is on the "widget"
    #and by update i mean move it to the mouse's position
    #if you cant understand that by reading the code what are you here for
    def updateXY(event):
        if hoverWindow:
           x = widget.winfo_rootx() + event.x + 10
           y = widget.winfo_rooty() + event.y + 10
           hoverWindow.geometry(f"+{x}+{y}")

    #the tooltip or the pseudo window 
    def showHover(event=None):
        nonlocal hoverWindow
        x, y, cx, cy = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        hoverWindow = tk.Toplevel(widget)
        hoverWindow.wm_overrideredirect(True)
        hoverWindow.wm_geometry(f"+{x}+{y}")

        label = tk.Label(hoverWindow,  text=text, justify='center', background="#0f0f0f", fg = "#ffffff", relief='solid', borderwidth=0, wraplength=wraplength, image=cover, compound='bottom')
        label.pack(ipadx=1)
    
    #... please read the name of the function
    def hide():
        nonlocal hoverWindow
        if hoverWindow:
            hoverWindow.destroy()
            hoverWindow = None

    #create local variables, and non local for concatenated functions
    hoverID = None
    hoverWindow = None
    fetching = None
    #title, score, genres, cover = None, None, None, None
    #binding events to functions
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)
    widget.bind("<ButtonPress>", leave)
    #widget.bind("<Motion>", updateXY)

#like 20% sure this is not needed. delete if you want to. it does absolutely nothing
imgCache = {}

def resize(event):
    #a nice little function to resize the window and the canvas.
    #plus, dynamic!
    nwidth = int(root.winfo_width() * 0.70)
    nheight = int(root.winfo_height() * 0.90)
    canvas.configure(width= nwidth, height = nheight)

    iwidth = int(root.winfo_width() * 0.30)
    iheight = int(root.winfo_height() * 0.90)
    infoCanvas.configure(width= iwidth, height = iheight)
#} end

#resize elements when screen is resized
root.bind("<Configure>", resize)

#where the data is stored. its in the same directory as the script, or exe if you compiled it (which is the release version)
file = r"anime.csv"
#uncomment if you want to use the icon, but in compilation it uses a different method. use py2exe (recommended) or pyinstaller (which is what py2exe uses)
icon = tk.PhotoImage(file=r"aura.png")
root.iconphoto(False, icon)

#check if the file exists, if not create it
if not os.path.exists(file):
    with open(file, "x") as activefile:
        writer = csv.DictWriter(activefile, fieldnames=fieldnamez)
        writer.writeheader()

#arrays to store the data
rowZ = [] #saves the csv file here in temp
variables = []
container = tk.Frame(root, bg="#1C1C1C", highlightthickness=0)
canvas = tk.Canvas(container, bg='#1C1C1C', highlightthickness=0)
frame = tk.Frame(canvas, bg="#1C1C1C")
# frame.pack(fill="both", expand=True)

#bunch of ui elements begin

infoContainer =  tk.Frame(root, bg="#1C1C1C", highlightthickness=0)
infoCanvas = tk.Canvas(infoContainer, bg='#1C1C1C', highlightthickness=0)
infoFrame = tk.Frame(infoCanvas, bg="#1C1C1C")

frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
infoFrame.bind("<Configure>", lambda e: infoCanvas.configure(scrollregion=infoCanvas.bbox("all")))

window = canvas.create_window((0,0), window=frame, anchor="nw")
root.after(100, lambda: canvas.yview_moveto(0))

container.place(x=0,y=0)
canvas.pack(side="left", fill="both", expand=True)

infoContainer.place(x=width*0.70,y=0)
infoCanvas.pack(side="left", fill="both", expand=True)

infoWindow = infoCanvas.create_window((0,0), window=infoFrame, anchor="nw")
infoFrame.pack()

infoTitle = tk.Label(infoFrame, text=None, bg="#1C1C1C", fg="white", font=("Comfortaa", 18), wraplength=400)
infoRating = tk.Label(infoFrame, text=None, bg="#1C1C1C", fg="white", font=("Comfortaa", 14))
infoGenres = tk.Label(infoFrame, text=None, bg="#1C1C1C", fg="white", font=("Comfortaa", 14))
infoCover = tk.Label(infoFrame, image=None, bg="#1C1C1C")
otherInfo = tk.Label(infoFrame, text=None, bg="#1C1C1C", fg="white", font=("Comfortaa", 14))

infoTitle.pack(padx = 15, pady = 10)
infoCover.pack(padx=15, pady=10)
infoRating.pack(padx = 15, pady = 5)
infoGenres.pack(padx = 15, pady = 5)
otherInfo.pack(padx = 15, pady = 5)

searchVar = tk.StringVar()
searchBar = tk.Entry(root, textvariable=searchVar, bg="#333333", fg="white", font=("Comfortaa", 14), relief="solid", borderwidth=0)
searchBar.place(x=width*0, y=height*0.92, width=width*0.70, height=30)

searchBar.bind("<Return>", lambda e: search(searchVar.get()))

dropdownTheme = ttk.Style()
dropdownTheme.theme_use("clam")

dropdownTheme.configure(
    "TCombobox",
    fieldbackground="#333333",
    background="#333333",
    foreground="black",
    arrowcolor="white",
)

root.option_add("*TCombobox*Listbox.background", "#3f3f3f")
root.option_add("*TCombobox*Listbox.foreground", "white")
root.option_add("*TCombobox*Listbox.selectBackground", "#555555")
root.option_add("*TCombobox*Listbox.selectForeground", "white")

dropdown = ttk.Combobox(root, values=["NAME", "TAGS", "WATCHED", "UNWATCHED"], state="readonly", font=("Comfortaa", 14), style="TCombobox")
dropdown.current(0)

dropdown.place(x=width*0.70, y=height*0.92, width=175, height=30)

dropdown.bind("<<ComboboxSelected>>", lambda e: filter(e, dropdown.get()))

searchBar.bind("<KeyRelease>", lambda e: filter(e, dropdown.get()))

#end

#bunch of functions begin{
def lookup(anime):
    
    #using jikan api to get the anime data, a life saver.
    response = requests.get(f"https://api.jikan.moe/v4/anime?q={anime}&limit=1")
    response.raise_for_status()
    results = response.json().get("data",[])
    #the data is a json object and we really only care about the first result
    #... also to say the 0th index is the only result
    #sure its a bit slow, but thats what you get for free
    if results:
        anime = results[0]
        genres = [genre["name"].strip().upper() for genre in anime.get("genres", [])] #i just like uppercase i guess
        title = anime["title"]
        score = anime["score"]
        genres = list(set(genres)) #removing duplicates
        imgUrl = anime["images"]["jpg"]["large_image_url"]
        imageReq = requests.get(imgUrl)
        imageReq.raise_for_status()
        image = Image.open(BytesIO(imageReq.content)) #get image pt1
        image.thumbnail((300, 300))
        imag = ImageTk.PhotoImage(image)  #get image pt2
        duration = anime["duration"]
        episodes = anime["episodes"]
        year = anime["year"]
        return title, score, genres, imag, duration, episodes, year

def infoUpdate(title, score, genres, cover, duration, episodes, year):
    infoCover.image = cover
    otherInfoText = f"year: {year}\nlen: {duration}\nepisodes: {episodes}"

    infoTitle.config(text=title)
    infoRating.config(text=f"Rating: {score}/10")
    infoGenres.config(text=f"Genres: {', '.join([genre.capitalize() for genre in genres])}")
    infoCover.config(image=cover)
    otherInfo.config(text=otherInfoText)

def windowsScroll(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")

def unixScroll(event):
    if event.num == 4:
        canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        canvas.yview_scroll(1, "units")

def addThese():
    # global addButton
    global tempVars, tempAnime, i
    if len(tempVars) == len(tempAnime):
        for l in range(len(tempVars)):
            if tempVars[l].get() == 1:
                i += 1
                name, genre = tempAnime[l]
                # rowZ.append(name, 0, ";".join(genre), i)
                rowZ.append({"NAME": name,
                             "VALUE": 0,
                             "TAGS": ";".join(genre),
                             "INDEX": i})
                var = tk.IntVar(value=0)
                variables.append(var)
    searchBar.delete(0, tk.END)
    save(destroy=False)
    updateTitle()
    filter(event=None, TYPE=dropdown.get())
    # print("ermmm")
    addButton.place_forget()

def search(anime):
    global addButton
    # print(anime)
    addButton = tk.Button(root, text="add", command=addThese, bg="#333333", fg="white", font=("Comfortaa", 14), relief="solid", borderwidth=0)
    addButton.place(x=width*0.825, y=height*0.92, width=100, height=30)
    jikan10 = f"https://api.jikan.moe/v4/anime?q={anime}&limit=10"
    response = requests.get(jikan10)
    response.raise_for_status()
    results = response.json().get("data", [])
    # print(results)
    makeCheckbox(results, anime)

def makeCheckbox(results, query=None):
    global tempVars, tempAnime
    lo = 0
    tempVars = []
    tempAnime = []
    for widget in frame.winfo_children():
        widget.destroy()

    canvas.yview_moveto(0)

    animeSplural = results
    # print(len(animeSplural))
    for index, row in enumerate(animeSplural):
        lo += 1
        var = tk.IntVar(value=int(i))
        check = tk.Checkbutton(frame, 
            text=f"{lo} : {row['title']}", 
            variable=var,
            bg="#1C1C1C",
            fg="white",
            selectcolor="#333333",
            font="Comfortaa",
            activebackground="#1C1C1C",
            activeforeground="white",
        # command= lambda: print("sel"))
        )
        check.pack(anchor="w", side="top")
        tempVars.append(var)
        tempAnime.append([row.get("title"), [genre["name"] for genre in row["genres"]]])
        onHover(check, row.get("title"))

    # print(f"results for {query}")
    
def filter(event, TYPE):
    global variables
    query = searchVar.get().strip().upper()
    if event:
        if event.keysym == "Return":
            return
    
    if TYPE == "WATCHED" or TYPE == "UNWATCHED":
        if TYPE == "WATCHED":
            query = "1"
        else:
            query = "0"
        TYPE = "VALUE"

    if query:
        for widget in frame.winfo_children():
            widget.destroy()
        
        for index, row, in enumerate(rowZ):
            if query in str(row[f"{TYPE}"]).upper():
                var = tk.IntVar(value=int(row["VALUE"]))
                #variables.append(var)
                variables[index] = var
                check = tk.Checkbutton(frame,
                    text=f"{row['INDEX']} : {row['NAME']}",
                    variable=var,
                    bg="#1C1C1C",
                    fg="white",
                    selectcolor="#333333",
                    font="Comfortaa",
                    activebackground="#1C1C1C",
                    activeforeground="white",
                    command=lambda: updateTitle(mode="Debug")
                )
                check.pack(anchor="w")
                anime = row['NAME']
                onHover(check, anime)
    else:
        for widget in frame.winfo_children():
            widget.destroy()
        
        for index, row, in enumerate(rowZ):
            var = tk.IntVar(value=int(row["VALUE"]))
            #variables.append(var)
            variables[index] = var
            check = tk.Checkbutton(frame,
                text=f"{row['INDEX']} : {row['NAME']}",
                variable=var,
                bg="#1C1C1C",
                fg="white",
                selectcolor="#333333",
                font="Comfortaa",
                activebackground="#1C1C1C",
                activeforeground="white",
                command=lambda: updateTitle(mode="Debug")
            )
            check.pack(anchor="w")
            anime = row['NAME']
            onHover(check, anime)

    #lambda: updateTitle(mode="Debug")
    
def updateTitle(mode=None):
    global rowZ, zero

    
    rowZ, variables = updateRowZ()
    #print(len(variables))
    #printArr(rowZ)

    i = 0
    w = sum(var.get() for var in variables)
    t = len(variables)
    if w == t:
        root.title(f"watch later list [ completed :  all {w} watched ]")
    else:
        root.title(f"watch later list [ {t} in list | {w} watched ]")
    
    if mode == "Debug":

        i += 1
        zero += 1
        # print(f"{zero}: called {i}")

def updateRowZ():
    tempRowz = []
    tempVarz = variables
    raW = rowZ
    for index, row in enumerate(raW):
        row['VALUE'] = tempVarz[index].get()
        tempRowz.append(row)
    
    # print(len(tempVarz))
    return list(tempRowz), tempVarz

def printArr(arr):
    for i, r in enumerate(arr):
        print(i, r['NAME'])
    # never to be used, lmao

def save(destroy=True):
    watched = 0
    for index, row in enumerate(rowZ):
        row['VALUE'] = variables[index].get()
    
    with open(file, "w", newline='', encoding='utf-8') as filetowrite:
        writer = csv.DictWriter(filetowrite, fieldnames=fieldname)
        writer.writeheader()
        writer.writerows(rowZ)
    
    if destroy:
        root.destroy()

# def add(NAME,VALUE,TAGS,INDEX,MALID,RATING,IMAGE, title, score, genres, imag, duration, episodes, year):
    # rowZ.append({"NAME":title, "VALUE":None, "TAGS":TAGS, "INDEX":INDEX, "MALID":MALID, "RATING":RATING, "IMAGE":IMAGE})

def addLookup():
    lookupMode = dropdown.get()

    if lookupMode == "WATCHED" or lookupMode == "UNWATCHED":
        return
    
    if lookupMode == "NAME":
        lookup(searchVar.get())
#} end
canvas.bind_all("<MouseWheel>", windowsScroll)
canvas.bind_all("<Button-4>", unixScroll)
canvas.bind_all("<Button-5>", unixScroll)

# create checkboxes and assign them a hover function, aka the initial
with open (file) as filetoread:
    reader = csv.DictReader(filetoread)
    global i
    i = 0
    watched = 0
    fieldname = reader.fieldnames
    for row in reader:
        i += 1
        if row['VALUE'] == "" or row['VALUE'] == None:
            row["VALUE"] = 0
        if row['VALUE'] == "1":
            watched += 1
        row["INDEX"] = i

        rowZ.append(row)

        var = tk.IntVar(value=int(row["VALUE"]))
        variables.append(var)

        check = tk.Checkbutton(frame,
            text=f"{i} : {row['NAME']}",
            variable=var,
            bg="#1C1C1C",
            fg="white",
            selectcolor="#333333",
            font="Comfortaa",
            activebackground="#1C1C1C",
            activeforeground="white",
            command=lambda: updateTitle()
        )
        check.pack(anchor="w")
        anime = row['NAME']
        onHover(check, anime)
root.protocol("WM_DELETE_WINDOW", save)
if watched == i:
    root.title(f"watch later list [ completed :  all {watched} watched ]")
else:
    root.title(f"watch later list [ {i} in list | {watched} watched ]")

root.mainloop()

# code made by kodealt on github. @a_persan on discord, if you have any questions.
# version 1 (current) made on feb 22, 2025