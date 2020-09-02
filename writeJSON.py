import json

# define list with values
splitters = ['ep1,ep2,ep3,ep4,ep5,ep6,ep7,ep8,ep9,ep10,ep11,ep12,ep13,ep14,ep15',
			'BOOK I,BOOK II,BOOK III']

# open output file for writing
with open('custom_splitters.txt', 'w') as filehandle:
    json.dump(splitters, filehandle)