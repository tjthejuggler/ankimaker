import re
from googletrans import Translator
import genanki

from langCodes import *

#INSTRUCTIONS
#1)copy captions from every episode/the movie into captions.txt
#2)if episodic, put ep(episode number) before each episode

#5)create a unique model number if changing the model for some reason

lang_model = genanki.Model(
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

episodes = ('ep1','ep2','ep3','ep4','ep5','ep6','ep7','ep8','ep9','ep10','ep11','ep12')

def word_count(str):
    word_list = dict()
    current_episode = 'ep1'
    clean = re.sub(r"[,.;@#?¿!¡\-\"&$]+\ *", " ", str)
    lowerString = clean.lower()
    words = lowerString.split()

    for word in words:
        if word in episodes:
            current_episode = word
        else:
            if word in word_list:
            	if current_episode not in word_list[word]:
                    word_list[word].append(current_episode)
            else:
                word_list[word] = [current_episode]

    sortedDict = sorted(word_list.items(), key=lambda x: x[1])
    return sortedDict

def reverse_tuple(tuples): 
    new_tup = tuples[::-1] 
    return new_tup

def run_language_program(text_filename, deck, src_lang, dest_lang):
  translator = Translator()
  with open('sources/'+text_filename+'.txt', encoding="utf8") as file:
    data = file.read().replace('\n', ' ')
  toWrite = word_count(data)
  string_to_write = ''
  for item in toWrite:
  	foreign_word = item[0]
  	translation_word = str(translator.translate(item[0], dest=get_lang_code(dest_lang), src=get_lang_code(src_lang)).text)
  	#print(foreign_word + ' ' + translation_word)
  	word_tags = []
  	for tag in item[1]:
  		word_tags.append(text_filename+tag)
  	my_note = genanki.Note(
  		model=lang_model,
  		tags=word_tags,
  		fields=[foreign_word, translation_word])
  	deck.add_note(my_note)
  	print(foreign_word)
  	print(translation_word)
  	print(word_tags)
  genanki.Package(deck).write_to_file(text_filename+'.apkg')