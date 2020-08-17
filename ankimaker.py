import sys
import re
import genanki
import time
from wordfreq import zipf_frequency
import requests
from requests.exceptions import HTTPError
import msvcrt
import wikipediaapi
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
import queue
from threading import Thread
from tkinter import filedialog 
from tkinter import Tk 
import os

from tkinter import *
import tkinter as ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image

import csv
import os

#from ankiarticle import *

root = Tk() 
root.title('Miug')
root.geometry('400x400')
root.resizable(0, 0)

# file select
# language/article
# threshold inputs
# a button that prints all words and shows their frequency to help select frequency thresholds
# either a unique deck id input or hook it up to current date/time
# for language, have a src and dest language input with dropdown

#closing tk window should end program

def printtest():
	print('test')

def browseFiles(): 
	Tk().withdraw()
	filename = filedialog.askopenfilename(initialdir = "/", 
                                          title = "Select a File", 
                                          filetypes = (("Text files", 
                                                        "*.txt*"), 
                                                       ("all files", 
                                                        "*.*"))) 	
	filename_string = filename.split(':')[1]
	print(filename_string)
	to_return = os.path.splitext(os.path.basename(filename_string))[0]
	return to_return

def file_browse_button_clicked():
	file_name = browseFiles()
	file_name_label.configure(text=file_name)
	file_name_label.update()

def text_type_radiobutton_changed(*args):
    if text_type_language_or_article.get() == 'language':
        print('language')
    if text_type_language_or_article.get() == 'article':
        print('article')

file_browse_button = ttk.Button(root, text="Click to Start Process", command=file_browse_button_clicked)
file_browse_button.place(x=30,y=30)

file_name_label = ttk.Label(root, text='')
file_name_label.place(x=180,y=30)



text_type_language_or_article = StringVar()
path_point_language_radiobutton = Radiobutton(root, text='language', variable=text_type_language_or_article, value='language', font=('Courier', 10))
path_point_language_radiobutton.place(x=30,y=60)
text_type_article_radiobutton = Radiobutton(root, text='article', variable=text_type_language_or_article, value='article', font=('Courier', 10))
text_type_article_radiobutton.place(x=180, y=60)
text_type_language_or_article.set('instances')
text_type_language_or_article.trace('w', text_type_radiobutton_changed)

frequency_thresholds_label = ttk.Label(root, text='frequency thresholds:')
frequency_thresholds_label.place(x=30,y=90)
frequency_thresholds_low_entry = Entry(root, bd =5)
frequency_thresholds_low_entry.place(x=130,y=90)
frequency_thresholds_high_entry = Entry(root, bd =5)
frequency_thresholds_high_entry.place(x=180,y=90)







root.mainloop()


#current_midi_config_optionmenu = OptionMenu(root, current_midi_config_index, *all_possible_point_config_indices)
#current_midi_config_optionmenu.place(x=10,y=480)