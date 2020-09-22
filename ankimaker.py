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
from tika import parser
import queue
import platform

from ankiarticle import *
from langCodes import *
from ankilang import *
from USERDATA import *

USERDATA_ = USERDATA() # Can also use initialization arguments

entry_width = 47
if platform.system() == 'Windows':
	entry_width = 73

root = Tk() 
root.title('Miug')
root.resizable()

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
	USERDATA_.text_filename = os.path.splitext(os.path.basename(filename_string))[0]
	return USERDATA_.text_filename

def file_browse_button_clicked():
	file_name = browseFiles()
	USERDATA_.text_filename = file_name
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
		show_file_browser_widgets()
		src_language.set('spanish')
		dest_lang.set('english')
		destination_language_optionmenu.configure(state='normal')
		frequency_thresholds_low_entry.configure(state='normal')
		exclude_var_entry.configure(state='disable')
	if text_type.get() == 'article':
		show_file_browser_widgets()
		src_language.set('english')
		destination_language_optionmenu.configure(state='disable')
		frequency_thresholds_low_entry.configure(state='disable')
		exclude_var_entry.configure(state='normal')
	if text_type.get() == 'youtube':
		show_url_entry()
		src_language.set('english')
		destination_language_optionmenu.configure(state='disable')
		frequency_thresholds_low_entry.configure(state='disable')
		exclude_var_entry.configure(state='normal')

def get_text_from_youtube_transcription(vid_id):
	transcription_text = ''
	transcription = YouTubeTranscriptApi.get_transcript(vid_id)
	for line in transcription:
		transcription_text = transcription_text + line['text'] + ' '
	return transcription_text

def youtubeTitleFormatted(title):
	lower_title = title.lower()
	no_symbol_title = re.sub(r"[,.'`’'|—;:@#?¿!¡<>_\-\"”“&$\[\]\)\(\\\/]+\ *", " ", lower_title)
	split_title = no_symbol_title.split(sep=None)
	formatted_title = ''
	for word in split_title:
		formatted_title = formatted_title + word.capitalize()
	return formatted_title

def url_button_clicked():
	try:
		USERDATA_.video_id = url_entry.get().split('=')[1]
		params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % USERDATA_.video_id}
		url = "https://www.youtube.com/oembed"
		query_string = urllib.parse.urlencode(params)
		url = url + "?" + query_string
		with urllib.request.urlopen(url) as response:
			response_text = response.read()
			data = json.loads(response_text.decode())
			artist, title = get_artist_title(data['title'])
			youtube_file_name_var.set(youtubeTitleFormatted(title)) #data['title'] is the whole title
	except:
		youtube_file_name_var.set('invalid url')
	file_name_label.configure(text=USERDATA_.text_filename)
	file_name_label.update()

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
	show_info_text()
	if text_type.get() == 'youtube':
		createTextFileFromYoutube()
	source_text = None
	if path.exists('sources/'+USERDATA_.text_filename+".txt"):
		with open('sources/'+USERDATA_.text_filename+'.txt', encoding="utf8") as file:
			source_text = file.read().replace('\n', ' ')
	elif path.exists('sources/'+USERDATA_.text_filename+".epub"):
		book = open_book('sources/'+USERDATA_.text_filename+".epub")
		convertedBook = convert_epub_to_lines(book)
		source_text = ' '.join(convertedBook)
	elif path.exists('sources/'+USERDATA_.text_filename+".pdf"):
		raw = parser.from_file('sources/'+USERDATA_.text_filename+".pdf")
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
				word_frequency_dictionary[word] = round(zipf_frequency(word, get_lang_code(str(src_language.get()))),1)
		for x in np.arange(0, 10, 0.1):
			x = 10 - x
			clean_x = round(x,1)
			words_with_x_freq = []
			for word, freq in word_frequency_dictionary.items():
				if freq == x:
					words_with_x_freq.append(word)
			if words_with_x_freq:
				tkprint(str(clean_x))
				tkprint(str(words_with_x_freq))
		if excluded_words:
			tkprint('EXCLUDED:')
			tkprint(str(excluded_words))

def createTextFileFromYoutube():
	text = get_text_from_youtube_transcription(USERDATA_.video_id)
	fileToWrite = open('sources/'+USERDATA_.text_filename+'.txt',"w+", encoding="utf8")
	fileToWrite.write(text)
	fileToWrite.close()

def change_name_label(change_to):
	file_name_label.configure(text=change_to)
	file_name_label.update()

def begin_choose_definitions_cycle():
	setupFrame.grid_forget()
	showInfoTextOuterFrame.grid(row=2, column=0, sticky=W)
	chooseDefinitionsEntryFrame.grid(row=3, column=0, sticky=W, pady = 4)
	choose_definitions_entry.focus()
	USERDATA_.article_text = get_text(USERDATA_.text_filename)
	add_words_to_dictionary(USERDATA_.article_text)
	ask_if_should_define()

def create_deck_clicked():
	create_deck_button.pack_forget()
	createDeckButtonFrame.grid_forget()
	showInfoTextOkButtonFrame.pack_forget()
	deck = genanki.Deck(round(time.time()),USERDATA_.text_filename)
	src_lng = str(src_language.get())
	dst_lng = str(src_language.get())
	frq_l = float(frequency_low.get())
	frq_h = float(frequency_high.get())
	splitters = splitters_var.get().split(',')
	if text_type.get() == 'language':
		run_language_program(USERDATA_.text_filename, deck, src_lng, dst_lng, frq_l, frq_h, splitters)
	elif text_type.get() == 'article':
		begin_choose_definitions_cycle()		
	elif text_type.get() == 'youtube':
		if USERDATA_.text_filename != 'invalid url':
			createTextFileFromYoutube()
			begin_choose_definitions_cycle()
		else:
			print('youtube not valid')

def show_info_text():
	setupFrame.grid_forget()
	showInfoTextOuterFrame.grid(row=2, column=0, sticky=W)
	createDeckButtonFrame.grid_forget()
	showInfoTextOkButtonFrame.pack(side='left', pady = 4, padx = 8)
	clear_tkprint()


def help_clicked():
	show_info_text()
	tkprint('Article: Copy and paste an article into a txt file and then browse to it.')
	tkprint('Language: Copy and paste foreign text in a txt file.')
	tkprint('Splitters: Indicate words that will be used to seperate the text into sections. This'
		'is to make anki tags for each episode. For example, if the filename is showCheers, then the'
		'tag for episode 1 will be showCheersEp1.'
		'In both cases, article and language, the name of the .apkg will be the same as'
		'the original text file. You can use the threshold inputs to limit which words'
		'will be used, the first threshold filters out rare words, and the second threshold'
		'filters common words. Click the button next to the threshold inputs to see all'
		'threshold numbers.')
	tkprint('Excludes - Enter a pattern to be ignored using *s, for example to ignore CH01,'
		'CH02, CH03.. input CH**. You can input as many patterns as you want seperated by'
		'commas.')

def hide_info_text():
	setupFrame.grid(row=1, column=0, sticky=W)
	showInfoTextOuterFrame.grid_forget()
	createDeckButtonFrame.grid(row=3, column=0, sticky=W, pady = 4)
	showInfoTextOkButtonFrame.pack_forget()	

def add_to_custom_splitters(splitters_to_add):
	all_splitters = get_custom_splitters()
	all_splitters.append(splitters_to_add)	
	with open('custom_splitters.txt', 'w') as filehandle:
		json.dump(all_splitters, filehandle)
	splitters_var.set('')
	splitters_optionmenu['menu'].delete(0, 'end')
	for splitter_choice in all_splitters:
		splitters_optionmenu['menu'].add_command(label=splitter_choice, command=ttk._setit(splitters_var, splitter_choice))
	setupFrame.grid(row=1, column=0, sticky=W)
	inputSplittersFrame.grid_forget()
	createDeckButtonFrame.grid(row=3, column=0, sticky=W, pady = 4)

def open_add_splitters():
	setupFrame.grid_forget()
	createDeckButtonFrame.grid_forget()
	inputSplittersFrame.grid(row=2, column=0, sticky=W)

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
	USERDATA_.text_filename = youtube_file_name_var.get()
	file_name_label.configure(text=USERDATA_.text_filename)
	file_name_label.update()

def ask_if_should_define():
	USERDATA_.question_type = 'should_define'
	no_words_remaining = True
	for word in USERDATA_.definition_dictionary:
		if USERDATA_.definition_dictionary[word][0] == '!undefined':
			no_words_remaining = False
			USERDATA_.key_in_question = word
			tkprint_create_spacer()
			tkprint("Should we define ' " + word + " '?(y/n)")
			break
	if no_words_remaining:
		tkprint('Do another level of definitions?(y/n)')
		USERDATA_.question_type = 'define_next_level'

def animated_loading(loading_message):
	chars = "/—\\|" 
	for char in chars:
		choose_definitions_text.configure(state="normal")
		choose_definitions_text.delete("end-1l","end")
		choose_definitions_text.insert("end",u"\nLoading..."+char)
		choose_definitions_text.see("end")
		choose_definitions_text.configure(state="disabled")
		root.update_idletasks()      
		time.sleep(.1)
		sys.stdout.flush()

def show_loading_and_definitions():
	word = USERDATA_.key_in_question
	que = queue.Queue()
	getting_definitions_thread = Thread(target=lambda q, arg1: q.put(get_definitions(arg1)), args=(que, word))
	getting_definitions_thread.start()
	choose_definitions_text.configure(state="normal")
	choose_definitions_text.insert("end",u"\n")
	while getting_definitions_thread.isAlive():
		animated_loading('Getting definitions')
	tkprint_delete_lines(1)
	getting_definitions_thread.join()
	definitions = que.get()
	show_definitions(definitions)

def tkprint(text):
	choose_definitions_text.configure(state="normal")
	choose_definitions_text.insert(END,"\n"+text)
	choose_definitions_text.see("end")
	choose_definitions_text.configure(state="disabled")

def clear_tkprint():
	choose_definitions_text.configure(state="normal")	
	choose_definitions_text.delete('1.0', END)
	choose_definitions_text.configure(state="disabled")	

def show_definitions(definitions):
	USERDATA_.select_definition_options = []
	word = USERDATA_.key_in_question
	article = get_text(USERDATA_.text_filename)
	tkprint("Choose definition for ' "+USERDATA_.key_in_question+" '")
	USERDATA_.current_word_usage_sentences = get_words_sentence_from_text(word, article, True)
	if USERDATA_.current_word_usage_sentences:
		tkprint('USAGE:'+' '*30)
	for sentence in USERDATA_.current_word_usage_sentences:
		tkprint(sentence)
	tkprint("1. Change word.")
	tkprint("2. Create your own definition.")
	tkprint("3. Discard word.")
	definition_number = 3
	USERDATA_.definitions_in_question = []
	if definitions:
		for definition in definitions:
			if definition:
				definition_number += 1
				USERDATA_.definitions_in_question.append(definition)
				tkprint((str(definition_number)+'. '+definition[0]))
	for i in range(1,definition_number+1):
		USERDATA_.select_definition_options.append(str(i))
	USERDATA_.question_type = 'select_definition'
	print('USERDATA_.select_definition_options',USERDATA_.select_definition_options)

def ask_for_definition_selection():
	USERDATA_.question_type = 'select_definition'
	definitions = show_loading_and_definitions()

def set_chosen_definition(chosen_definition):
	USERDATA_.definition_dictionary[USERDATA_.key_in_question] = USERDATA_.definitions_in_question[chosen_definition]
	show_chosen_definition(USERDATA_.key_in_question)
	ask_if_should_define()

def ask_for_new_keyword():
	USERDATA_.question_type = 'new_keyword'
	tkprint_create_spacer()
	tkprint("Enter replacement word for ' "+USERDATA_.key_in_question+" ':")

def ask_for_user_definition():
	USERDATA_.question_type = 'input_definition'
	tkprint("Enter definition for ' "+USERDATA_.key_in_question+" ':" )

def tkprint_create_spacer():
	print('end',re.search('[a-zA-Z]', choose_definitions_text.get("end","end")))
	print('end -1l',re.search('[a-zA-Z]', choose_definitions_text.get("end -1l","end")))
	print('end -2l',re.search('[a-zA-Z]', choose_definitions_text.get("end -2l","end")))
	print('end -3l',re.search('[a-zA-Z]', choose_definitions_text.get("end -3l","end")))
	print('end -4l',re.search('[a-zA-Z]', choose_definitions_text.get("end -4l","end")))
	print('end -5l',re.search('[a-zA-Z]', choose_definitions_text.get("end -5l","end")))
	if re.search('[a-zA-Z]', choose_definitions_text.get("end -1l","end")) is None:
		choose_definitions_text.configure(state="normal")
		choose_definitions_text.delete("end","end")
		choose_definitions_text.configure(state="disabled")
	if re.search('[a-zA-Z]', choose_definitions_text.get("end -1l","end")) is not None:
		print('should make spacer')
		tkprint('')

def tkprint_delete_lines(number_of_lines):
	choose_definitions_text.configure(state="normal")
	choose_definitions_text.delete("end-"+str(number_of_lines)+"l","end")
	choose_definitions_text.configure(state="disabled")

def deal_with_user_selection(option):
	usage_lines = 0
	if USERDATA_.current_word_usage_sentences:
		usage_lines = len(USERDATA_.current_word_usage_sentences) + 1
	if option == '1':
		tkprint_delete_lines(len(USERDATA_.definitions_in_question)+usage_lines+4)
		ask_for_new_keyword()
	elif option == '2':
		ask_for_user_definition()
	elif option == '3':
		tkprint_delete_lines(len(USERDATA_.definitions_in_question)+usage_lines+4)
		USERDATA_.definition_dictionary[USERDATA_.key_in_question] = ['!rejected', '!no_alt']
		ask_if_should_define()
	else:
		tkprint_delete_lines(len(USERDATA_.definitions_in_question)+usage_lines+4)
		set_chosen_definition(4-int(option))

def clean_dictionary():
	for word in list(USERDATA_.definition_dictionary):
		if USERDATA_.definition_dictionary[word][0] == '!rejected':
			USERDATA_.definition_dictionary.pop(word)

def create_deck():
	should_autorun = False
	if autorun_var.get() == 1:
		should_autorun = True
	clean_dictionary()
	create_article_anki_deck(USERDATA_.definition_dictionary, USERDATA_.article_text, USERDATA_.text_filename, should_autorun)
	tkprint('Deck created! ('+USERDATA_.text_filename+')')

def create_another_level_of_keywords():
	string_of_definitions = concatenate_all_definitions_to_string(USERDATA_.definition_dictionary)
	add_words_to_dictionary(string_of_definitions)
	no_words_remaining = True
	for word in USERDATA_.definition_dictionary:
		if USERDATA_.definition_dictionary[word][0] == '!undefined':
			no_words_remaining = False
			break
	if no_words_remaining:
		tkprint("No more words to define.")
		create_deck()
	else:
		ask_if_should_define()

def definition_callback():
	user_input = str(choose_definitions_entry_var.get())
	if USERDATA_.question_type == 'should_define':
		if user_input.lower() == 'n':
			USERDATA_.definition_dictionary[USERDATA_.key_in_question] = ['!rejected', '!no_alt']
			tkprint_delete_lines(1)
			ask_if_should_define()
		elif user_input.lower() == 'y':
			tkprint_delete_lines(1)
			ask_for_definition_selection()
		choose_definitions_entry_var.set('')
	elif USERDATA_.question_type == 'select_definition':
		for option in USERDATA_.select_definition_options:
			if user_input == option:
				deal_with_user_selection(option)
		choose_definitions_entry_var.set('')
	elif USERDATA_.question_type == 'define_next_level':
		if user_input.lower() == 'n':
			create_deck()
		elif user_input.lower() == 'y':
			create_another_level_of_keywords()
		else:
			choose_definitions_entry_var.set('')

def show_chosen_definition(key):
	tkprint_create_spacer()
	tkprint(key+" - "+USERDATA_.definition_dictionary[key][0])
	if USERDATA_.current_word_usage_sentences:
		tkprint('USAGE:')
		for sentence in USERDATA_.current_word_usage_sentences:
			tkprint(sentence)
	start = 'end -'+str(len(USERDATA_.current_word_usage_sentences)+3)+'l'
	while 1:
		tag_start = choose_definitions_text.search(key, start, stopindex=END, regexp=True)       
		if not tag_start: break
		tag_end = '%s+%dc' % (tag_start, len(key))
		choose_definitions_text.tag_add('bold', tag_start, tag_end)
		choose_definitions_text.tag_configure('bold', foreground="green",font='TkDefaultFont 9 bold')
		start = tag_start + "+1c"

def enter_pressed_in_entry():	
	user_input = str(choose_definitions_entry_var.get())
	if USERDATA_.question_type == 'new_keyword':
		USERDATA_.key_in_question = user_input
		#tkprint("Define ' "+user_input+" '")
		tkprint_delete_lines(1)
		choose_definitions_entry_var.set('')
		show_loading_and_definitions()
	elif USERDATA_.question_type == 'input_definition':
		usage_lines = 0
		if USERDATA_.current_word_usage_sentences:
			usage_lines = len(USERDATA_.current_word_usage_sentences) + 1
		tkprint_delete_lines(len(USERDATA_.definitions_in_question)+usage_lines+4)
		USERDATA_.definition_dictionary[USERDATA_.key_in_question] = [user_input, '!no_alt']
		tkprint_delete_lines(1)
		show_chosen_definition(USERDATA_.key_in_question)
		choose_definitions_entry_var.set('')
		ask_if_should_define()

def add_words_to_dictionary(text):
	high_freq = float(frequency_high.get())
	src_lang = str(src_language.get())
	words = convert_text_to_keywords(text, high_freq, src_lang)
	for word in words:
		if not word in USERDATA_.definition_dictionary:
			USERDATA_.definition_dictionary[word] = ['!undefined', '!no_alt']

nameAndHelpFrame = Frame(root)
nameAndHelpFrame.grid(row=0, column=0, sticky="ew", pady = 4)
file_name_label = ttk.Label(nameAndHelpFrame, text=USERDATA_.text_filename)
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
src_language = ttk.StringVar(languageFrame)
src_language.set('english')
source_language_optionmenu = ttk.OptionMenu(languageFrame, src_language, *language_choices)
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
splitters_optionmenu.config(width=24)
add_splitters = ttk.Button(splittersFrame, text="+", command=open_add_splitters)
add_splitters.pack(side="left", padx = 4)
remove_spllitters = ttk.Button(splittersFrame, text=" - ", command=remove_from_custom_splitters)
remove_spllitters.pack(side="left", padx = 4)

autorunFrame = Frame(setupFrame)
autorunFrame.pack(fill=X, pady = 4)
autorun_var = IntVar()
autorun_var.set(0)
if platform.system() == 'Windows':
	Checkbutton(setupFrame, text="Auto-run deck file", variable=autorun_var).pack(side="left", padx = 4)

inputSplittersFrame = Frame(root)
inputSplittersFrame.grid_forget()
splitters_to_add = StringVar(inputSplittersFrame, value='')
add_splitters_entry = Entry(inputSplittersFrame, textvariable = splitters_to_add, bd =1, width=entry_width)
add_splitters_entry.pack(anchor=W)
add_splitters_button = ttk.Button(inputSplittersFrame, text="Add", command=lambda : add_to_custom_splitters(splitters_to_add.get()))
add_splitters_button.pack(anchor=W)

showInfoTextOuterFrame = Frame(root)
showInfoTextOuterFrame.grid_forget()

showInfoTextInnerFrame = Frame(showInfoTextOuterFrame)
showInfoTextInnerFrame.pack(fill=X, pady = 4, padx = 8)

scrollbar = Scrollbar(showInfoTextInnerFrame)
scrollbar.pack(side=RIGHT, fill = Y)

choose_definitions_text = ttk.Text(showInfoTextInnerFrame, 
		height = 28,
		width = 55,
		bg = 'black', 
		fg = 'white', 
		borderwidth = 5,
		relief="sunken",
		wrap=ttk.WORD,
		yscrollcommand = scrollbar.set)

choose_definitions_text.insert(END,'Get ready to choose definitions!')
choose_definitions_text.configure(state="disabled")
choose_definitions_text.pack(side='left')
scrollbar.config(command=choose_definitions_text.yview)

showInfoTextOkButtonFrame = ttk.Button(showInfoTextOuterFrame, text="OK", command=hide_info_text)
showInfoTextOkButtonFrame.pack_forget()

chooseDefinitionsEntryFrame = Frame(root)
chooseDefinitionsEntryFrame.grid_forget()

choose_definitions_entry_var = StringVar(chooseDefinitionsEntryFrame, value='')
choose_definitions_entry_var.trace("w", lambda name, index, mode, choose_definitions_entry_var=choose_definitions_entry_var: definition_callback())
choose_definitions_entry = Entry(chooseDefinitionsEntryFrame, 
	textvariable = choose_definitions_entry_var,
	width = entry_width,
	bd =1, 
	bg = 'black', 
	fg = 'white', 
	insertbackground = 'white',
	borderwidth = 5,
	relief="sunken",
	insertwidth = "10")
choose_definitions_entry.pack(side="left", fill=X)
choose_definitions_entry.bind("<Return>", lambda x: enter_pressed_in_entry())

createDeckButtonFrame = Frame(root)
createDeckButtonFrame.grid(row=4, column=0, sticky=W, pady = 4)
create_deck_button = ttk.Button(createDeckButtonFrame, text="Create Deck", command=create_deck_clicked)
create_deck_button.pack(side="left")

root.mainloop()
