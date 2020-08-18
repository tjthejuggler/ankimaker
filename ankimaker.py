import numpy as np

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

from ankiarticle import *
from langCodes import *

#look into quillionz and python library question-generation for making questions

#hook up language inputs and get rid of dest optionmenu if article is selected
text_filename = 'podFoundmyfitnessCovid2'

root = Tk() 
root.title('Miug')
root.geometry('400x400')
root.resizable(0, 0)

deck = genanki.Deck(round(time.time()),text_filename)

freq_threshold = 2

# for language, have a src and dest language input with dropdown

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
	text_filename = os.path.splitext(os.path.basename(filename_string))[0]
	return text_filename

def file_browse_button_clicked():
	file_name = browseFiles()
	file_name_label.configure(text=file_name)
	file_name_label.update()

def text_type_radiobutton_changed(*args):
    if text_type_language_or_article.get() == 'language':
        print('language')
    if text_type_language_or_article.get() == 'article':
        print('article')


def show_frequencies():
	with open('sources/'+text_filename+'.txt', encoding="utf8") as file:
		source_text = file.read().replace('\n', ' ')
	if source_text:
		word_frequency_dictionary = dict()
		clean = re.sub(r"[,.;@#?¿!¡\-\"&$\[\]\)\(]+\ *", " ", source_text)
		words = clean.split()
		for word in words:
			if not word.isdigit():
				word_frequency_dictionary[word] = round(zipf_frequency(word, "es"),1)
		for x in np.arange(0, 10, 0.1):
			clean_x = round(x,1)
			words_with_x_freq = []
			for word, freq in word_frequency_dictionary.items():
				if freq == x:
					words_with_x_freq.append(word)
			if words_with_x_freq:
				print(clean_x)
				print(words_with_x_freq)

def run_clicked():
	print('run_clicked', text_type_language_or_article.get())
	if text_type_language_or_article.get() == 'language':
		print('language')
	if text_type_language_or_article.get() == 'article':
		print('article')
		run_article_program(text_filename, deck, str(src_lang.get()))



file_browse_button = ttk.Button(root, text="Select file", command=file_browse_button_clicked)
file_browse_button.place(x=30,y=30)

file_name_label = ttk.Label(root, text=text_filename)
file_name_label.place(x=180,y=30)



text_type_language_or_article = StringVar()
path_point_language_radiobutton = Radiobutton(root, text='language', variable=text_type_language_or_article, value='language', font=('Courier', 10))
path_point_language_radiobutton.place(x=30,y=60)
text_type_article_radiobutton = Radiobutton(root, text='article', variable=text_type_language_or_article, value='article', font=('Courier', 10))
text_type_article_radiobutton.place(x=180, y=60)
text_type_language_or_article.set('article')
text_type_language_or_article.trace('w', text_type_radiobutton_changed)

language_choice = {"a","b","c","d","e","f"}
source_language_label = ttk.Label(root, text='source language:')
source_language_label.place(x=30,y=90)
src_lang = ttk.StringVar(root)
src_lang.set('english')
source_language_optionmenu = ttk.OptionMenu(root, src_lang, *language_choices)
source_language_optionmenu.place(x=130,y=90)
source_language_optionmenu.config(width=10)
destination_language_label = ttk.Label(root, text='target language:')
destination_language_label.place(x=30,y=120)
dest_lang = ttk.StringVar(root)
dest_lang.set('spanish')
destination_language_optionmenu = ttk.OptionMenu(root, dest_lang, *language_choices)
destination_language_optionmenu.place(x=130,y=120)
destination_language_optionmenu.config(width=10)


frequency_thresholds_label = ttk.Label(root, text='frequency thresholds:')
frequency_thresholds_label.place(x=30,y=150)
frequency_thresholds_low_entry = Entry(root, bd =1, width=3)
frequency_thresholds_low_entry.place(x=160,y=150)
frequency_thresholds_high_entry = Entry(root, bd =1, width=3)
frequency_thresholds_high_entry.place(x=190,y=150)

show_frequencies_button = ttk.Button(root, text="Show frequencies", command=show_frequencies)
show_frequencies_button.place(x=230,y=150)

run_button = ttk.Button(root, text="Run", command=run_clicked)
run_button.place(x=330,y=150)





root.mainloop()


#current_midi_config_optionmenu = OptionMenu(root, current_midi_config_index, *all_possible_point_config_indices)
#current_midi_config_optionmenu.place(x=10,y=480)