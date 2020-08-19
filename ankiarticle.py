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

from langCodes import *

article_deck = None
text_filename = ''
lemmatizer = WordNetLemmatizer()
stemmer = SnowballStemmer("english")
wiki_wiki = wikipediaapi.Wikipedia('en')

def get_google_definition(word_to_define):
	#print('getD',word_to_define)
	first_definition = ''
	try:
		response = requests.get('https://api.dictionaryapi.dev/api/v1/entries/en/'+word_to_define)
		response.raise_for_status()
		jsonResponse = response.json()
		values_view = jsonResponse[0]['meaning'].values()
		value_iterator = iter(values_view)
		first_value = next(value_iterator)
		values_view = first_value[0].values()
		value_iterator = iter(values_view)
		first_definition = next(value_iterator)
	except HTTPError as http_err:
	    pass
	except Exception as err:
	    pass
	return (first_definition)

def get_wikipedia_summary(word_to_define):
	to_return = ''
	page = wiki_wiki.page(word_to_define)
	if page.exists():
		to_return = page.summary.partition('.')[0] + '.'
	return to_return

def get_definitions(word):
	word_forms = []
	word_forms.append(word)
	word_forms.append(stemmer.stem(word))
	word_forms.append(lemmatizer.lemmatize(word))
	if word_forms[0] and word_forms[0][-1] == 's':
		word_forms.append(word_forms[0][:-1])	
	if word_forms[1] and word_forms[1][-1] == 't' or word_forms[1][-1] == 's':
		word_forms.append(word_forms[1]+'ion')
	word_forms = list(dict.fromkeys(word_forms)) #remove duplicates from list
	definitions = []
	for word_form in word_forms:
		if word_form:
			wiki_def = get_wikipedia_summary(word_form).lower().replace('\n', ' ')
			if ' is ' in wiki_def:
				wiki_def = wiki_def.split('is ',1)[1].capitalize()
			if wiki_def and 'may refer to:' not in wiki_def:
				definitions.append([wiki_def,word_form])
			google_def = get_google_definition(word_form)
			if google_def:
				definitions.append([google_def,word_form])
	return definitions

def show_definitions(word, definitions, article):
	sentences = get_words_sentence_from_text(word, article, True)
	if sentences:
		print('\rUSAGE:',' '*30)
	for sentence in sentences:
		print(sentence+'\n')
	definition_number = 0
	if definitions:
		for definition in definitions:
			if definition:
				definition_number += 1
				if definition_number == 1:
					print('\r'+str(definition_number)+'. '+definition[0])
				else:
					print(str(definition_number)+'. '+definition[0])
	if definition_number == 0:
		print('\r'+str(definition_number+1)+'. Create your own definition.               ')
	else:
		print(str(definition_number+1)+'. Create your own definition.               ')
	print(str(definition_number+2)+'. Change word.')
	print(str(definition_number+3)+'. Discard word.')	

def concatenate_all_definitions_to_string(dictionary):
	dict_value_list = []
	for dict_value in dictionary.values():
		if dict_value != 'rejected!' and dict_value != 'alt word form used.':
			dict_value_list.append(dict_value[0].replace('\n', ' ') + ' ')#pretty sure this will have fixed my problem
	return ''.join(dict_value_list)

def animated_loading(loading_message):
    chars = "/—\\|" 
    for char in chars:
        sys.stdout.write('\r'+loading_message+'...'+char)          
        time.sleep(.1)
        sys.stdout.flush()

def convert_text_to_keywords(text, low_freq, src_lang):
	clean = re.sub(r"[,.;@#?¿!¡\-\"&$\[\]\)\(]+\ *", " ", text)
	lowerString = clean.lower()
	words = lowerString.split()
	keywords = []
	for word in words:
		print('lowf', word, zipf_frequency(word, get_lang_code(src_lang)))

		if (not word.isdigit() and 
			"/" not in word and
			"\\" not in word and
			len(word) > 1 and
			zipf_frequency(word, get_lang_code(src_lang)) < low_freq):
				print('keyw', word)
				keywords.append(word)
	return keywords

def show_loading_and_get_definitions(word):
	que = queue.Queue()
	getting_definitions_thread = Thread(target=lambda q, arg1: q.put(get_definitions(arg1)), args=(que, word))
	getting_definitions_thread.start()
	while getting_definitions_thread.isAlive():
		animated_loading('Getting definitions')
	getting_definitions_thread.join()
	definitions = que.get()
	return definitions

def get_user_definition_decision_int(definitions):
	possible_definition_decisions = []
	for i in range(len(definitions)+3):
		possible_definition_decisions.append(str(i+1))					
	user_definition_decision = ''
	while user_definition_decision not in possible_definition_decisions:
		try:
			user_definition_decision = msvcrt.getch().decode('ASCII') #ignore inputs that are not an appropriate number
		except:
			pass
	return int(user_definition_decision)

def get_users_definition_decision(word, article):
	word_definition = ''
	word_is_rejected = False
	while word_definition == '' and not word_is_rejected:	
		definitions = show_loading_and_get_definitions(word)
		show_definitions(word, definitions, article)
		word_definition = ''
		word_is_rejected = False
		user_definition_decision_int = get_user_definition_decision_int(definitions)
		if user_definition_decision_int-1 == len(definitions):
			print("Input definition:")
			word_definition = [input(), word]
			if not word_definition:
				word_is_rejected = True
				continue
		elif user_definition_decision_int-2 == len(definitions):									
			word = ''
			while not word:
				print("Input other word form:")
				word = input()
			continue						
		elif user_definition_decision_int-3 == len(definitions):
			word_is_rejected = True
			continue							
		else:
			word_definition = definitions[int(user_definition_decision_int)-1]

	return word_definition, word_is_rejected, word

def build_dictionary_with_user(dictionary, text, original_article, low_freq, src_lang):
	words = convert_text_to_keywords(text, low_freq, src_lang)
	more_words_to_define = False
	for word in words:
		if word not in dictionary:			
			print(" \nShould we define ' " + word + " '?(y/n)")
			user_decided_to_define = False
			while user_decided_to_define == False:
				try:
					users_decision_to_define = msvcrt.getch().decode('ASCII')
				except:
					pass
				if users_decision_to_define.upper() == 'Y':
					user_decided_to_define = True
					word_definition, word_is_rejected, word = get_users_definition_decision(word, original_article)
					if word_is_rejected:
						dictionary[word] = 'rejected!'
					elif word_definition:
						dictionary[word_definition[1]] = [word_definition[0], word]
						if word_definition[1] != word:
							dictionary[word] = 'alt word form used.'
						more_words_to_define = True
				elif users_decision_to_define.upper() == 'N':
					user_decided_to_define = True
					dictionary[word] = 'rejected!'
					word_is_rejected = True
		else:
			if not dictionary[word]:
				dictionary[word] = 'rejected!'
	return dictionary, more_words_to_define

def create_definitions_cards(dictionary):
	definition_model = genanki.Model(
		1607392319,
		'Simple Model',
		fields=[
			{'name': 'Question'},
			{'name': 'Answer'},
		],
		templates=[
			{
				'name': 'Card 1',
				'qfmt': '{{Question}}',
				'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
			},
			{
				'name': 'Card 2',
				'qfmt': '{{Answer}}',
				'afmt': '{{FrontSide}}<hr id="answer">{{Question}}',
			}
		])	

	for word in dictionary:
		if dictionary[word] != 'rejected!' and dictionary[word] != 'alt word form used.':
			my_note = genanki.Note(
				model=definition_model,
				tags=text_filename,
				fields=[word, dictionary[word][0]])
			article_deck.add_note(my_note)

def get_words_sentence_from_text(word, article_text, show_word):
	#article_text = article_text.lower()
	all_sentences = article_text.split('.')
	sentences_with_word = []
	for sentence in all_sentences:
		sentence_without_punctuation = re.sub(r"[,.;@#?¿!¡\-\"&$\[\]\)\(]+\ *", " ", sentence)
		if ' ' + word+ ' ' in sentence_without_punctuation.lower() :
			if not show_word:
				sentence = sentence.replace(word, '_____')
			sentences_with_word.append(sentence + '.')
	return sentences_with_word

def create_fill_in_the_blank_cards(dictionary, article_text):
	definition_model = genanki.Model(
		1607392320,
		'Simple Model',
		fields=[
			{'name': 'Question'},
			{'name': 'Answer'},
		],
		templates=[
			{
				'name': 'Card 1',
				'qfmt': '{{Question}}',
				'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
			}
		])	

	for word in dictionary:
		if dictionary[word] != 'rejected!' and dictionary[word] != 'alt word form used.':
			sentences_with_word = get_words_sentence_from_text(dictionary[word][1], article_text, False)
			for sentence in sentences_with_word:
				my_note = genanki.Note(
					model=definition_model,
					tags=text_filename,
					fields=[sentence, dictionary[word][1]])
				article_deck.add_note(my_note)

def create_anki_deck(dictionary, article_text, filename):
	create_definitions_cards(dictionary)
	create_fill_in_the_blank_cards(dictionary, article_text)
	genanki.Package(article_deck).write_to_file('ankidecks/'+filename+'.apkg')

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

def set_global_variables(deck, src_lang):
	global article_deck
	article_deck = deck
	global stemmer
	try:
		stemmer = SnowballStemmer(src_language)
	except:
		stemmer = SnowballStemmer('english')
	global wiki_wiki
	wiki_wiki = wikipediaapi.Wikipedia(get_lang_code(src_lang))

def run_article_program(filename, deck, src_lang, low_freq):
	text_filename = filename
	set_global_variables(deck, src_lang)
	complete_dictionary = dict()
	with open('sources/'+text_filename+'.txt', encoding="utf8") as file:
		article_text = file.read().replace('\n', ' ')
	complete_dictionary, more_words_to_define = build_dictionary_with_user(complete_dictionary, article_text, article_text, low_freq, src_lang)
	still_building_dictionary = True
	while still_building_dictionary and more_words_to_define:
		print(" \nDefine keywords from next level of definitions?(y/n)")
		user_decision_definition_made = False
		while user_decision_definition_made == False:
			try:
				user_decision_definition = msvcrt.getch().decode('ASCII')
			except:
				pass
			if user_decision_definition.upper() == 'Y':
				user_decision_definition_made = True
				string_of_definitions = concatenate_all_definitions_to_string(complete_dictionary)
				dictionary_additions, more_words_to_define = build_dictionary_with_user(complete_dictionary, string_of_definitions, article_text, low_freq, src_lang)
				complete_dictionary = {**complete_dictionary, **dictionary_additions}
			elif user_decision_definition.upper() == 'N':
				user_decision_definition_made = True
				still_building_dictionary = False
	create_anki_deck(complete_dictionary, article_text, filename)
	for word in complete_dictionary:
		if complete_dictionary[word] != "rejected!" and complete_dictionary[word] != 'alt word form used.':
			print('\n',word.upper(), '=', complete_dictionary[word][0])
	print('\n','Deck created:',text_filename)

