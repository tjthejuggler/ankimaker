import sys
import re
import genanki
import time
from wordfreq import zipf_frequency
import requests
from requests.exceptions import HTTPError
if sys.platform == 'linux':
	import getch
else:
	import msvcrt
import wikipediaapi
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
import queue
from threading import Thread
from tkinter import filedialog 
from tkinter import Tk 
import os
from epub_conversion.utils import open_book, convert_epub_to_lines
import os.path
from os import path
import math
from tkinter import *
import tkinter as ttk
from langCodes import *
import subprocess

article_deck = None
lemmatizer = WordNetLemmatizer()
stemmer = SnowballStemmer("english")
wiki_wiki = wikipediaapi.Wikipedia('en')

def get_google_definition(word_to_define):
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

def concatenate_all_definitions_to_string(dictionary):
	dict_value_list = []
	for dict_value in dictionary.values():
		if dict_value != 'rejected!' and dict_value != 'alt word form used.':
			dict_value_list.append(dict_value[0].replace('\n', ' ') + ' ')
	return ''.join(dict_value_list)

def convert_text_to_keywords(text, high_freq, src_lang):
	clean = re.sub(r"[,.'`’'|—;:@#?¿!¡<>_\-\"”“&$\[\]\)\(\\\/]+\ *", " ", text)
	lowerString = clean.lower()
	words = lowerString.split(sep=None)
	print('words c', words)
	keywords = []
	for word in words:
		print('zipf_frequency(word, get_lang_code(src_lang))', zipf_frequency(word, get_lang_code(src_lang)))
		print('high_freq', high_freq)
		if (not word.isdigit() and 
			"/" not in word and
			"\\" not in word and
			len(word) > 1 and
			zipf_frequency(word, get_lang_code(src_lang)) <= high_freq):
				keywords.append(word)
	return keywords

def create_definitions_cards(dictionary, text_filename):
	global article_deck
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
				tags=[text_filename],
				fields=[word + ' ('+str(round(time.time()))+')', dictionary[word][0]])
			article_deck.add_note(my_note)

def get_words_sentence_from_text(word, article_text, show_word):
	all_sentences = article_text.split('.')
	sentences_with_word = []
	for sentence in all_sentences:
		sentence_without_punctuation = re.sub(r"[,.;@#?¿!¡\-\"&$\[\]\)\(]+\ *", " ", sentence)
		if ' ' + word.lower() in sentence_without_punctuation.lower() :
			if len(sentence.split()) > 29:
				split_sentence = sentence.split(' ')
				for i in range(0,len(split_sentence)):
					if word.lower() in split_sentence[i].lower():
						surrounding_words = ''
						for j in range(max(0,i-10),min(i+10,len(split_sentence))):
							if not show_word and i == j:
								word_to_add = '_____'
							else:
								word_to_add = split_sentence[j]
							surrounding_words = surrounding_words + word_to_add + ' '
						sentences_with_word.append('...' + surrounding_words + '...')
			else:
				if not show_word:
					sentence = sentence.replace(word, '_____')
				sentences_with_word.append(sentence + '.')
	return sentences_with_word

def create_fill_in_the_blank_cards(dictionary, article_text, text_filename):
	global article_deck
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
					tags=[text_filename],
					fields=[sentence + ' ('+str(round(time.time()))+')', dictionary[word][1]])
				article_deck.add_note(my_note)

def create_article_anki_deck(dictionary, article_text, text_filename, should_autorun):
	global article_deck
	article_deck = genanki.Deck(round(time.time()),text_filename)
	create_definitions_cards(dictionary, text_filename)
	create_fill_in_the_blank_cards(dictionary, article_text, text_filename)
	genanki.Package(article_deck).write_to_file('ankidecks/'+text_filename+'.apkg')
	cwd = os.getcwd()
	print(cwd)
	if should_autorun:
		os.startfile(cwd+'\\ankidecks\\'+text_filename+'.apkg')
	#os.system(['C:\\Program Files\\Anki\\Anki.exe','ankidecks/'+text_filename+'.apkg'])
	sys.exit()

def get_text(text_filename):
	article_text = ''
	if path.exists('sources/'+text_filename+".txt"):
		with open('sources/'+text_filename+'.txt', encoding="utf8") as file:
			article_text = file.read().replace('\n', ' ')
	elif path.exists('sources/'+text_filename+".epub"):
		book = open_book('sources/'+text_filename+".epub")
		convertedBook = convert_epub_to_lines(book)
		article_text = ' '.join(convertedBook)
	elif path.exists('sources/'+text_filename+".pdf"):
		raw = parser.from_file('sources/'+text_filename+".pdf")
		print(raw['content'])
		article_text = raw['content']
	return article_text








