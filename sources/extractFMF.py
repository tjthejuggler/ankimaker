import requests
from lxml import html
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import os.path
from os import path
import json

folder = 'podFoundMyFitness/'

def scrapeURLS():
	with open('helpers/foundmyfitnessEpsArchive.txt', encoding="utf8") as file:
		fullDoc = file.read()
	splitDoc = fullDoc.split('<a href="/episodes/')
	urls = []
	for chunk in splitDoc:
		urlEnding = chunk.split('"')
		urls.append('https://www.foundmyfitness.com/episodes/'+urlEnding[0])
		page = requests.get('https://www.foundmyfitness.com/episodes/'+urlEnding[0])
	with open('foundmyfitnessEpsArchiveURLS.txt', 'w') as f:
		f.write(json.dumps(urls))	
	return urls

def getURLSfromJSON():
	urls = []
	with open('helpers/foundmyfitnessEpsArchiveURLS.txt', 'r') as f:
		urls = json.loads(f.read())
	return urls

def getTranscriptions(urls):
	for url in urls:
		namePrefix = "podFoundMyFitness"
		name = url.replace('https://www.foundmyfitness.com/episodes/','').capitalize()
		fullName = namePrefix + name
		if not path.exists(folder+fullName+".txt"):
			chromedriver = 'C:\\Program Files\\chromedriver\\chromedriver.exe' 
			options = webdriver.ChromeOptions()
			options.add_argument('headless')
			#options.add_argument('window-size=1200x600') 
			browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options) 
			browser.get(url)
			html = browser.page_source
			if 'episode_tabs-content' in html:
				html2 = html.split('episode_tabs-content">')[1]
				html3 = html2.split("container episode_supporter-call")[0]
				soup = BeautifulSoup(html3)
				text = soup.get_text()
				print(text)
				fileToWrite = open(folder+fullName+".txt","w+", encoding="utf8")
				fileToWrite.write(text)
				fileToWrite.close()
			browser.quit()

def main():
	#urls = scrapeURLS()
	urls = getURLSfromJSON()
	print(urls)
	getTranscriptions(urls)

main()