import re
#from googletrans import Translator
#from translate import Translator
from deep_translator import (GoogleTranslator,MyMemoryTranslator,QCRI,LingueeTranslator)
import genanki
import time
from wordfreq import zipf_frequency
import os
import os.path
from os import path
import sys
import tkinter as ttk
import json

from langCodes import *

start_time = time.time()


#translator = Translator(to_lang="en")

translator_to_use = 'google'

print_rejected_words = True
print_added = True
print_made_cards = False

language_model = genanki.Model(
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

def get_src_words_and_phrases(str,low_freq,high_freq,src_langcode,splitters):
	src_list = dict()
	rejected_words = []
	current_episode = 'ep1'
	episode_count = 0
	clean = re.sub(r"[,.;@#?¿!¡\-\"&$\[\]]+\ *", " ", str)
	lowerString = clean.lower()
	words = lowerString.split()

	for word in words:
		word.strip()
		if word in splitters:
			current_episode = word
			episode_count += 1
		else:
			if (not word.isdigit() and 
				word not in rejected_words):
					if word in src_list:
						if current_episode not in src_list[word]:
							src_list[word].append(current_episode)
					else:
						word_src_freq = zipf_frequency(word, src_langcode)
						if word_src_freq < high_freq:
							if word_src_freq > low_freq:
								src_list[word] = [current_episode]
								if print_added == True:
									print('word added', word)
							else:
								rejected_words.append(word)
								if print_rejected_words == True:
									print('							word too rare', word)
						else:
							rejected_words.append(word)
							if print_rejected_words == True:
								print('				word too common', word)
	current_episode = 'ep1'
	clean_phrases = re.sub(r"[;@#\"&$\[\]]+\ *", " ", str)
	clean_phrases_punct = re.sub(r"[,.;@#?¿!¡\-\"&$]+\ *", ".", clean_phrases)
	phrases = clean_phrases_punct.split(".")
	for phrase in phrases:
		if phrase in splitters:
			current_episode = phrase
		else:
			if len(phrase.split()) > 1 and phrase:
				if phrase in src_list:
					if current_episode not in src_list[phrase]:
						src_list[phrase].append(current_episode)
				else:
					if print_added == True:
						print('phrase added', phrase)
					src_list[phrase] = [current_episode]
	sortedDict = sorted(src_list.items(), key=lambda x: x[1])
	return episode_count, sortedDict

#todo
#look into downloading dictionary and querry that for individual words
#maybe programatically changing vpn is option
#figure out a way to get translations reliably
#	maybe somehow cycling through each one that works will keep them from overloading
#	keeping my own dictionary of definitions that I check first so that repeats don't need to bother servers

def translate(src_text, dest_langcode, src_langcode):
	global translator_to_use
	print('translator_to_use', translator_to_use)
	#check if there is a local .json dictionary
	cwd = os.getcwd()
	local_dict_file = src_langcode+'_'+dest_langcode+'.json'
	dest_text = ''
	if path.exists(cwd+'/local_dictionaries/'+local_dict_file):			
		with open(cwd+'/local_dictionaries/'+local_dict_file) as json_file:
			local_dict = json.load(json_file)
			if src_text in local_dict:
				dest_text = local_dict[src_text]
	if dest_text == '':
		if translator_to_use == 'google':
			translator_to_use = 'linguee'
			try:
				
				print('goog')
				dest_text = GoogleTranslator(source=src_langcode, target=dest_langcode).translate(src_text)
			except:
				pass			
	if dest_text == '':
		if translator_to_use == 'linguee':
			translator_to_use = 'myMemory'
			try:
				
				print('lingue')
				dest_text = LingueeTranslator(source=src_langcode, target=dest_langcode).translate(src_text)
			except:
				pass
	if dest_text == '':
		if translator_to_use == 'myMemory':
			translator_to_use = 'google'
			try:
				
				print('myMemory')
				dest_text = MyMemoryTranslator(source=src_langcode, target=dest_langcode).translate(src_text)
			except:
				pass
	return dest_text


def add_translation_to_local_dictionary(src_text, dest_text, dest_langcode, src_langcode):
	print('add_translation_to_local_dictionary', dest_text)
	cwd = os.getcwd()
	local_dict_file = src_langcode+'_'+dest_langcode+'.json'
	local_dict = {}
	if path.exists(cwd+'/local_dictionaries/'+local_dict_file):			
		with open(cwd+'/local_dictionaries/'+local_dict_file) as json_file:
			local_dict = json.load(json_file)

	if not src_text in local_dict:
		print('!!!',src_text,dest_text)
		local_dict[src_text] = dest_text
		my_json = json.dumps(local_dict)
		f = open(cwd+'/local_dictionaries/'+local_dict_file,"w")
		f.write(my_json)
		f.close()




def get_translation(src_text, dest_langcode, src_langcode):
	#translator = Translator(from_lang=src_langcode,to_lang=dest_langcode)

	# print('get_translation')
	# dest_text_plain = translator.translate(src_text)
	# print('dest_text_plain',dest_text_plain)
	# dest_text = str(translator.translate(src_text, dest=dest_langcode, src=src_langcode).text)
	# print('dest_text',dest_text)
	#dest_text = translator.translate(src_text)
	dest_text = translate(src_text, dest_langcode, src_langcode)
	#translated = GoogleTranslator(source='auto', target='de').translate("keep it up, you are awesome")
	print('dest_text',dest_text)
	word_src_freq = 0
	word_dest_freq = 0
	should_make_note = True
	if src_text == dest_text or dest_text == '':
		translation_attempt = 1#look into using turkey vpn instead of this sleep
		word_src_freq = zipf_frequency(src_text, src_langcode)
		word_dest_freq = zipf_frequency(src_text, dest_langcode)
		if word_src_freq >= word_dest_freq:
			while translation_attempt < 5:
				time.sleep(translation_attempt)
				dest_text = translate(src_text, dest_langcode, src_langcode)
				if src_text == dest_text:
					translation_attempt += translation_attempt
				else:
					translation_attempt = 5
		else:
			should_make_note = False
			print('rejected because more common in dest:', src_text, word_src_freq,word_dest_freq )

	if dest_text != '':	
		add_translation_to_local_dictionary(src_text, dest_text, dest_langcode, src_langcode)

	if not should_make_note:
		dest_text = ''
	return dest_text

def create_anki_note(episode_count, filename, item, src_text, dest_text, dupe_counter, translations_counter, language_deck):
	if src_text == dest_text:
		dupe_counter += 1
	translations_counter += 1
	word_tags = []
	is_sentence = ''
	if len(src_text.split()) > 1:
		is_sentence = 's'
	for tag in item[1]:
		word_tags.append(filename+tag+is_sentence)
	if episode_count == len(item[1]):
		word_tags.append(filename+'AllEp')
	my_note = genanki.Note(
		model=language_model,
		tags=word_tags,
		fields=[src_text + ' ('+str(round(time.time()))+')', dest_text])
	language_deck.add_note(my_note)
	if print_made_cards:
		print(src_text)
		print(dest_text)
		print(word_tags)
	return dupe_counter, translations_counter, language_deck

# def run_language_program(filename, language_deck, src_lang, dest_lang, low_freq, high_freq, splitters, should_autorun):
# 	translator = Translator()
# 	src_langcode = get_lang_code(src_lang)
# 	dest_langcode = get_lang_code(dest_lang)
# 	with open('sources/'+filename+'.txt', encoding="utf8") as file:
# 		data = file.read().replace('\n', ' ')
# 	episode_count, src_words_and_phrases = get_src_words_and_phrases(data, low_freq, high_freq, src_langcode, splitters)
# 	print('begin making cards',time.time() - start_time)
# 	dupe_counter = 0
# 	translations_counter = 0
# 	for item in src_words_and_phrases:
# 		src_text = item[0]
# 		dest_text = get_translation(src_text, dest_langcode, src_langcode)
# 		if dest_text:
# 			dupe_counter, translations_counter, language_deck = create_anki_note(episode_count, filename, item, src_text, dest_text, dupe_counter, translations_counter, language_deck)
# 	print("dupes",dupe_counter)
# 	print("translations",translations_counter)
# 	print("My program took", time.time() - start_time, "to run")
# 	genanki.Package(language_deck).write_to_file('ankidecks/'+filename+'.apkg')
# 	if should_autorun:
# 		cwd = os.getcwd()
# 		os.startfile(cwd+'\\ankidecks\\'+filename+'.apkg')
# 	sys.exit()