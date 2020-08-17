import re
from googletrans import Translator
import genanki
import time
from wordfreq import zipf_frequency

start_time = time.time()
translator = Translator()

print_rejected_words = True
print_added = True
print_made_cards = False

#INSTRUCTIONS
#1)copy captions from every episode/the movie into captions.txt
#2)if episodic, put '.ep(episode number).' before each episode
#3)set mediaName as show/movie(name+season)
mediaName = 'showClubDeCuervos3'
#4)create a unique deck ID number
unique_deck_id = 2059290120
#5)create a unique model number if changing the model for some reason
#6)set the langcodes according to the list in langCodes.txt
src_langcode = 'es'
dest_langcode = 'en'
#7)set freq_threshold, higher threshold means more words will be used. (ex:the=7.77,word=5.29,frequency=4.43)
freq_threshold = 7 #7 is probably good for spanish, #10 for turkish
rare_freq_threshold = -1 #1 is probably good for spanish, -1 for turkish

with open(mediaName+'.txt', encoding="utf8") as file:
	subtitle_file = file.read().replace('\n', ' ')

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

episodes = ('ep1','ep2','ep3','ep4','ep5','ep6','ep7','ep8','ep9','ep10','ep11','ep12','ep13','ep14','ep15')

def get_src_words_and_phrases(str):
	src_list = dict()
	rejected_words = []
	current_episode = 'ep1'
	clean = re.sub(r"[,.;@#?¿!¡\-\"&$\[\]]+\ *", " ", str)
	lowerString = clean.lower()
	words = lowerString.split()

	for word in words:
		word.strip()
		if word in episodes:
			current_episode = word
		else:
			if (not word.isdigit() and 
				word not in rejected_words):
					if word in src_list:
						if current_episode not in src_list[word]:
							src_list[word].append(current_episode)
					else:
						word_src_freq = zipf_frequency(word, src_langcode)
						if word_src_freq < freq_threshold:
							if word_src_freq > rare_freq_threshold:
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
		if phrase in episodes:
			current_episode = phrase
		else:
			if len(phrase.split()) > 1 and phrase:
				#print('orig',phrase)
				if phrase in src_list:
					#print('p in src_list', phrase)
					if current_episode not in src_list[phrase]:
						#print('current_episode not in src_list[phrase]:',phrase)
						src_list[phrase].append(current_episode)
				else:
					#print('trans',phrase)
					if print_added == True:
						print('phrase added', phrase)
					src_list[phrase] = [current_episode]
	sortedDict = sorted(src_list.items(), key=lambda x: x[1])
	return sortedDict

def create_deck():
	src_words_and_phrases = get_src_words_and_phrases(subtitle_file)
	print('begin making cards',time.time() - start_time)
	print
	dupe_counter = 0
	translations_counter = 0
	for item in src_words_and_phrases:
		src_text = item[0]
		dest_text = str(translator.translate(src_text, dest=dest_langcode, src=src_langcode).text)
		word_src_freq = 0
		word_dest_freq = 0
		should_make_note = True
		if src_text == dest_text:
			translation_attempt = 1#look into using turkey vpn instead of this sleep
			word_src_freq = zipf_frequency(src_text, src_langcode)
			word_dest_freq = zipf_frequency(src_text, dest_langcode)
			if word_src_freq >= word_dest_freq:
				while translation_attempt < 5:
					time.sleep(translation_attempt)
					dest_text = str(translator.translate(src_text, dest=dest_langcode, src=src_langcode).text)
					if src_text == dest_text:
						translation_attempt += translation_attempt
					else:
						translation_attempt = 5
			else:
				should_make_note = False
				print('rejected because more common in dest:', src_text, word_src_freq,word_dest_freq )
		if should_make_note:
			if src_text == dest_text:
				print('dupe',src_text,word_src_freq,word_dest_freq)
				dupe_counter += 1
			translations_counter += 1
			word_tags = []
			is_sentence = ''
			if len(src_text.split()) > 1:
				is_sentence = 's'
			for tag in item[1]:
				word_tags.append(mediaName+tag+is_sentence)
			my_note = genanki.Note(
				model=my_model,
				tags=word_tags,
				fields=[src_text, dest_text])
			my_deck.add_note(my_note)
			if print_made_cards:
				print(src_text)
				print(dest_text)
				print(word_tags)
	print("dupes",dupe_counter)
	print("translations",translations_counter)
	print("My program took", time.time() - start_time, "to run")
	genanki.Package(my_deck).write_to_file(mediaName+'.apkg')

create_deck()