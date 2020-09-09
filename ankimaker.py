import numpy as np
import sys
import re
import genanki
import time
from wordfreq import zipf_frequency
import json
import os
from tkinter import *
import tkinter as ttk
from epub_conversion.utils import open_book, convert_epub_to_lines
import os.path
from os import path
import urllib.request
import urllib
from youtube_title_parse import get_artist_title
from youtube_transcript_api import YouTubeTranscriptApi
#import pdftotext
from tika import parser

from ankiarticle import *
from langCodes import *
from ankilang import *

#freq_threshold = 7 #7 is probably good for spanish, #10 for turkish
#rare_freq_threshold = -1 #1 is probably good for spanish, -1 for turkish


text_filename = 'podFoundmyfitnessCovid2'
text_filename = 'sample'
video_id = ''

root = Tk() 
root.title('Miug')
#root.geometry('400x400')
root.resizable()
#root.maxsize(500, 500) 


def get_custom_splitters():
	with open('custom_splitters.txt', 'r') as filehandle:
	    splitter_options = json.load(filehandle)
	return splitter_options

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

def show_file_browser_widgets():
	youtubeInfoFrame.pack_forget()
	fileBrowseFrame.pack(fill=X)

def show_url_entry():
	youtubeInfoFrame.pack(fill=X)
	fileBrowseFrame.pack_forget()

def text_type_radiobutton_changed(*args):
	if text_type.get() == 'language':
		print('language')
		show_file_browser_widgets()
		src_lang.set('spanish')
		dest_lang.set('english')
		chooseDefinitionsButtonFrame.pack_forget()
		destination_language_optionmenu.configure(state='normal')
		frequency_thresholds_low_entry.configure(state='normal')
		exclude_var_entry.configure(state='disable')
	if text_type.get() == 'article':
		print('article')
		show_file_browser_widgets()
		src_lang.set('english')
		destination_language_optionmenu.configure(state='disable')
		frequency_thresholds_low_entry.configure(state='disable')
		chooseDefinitionsButtonFrame.pack(side='left')
		exclude_var_entry.configure(state='normal')
	if text_type.get() == 'youtube':
		print('youtube')
		show_url_entry()
		src_lang.set('english')
		chooseDefinitionsButtonFrame.pack(side='left')
		destination_language_optionmenu.configure(state='disable')
		frequency_thresholds_low_entry.configure(state='disable')
		exclude_var_entry.configure(state='normal')

def get_text_from_youtube_transcription(video_id):
	transcription_text = ''
	transcription = YouTubeTranscriptApi.get_transcript(video_id)
	for line in transcription:
		transcription_text = transcription_text + line['text'] + ' '
	return transcription_text

def youtubeTitleFormatted(title):
	lower_title = title.lower()
	print('lowe', lower_title)
	no_symbol_title = re.sub(r"[,.'`’'|—;:@#?¿!¡<>_\-\"”“&$\[\]\)\(\\\/]+\ *", " ", lower_title)
	print(no_symbol_title)
	split_title = no_symbol_title.split(sep=None)
	print(split_title)
	formatted_title = ''
	for word in split_title:
		formatted_title = formatted_title + word.capitalize()
	return formatted_title

def url_button_clicked():
	global text_filename
	global video_id
	try:
		video_id = url_entry.get().split('=')[1]
		params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % video_id}
		url = "https://www.youtube.com/oembed"
		query_string = urllib.parse.urlencode(params)
		url = url + "?" + query_string
		with urllib.request.urlopen(url) as response:
			response_text = response.read()
			data = json.loads(response_text.decode())
			artist, title = get_artist_title(data['title'])
			print('title', title)
			youtube_file_name_var.set(youtubeTitleFormatted(title)) #data['title'] is the whole title
	except:
		youtube_file_name_var.set('invalid url')
	file_name_label.configure(text=text_filename)
	file_name_label.update()
	#print(get_text_from_youtube_transcription(video_id))

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
	if text_type.get() == 'youtube':
		createTextFileFromYoutube()
	source_text = None
	if path.exists('sources/'+text_filename+".txt"):
		with open('sources/'+text_filename+'.txt', encoding="utf8") as file:
			source_text = file.read().replace('\n', ' ')
	elif path.exists('sources/'+text_filename+".epub"):
		book = open_book('sources/'+text_filename+".epub")
		convertedBook = convert_epub_to_lines(book)
		source_text = ' '.join(convertedBook)
	elif path.exists('sources/'+text_filename+".pdf"):
		raw = parser.from_file('sources/'+text_filename+".pdf")
		print(raw['content'])
		source_text = raw['content']
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

def createTextFileFromYoutube():
	global video_id
	text = get_text_from_youtube_transcription(video_id)
	print('cr',text_filename)
	fileToWrite = open('sources/'+text_filename+'.txt',"w+", encoding="utf8")
	fileToWrite.write(text)
	fileToWrite.close()

def change_name_label(change_to):
	file_name_label.configure(text=change_to)
	file_name_label.update()

def create_deck_clicked():
	deck = genanki.Deck(round(time.time()),text_filename)
	print('create_deck_clicked', text_type.get())
	src_lng = str(src_lang.get())
	dst_lng = str(src_lang.get())
	frq_l = float(frequency_low.get())
	frq_h = float(frequency_high.get())
	splitters = splitters_var.get().split(',')
	if text_type.get() == 'language':
		print('language')
		run_language_program(text_filename, deck, src_lng, dst_lng, frq_l, frq_h, splitters)
	elif text_type.get() == 'article':
		print('article')
		root.destroy()
		run_article_program(text_filename, deck, src_lng, frq_h, splitters)		
	elif text_type.get() == 'youtube':
		if text_filename != 'invalid url':
			print('youtube valid')
			createTextFileFromYoutube()
			run_article_program(text_filename, deck, src_lng, frq_h, splitters)
		else:
			print('youtube not valid')

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

def add_to_custom_splitters(splitters_to_add, this_window):
	print('add_to_custom_splitters'+splitters_to_add)
	all_splitters = get_custom_splitters()
	all_splitters.append(splitters_to_add)	
	with open('custom_splitters.txt', 'w') as filehandle:
		json.dump(all_splitters, filehandle)
	splitters_var.set('')
	splitters_optionmenu['menu'].delete(0, 'end')
	for splitter_choice in all_splitters:
		splitters_optionmenu['menu'].add_command(label=splitter_choice, command=ttk._setit(splitters_var, splitter_choice))
	this_window.destroy()

def open_add_splitters():
	add_splitters_window = Toplevel(root)
	add_splitters_window.title("Add splitters") 
	add_splitters_window.geometry("600x60")
	splitters_to_add = StringVar(add_splitters_window, value='')
	add_splitters_entry = Entry(add_splitters_window, textvariable = splitters_to_add, bd =1, width=100)
	add_splitters_entry.place(x=10,y=20)	
	add_splitters_button = ttk.Button(add_splitters_window, text="Add", command=lambda : add_to_custom_splitters(splitters_to_add.get(), add_splitters_window))
	add_splitters_button.place(x=10,y=40)

def remove_from_custom_splitters():
	all_splitters = get_custom_splitters()
	all_splitters.remove(splitters_var.get())	
	with open('custom_splitters.txt', 'w') as filehandle:
		json.dump(all_splitters, filehandle)
	splitters_var.set('')
	splitters_optionmenu['menu'].delete(0, 'end')
	for splitter_choice in all_splitters:
		splitters_optionmenu['menu'].add_command(label=splitter_choice, command=ttk._setit(splitters_var, splitter_choice))

def youtube_file_name_var_callback():
	global text_filename
	text_filename = youtube_file_name_var.get()
	file_name_label.configure(text=text_filename)
	file_name_label.update()
	print(youtube_file_name_var.get())

def choose_definitions_clicked():
	setupFrame.grid_forget()
	chooseDefinitionsFrame.grid(row=2, column=0, sticky=W)
	print('choose definitions')

nameAndHelpFrame = Frame(root)
nameAndHelpFrame.grid(row=0, column=0, sticky="ew", pady = 4)
file_name_label = ttk.Label(nameAndHelpFrame, text=text_filename)
file_name_label.pack(side='left', anchor=W)
help_button = ttk.Button(nameAndHelpFrame, text="?", command=help_clicked)
help_button.pack(side='right', anchor=E)

setupFrame = Frame(root)
setupFrame.grid(row=1, column=0, sticky=W)

textTypeFrame = Frame(setupFrame)
textTypeFrame.pack(fill=X, pady = 4)
text_type = StringVar()
text_type_language_radiobutton = Radiobutton(textTypeFrame, text='language', variable=text_type, value='language')
text_type_language_radiobutton.pack(side="left")
text_type_article_radiobutton = Radiobutton(textTypeFrame, text='article', variable=text_type, value='article')
text_type_article_radiobutton.pack(side="left")
text_type_youtube_radiobutton = Radiobutton(textTypeFrame, text='youtube', variable=text_type, value='youtube')
text_type_youtube_radiobutton.pack(side="left")
text_type.set('article')
text_type.trace('w', text_type_radiobutton_changed)

outsideDataFrame = Frame(setupFrame)
outsideDataFrame.pack(fill=X)

youtubeInfoFrame = Frame(outsideDataFrame)
youtube_file_name_label = ttk.Label(youtubeInfoFrame, text='name')
youtube_file_name_label.grid(row=0, column=0, sticky=E, pady = 4)
youtube_file_name_var = StringVar(youtubeInfoFrame, value='')
youtube_file_name_var.trace("w", lambda name, index, mode, youtube_file_name_var=youtube_file_name_var: youtube_file_name_var_callback())
youtube_file_name_entry = ttk.Entry(youtubeInfoFrame, text=youtube_file_name_var,bd =1, width=45)
youtube_file_name_entry.grid(row=0, column=1, pady = 4)

youtube_file_url_label = ttk.Label(youtubeInfoFrame, text='url')
youtube_file_url_label.grid(row=1, column=0, sticky=E, pady = 4)
url_entry_var = StringVar(youtubeInfoFrame, value='')
url_entry = Entry(youtubeInfoFrame, textvariable = url_entry_var,bd =1, width=45)
url_entry.grid(row=1, column=1, pady = 4)
url_entry_button = ttk.Button(youtubeInfoFrame, text="ok", command=url_button_clicked)
url_entry_button.grid(row=1, column=2, pady = 4, padx = 4)

fileBrowseFrame = Frame(outsideDataFrame)
fileBrowseFrame.pack(fill=X)
file_browse_button = ttk.Button(fileBrowseFrame, text="Select file", command=file_browse_button_clicked)
file_browse_button.pack(side="left")

languageFrame = Frame(setupFrame)
languageFrame.pack(fill=X)
source_language_label = ttk.Label(languageFrame, text='source language:')
source_language_label.grid(row=0, column=0, sticky=E, pady = 4)
src_lang = ttk.StringVar(languageFrame)
src_lang.set('english')
source_language_optionmenu = ttk.OptionMenu(languageFrame, src_lang, *language_choices)
source_language_optionmenu.grid(row=0, column=1, pady = 4)
source_language_optionmenu.config(width=10)
destination_language_label = ttk.Label(languageFrame, text='target language:')
destination_language_label.grid(row=1, column=0, sticky=E, pady = 4)
dest_lang = ttk.StringVar(languageFrame)
dest_lang.set('spanish')
destination_language_optionmenu = ttk.OptionMenu(languageFrame, dest_lang, *language_choices)
destination_language_optionmenu.grid(row=1, column=1, pady = 4)
destination_language_optionmenu.configure(state='disable')
destination_language_optionmenu.config(width=10)

frequencyFrame = Frame(setupFrame)
frequencyFrame.pack(fill=X, pady = 4)
frequency_thresholds_label = ttk.Label(frequencyFrame, text='frequency thresholds:')
frequency_thresholds_label.pack(side="left")
frequency_low = StringVar(frequencyFrame, value=0)
frequency_thresholds_low_entry = Entry(frequencyFrame, textvariable = frequency_low, bd =1, width=3)
frequency_thresholds_low_entry.configure(state='disable')
frequency_thresholds_low_entry.pack(side="left")
frequency_high = StringVar(frequencyFrame, value=10)
frequency_thresholds_high_entry = Entry(frequencyFrame, textvariable = frequency_high,bd =1, width=3)
frequency_thresholds_high_entry.pack(side="left")
show_frequencies_button = ttk.Button(frequencyFrame, text="Show frequencies", command=show_frequencies)
show_frequencies_button.pack(side="left")

excludesFrame = Frame(setupFrame)
excludesFrame.pack(fill=X, pady = 4)
exclude_label = ttk.Label(excludesFrame, text='Excludes:')
exclude_label.pack(side="left")
exclude_var = StringVar(excludesFrame, value='')
exclude_var_entry = Entry(excludesFrame, textvariable = exclude_var, bd =1, width=30)
exclude_var_entry.configure(state='normal')
exclude_var_entry.pack(side="left")

splittersFrame = Frame(setupFrame)
splittersFrame.pack(fill=X, pady = 4)
splitters_choices = get_custom_splitters()
splitters_label = ttk.Label(splittersFrame, text='Splitters:')
splitters_label.pack(side="left")
splitters_var = StringVar(splittersFrame, value='')
splitters_optionmenu = ttk.OptionMenu(splittersFrame, splitters_var, *splitters_choices)
splitters_optionmenu.pack(side="left")
splitters_optionmenu.config(width=30)
add_splitters = ttk.Button(splittersFrame, text="+", command=open_add_splitters)
add_splitters.pack(side="left", padx = 4)
remove_spllitters = ttk.Button(splittersFrame, text=" - ", command=remove_from_custom_splitters)
remove_spllitters.pack(side="left", padx = 4)

chooseDefinitionsButtonFrame = Frame(setupFrame)
chooseDefinitionsButtonFrame.pack(fill=X, pady = 4)
choose_definitions_button = ttk.Button(chooseDefinitionsButtonFrame, text="Choose Definitions", command=choose_definitions_clicked)
choose_definitions_button.pack(side="left")

chooseDefinitionsFrame = Frame(root)
chooseDefinitionsFrame.grid_forget()

chooseDefinitionsTextFrame = Frame(chooseDefinitionsFrame)
chooseDefinitionsTextFrame.pack(fill=X, pady = 4)

scrollbar = Scrollbar(chooseDefinitionsTextFrame)
scrollbar.pack(side=RIGHT, fill = Y)

choose_definitions_text = ttk.Text(chooseDefinitionsTextFrame, 
		height = 4,
		width = 55,
		bg = 'black', 
		fg = 'white', 
		borderwidth = 5,
		relief="sunken",
		wrap='char',
		yscrollcommand = scrollbar.set)
choose_definitions_text.insert(END,'choose_definitions_text_text this is a test to see what \
	lots of text will look like in this label box. so now i am \
	just typing whatevr i want to. choose_definitions_text_text this\
	choose_definitions_text_text this is a test to see what \
	lots of text will look like in this label box. so now i am \
	just typing whatevr i want to. choose_definitions_text_text this')
choose_definitions_text.pack(side='left')

scrollbar.config(command=choose_definitions_text.yview)

createDeckFrame = Frame(root)
createDeckFrame.grid(row=3, column=0, sticky=W, pady = 4)
run_button = ttk.Button(createDeckFrame, text="Create Deck", command=create_deck_clicked)
run_button.pack(side="left", pady = 4)

root.mainloop()

#create deck button(only visible when lang file is input or all definitions have been decided)
