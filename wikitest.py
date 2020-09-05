from wordfreq import zipf_frequency
import wikipediaapi
import sys

print(zipf_frequency("money", "en"))

wiki_wiki = wikipediaapi.Wikipedia('en')

page = wiki_wiki.page('test')

print(page.summary.partition('.')[0] + '.')


