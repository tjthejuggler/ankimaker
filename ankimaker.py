import numpy as np
import sys
import re
import genanki
import time
from wordfreq import zipf_frequency
# import requests
# from requests.exceptions import HTTPError
#import msvcrt
#import wikipediaapi
# from nltk.stem.snowball import SnowballStemmer
# from nltk.stem import WordNetLemmatizer
# import queue
# from threading import Thread
# from tkinter import filedialog 
# from tkinter import Tk 
import os
from tkinter import *
import tkinter as ttk
# from tkinter.scrolledtext import ScrolledText
# from tkinter import messagebox
# from PIL import ImageTk, Image
# import csv
from epub_conversion.utils import open_book, convert_epub_to_lines
import os.path
from os import path

from ankiarticle import *
from langCodes import *
from ankilang import *

#freq_threshold = 7 #7 is probably good for spanish, #10 for turkish
#rare_freq_threshold = -1 #1 is probably good for spanish, -1 for turkish


text_filename = 'podFoundmyfitnessCovid2'
text_filename = 'sample'

root = Tk() 
root.title('Miug')
root.geometry('400x400')
root.resizable(0, 0)



def browseFiles(): 
	Tk().withdraw()
	filename = filedialog.askopenfilename(initialdir = "/", 
                                          title = "Select a File", 
                                          filetypes = (("all files", 
                                                        "*.*"),("Text files", 
                                                        "*.txt*"))) 	
	filename_string = filename.split(':')[1]
	print(filename_string)
	text_filename = os.path.splitext(os.path.basename(filename_string))[0]
	return text_filename

def file_browse_button_clicked():
	file_name = browseFiles()
	global text_filename
	text_filename = file_name
	file_name_label.configure(text=file_name)
	file_name_label.update()

def text_type_radiobutton_changed(*args):
	if text_type_language_or_article.get() == 'language':
		print('language')
		src_lang.set('spanish')
		dest_lang.set('english')
		destination_language_optionmenu.configure(state='normal')
		frequency_thresholds_low_entry.configure(state='normal')
		exclude_var_entry.configure(state='disable')
	if text_type_language_or_article.get() == 'article':
		print('article')
		src_lang.set('english')
		destination_language_optionmenu.configure(state='disable')
		frequency_thresholds_low_entry.configure(state='disable')
		exclude_var_entry.configure(state='normal')
		
def word_excluded(word):
	should_exclude = False
	lower_word = word.lower()
	if exclude_var.get():
		for item in exclude_var.get().split(','):
			item_clean = item.lower().strip()
			if len(item_clean) == len(lower_word):
				should_exclude = True
				for c in range(0, len(item_clean)):
					if item_clean[c] != '*':
						if item_clean[c] != lower_word[c]:
							should_exclude = False
	return should_exclude

def show_frequencies():
	source_text = None
	if path.exists('sources/'+text_filename+".txt"):
		with open('sources/'+text_filename+'.txt', encoding="utf8") as file:
			source_text = file.read().replace('\n', ' ')
	elif path.exists('sources/'+text_filename+".epub"):
		book = open_book('sources/'+text_filename+".epub")
		convertedBook = convert_epub_to_lines(book)
		source_text = ' '.join(convertedBook)
	if source_text:
		source_text = source_text.lower()
		excluded_words = []
		word_frequency_dictionary = dict()
		clean = re.sub(r"[,.'`’'|—;:@#?¿!¡<>_\-\"”“&$\[\]\)\(\\\/]+\ *", " ", source_text)
		words = clean.split()
		for word in words:
			if word_excluded(word):
				if not word in excluded_words:
					excluded_words.append(word)
			elif not word.isdigit():
				word_frequency_dictionary[word] = round(zipf_frequency(word, get_lang_code(str(src_lang.get()))),1)
		for x in np.arange(0, 10, 0.1):
			x = 10 - x
			clean_x = round(x,1)
			words_with_x_freq = []
			for word, freq in word_frequency_dictionary.items():
				if freq == x:
					words_with_x_freq.append(word)
			if words_with_x_freq:
				print(clean_x)
				print(words_with_x_freq)
		if excluded_words:
			print('EXCLUDED:')
			print(excluded_words)

def run_clicked():
	deck = genanki.Deck(round(time.time()),text_filename)
	print('run_clicked', text_type_language_or_article.get())
	if text_type_language_or_article.get() == 'language':
		print('language')
		run_language_program(text_filename, deck, str(src_lang.get()), str(dest_lang.get()), float(frequency_low.get()), float(frequency_high.get()))
	if text_type_language_or_article.get() == 'article':
		print('article')
		run_article_program(text_filename, deck, str(src_lang.get()), float(frequency_high.get()))

def help_clicked():
	print('Article: copy and paste an article into a txt file and then browse to it.')
	print('Language: copy and paste subtitles from a show/movie in a txt file, if it is')
	print('a show, seperate every episode with .ep#. where # is the episode number. This')
	print('is to make anki tags for each episode. If the filename is showCheers, then the')
	print('tag for episode 1 will be showCheersEp1.')
	print('In both cases, article and language, the name of the .apkg will be the same as')
	print('the original text file. You can use the threshold inputs to limit which words')
	print('will be used, the first threshold filters out rare words, and the second threshold')
	print('filters common words. Click the button next to the threshold inputs to see all')
	print('threshold numbers.')
	print('Excludes - Enter a pattern to be ignored using *s, for example to ignore CH01,')
	print('CH02, CH03.. input CH**. You can input as many patterns as you want seperated by')
	print('commas.')

file_browse_button = ttk.Button(root, text="?", command=help_clicked)
file_browse_button.place(x=360,y=10)

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
destination_language_optionmenu.configure(state='disable')
destination_language_optionmenu.config(width=10)

frequency_thresholds_label = ttk.Label(root, text='frequency thresholds:')
frequency_thresholds_label.place(x=30,y=150)
frequency_low = StringVar(root, value=0)
frequency_thresholds_low_entry = Entry(root, textvariable = frequency_low, bd =1, width=3)
frequency_thresholds_low_entry.configure(state='disable')
frequency_thresholds_low_entry.place(x=160,y=150)
frequency_high = StringVar(root, value=10)
frequency_thresholds_high_entry = Entry(root, textvariable = frequency_high,bd =1, width=3)
frequency_thresholds_high_entry.place(x=190,y=150)

show_frequencies_button = ttk.Button(root, text="Show frequencies", command=show_frequencies)
show_frequencies_button.place(x=230,y=150)

exclude_label = ttk.Label(root, text='Excludes:')
exclude_label.place(x=30,y=180)
exclude_var = StringVar(root, value='')
exclude_var_entry = Entry(root, textvariable = exclude_var, bd =1, width=30)
exclude_var_entry.configure(state='normal')
exclude_var_entry.place(x=100,y=180)

run_button = ttk.Button(root, text="Run", command=run_clicked)
run_button.place(x=30,y=210)

root.mainloop()
