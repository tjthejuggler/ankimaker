import genanki
import time

deck = genanki.Deck(round(time.time()),'podFoundmyfitnessCovid2')

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

with open('tempDefinitions.txt', encoding="utf8") as file:
	text = file.read()

#print(text)

lines = text.split('\n')
print(lines)

for line in lines:
	if line:
		print(line)
		word_definition_pair = line.split(' = ')
		print(word_definition_pair)
		my_note = genanki.Note(
			model=definition_model,
			tags='podFoundmyfitnessCovid2',
			fields=[word_definition_pair[0], word_definition_pair[1]])
		deck.add_note(my_note)


genanki.Package(deck).write_to_file('podFoundmyfitnessCovid2.apkg')