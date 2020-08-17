import re
from googletrans import Translator
import genanki

#INSTRUCTIONS
#1)copy captions from every episode/the movie into captions.txt
#2)if episodic, put ep(episode number) before each episode
#3)set mediaName as show/movie(name+season)
mediaName = 'showHighSeas3'
#4)create a unique deck ID number
unique_deck_id = 2059290113
#5)create a unique model number if changing the model for some reason
#6)set langcode according to the list here: https://py-googletrans.readthedocs.io/en/latest/
langcode = 'es'

my_model = genanki.Model(
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

my_deck = genanki.Deck(unique_deck_id,mediaName)

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

with open('captions.txt', encoding="utf8") as file:
    data = file.read().replace('\n', ' ')

translator = Translator()
toWrite = word_count(data)
string_to_write = ''
for item in toWrite:
	foreign_word = item[0]
	translation_word = str(translator.translate(item[0], dest='en', src=langcode).text)
	#print(foreign_word + ' ' + translation_word)
	word_tags = []
	for tag in item[1]:
		word_tags.append(mediaName+tag)
	my_note = genanki.Note(
		model=my_model,
		tags=word_tags,
		fields=[foreign_word, translation_word])
	my_deck.add_note(my_note)
	print(foreign_word)
	print(translation_word)
	print(word_tags)

#print(string_to_write)
genanki.Package(my_deck).write_to_file(mediaName+'.apkg')