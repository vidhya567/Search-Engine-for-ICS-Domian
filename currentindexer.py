
from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import urllib2
import codecs
import requests
import re,os
import string
from urlparse import urlparse, parse_qs ,urljoin
from nltk.stem.porter import *
from nltk.tokenize import RegexpTokenizer
import magic
import json
import math
import operator
word_freq_final = {}
word_freq_title_final = {}
tag_final = {}
document_count = 0
ignore_links = set()
link_analysis = {}
links = set()
PR = {}
links_from_index = {}
page_counts = {}
sorted_PR = {}


def is_valid(url):
	global ignore_links
	parsed = urlparse(url)
	if (url == "http://www.ics.uci.edu/~cs224/"):
		return False
	try:
		returnval =  ".ics.uci.edu" in parsed.hostname \
			and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
			+ "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
			+ "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1|R|Z" \
			+ "|thmx|mso|arff|rtf|jar|csv"\
			+ "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
		if returnval == True:
			if re.match("^.*?(/.+?/).*?\\1.*$|^.*?/(.+?/)\\2.*$", parsed.path.lower()):
				returnval = False
				pass
			else:
				if url in ignore_links:
					returnval =  False
				else:
					returnval = True
					ignore_links.add(url)
		return returnval
	except TypeError:
		print ("TypeError for ", parsed)
		print "TypeError occured"
		return False

def stem_porter(tokens, stemmer):
	stemmed_list = []
	for word in tokens:
		stemmed_list.append(stemmer.stem(word))
	return stemmed_list


def indexer():
 with codecs.open("valid_URL.txt","r",encoding='utf8') as fh_book:
	global word_freq_title_final
	global document_count
	global word_freq_final
	global link_analysis
	outLinks = []
	for line in fh_book:
		info = line.split()
		path = info[0]
		url = info[1]
		print "Path :" + str(path)
		url = "http:" + url
		if(path == "39/373") or (path == "56/176") or (path == "10/451") or (path == "55/433"):
			print "Pass_bad_URL_hardCode"
			continue
		return_val = is_valid(url)
		if return_val == True:
			if magic.from_file(path).startswith('HTML') or magic.from_file(path).startswith('XML'):
				document_count += 1
				fh = codecs.open(path,'r',encoding='utf8')
				soup = BeautifulSoup(fh,'lxml')
				fh.close()
				#TODO comment after first run

				[x.extract() for x in soup.find_all('script')]
				sample_list = soup.get_text().lower()
				#comment next two lines
				outLinks = extract_next_links(soup,url)
				link_analysis[url] = outLinks
			elif magic.from_file(path).startswith('ASCII') or magic.from_file(path).startswith('UTF'):
				document_count += 1
				fh = codecs.open(path,'r',encoding='utf8')
				sample_list = fh.read()
			else:
				continue
			tokenizer = RegexpTokenizer(r'\w+')
			punct_remove = tokenizer.tokenize(sample_list)
			token_list_stopwords = [word for word in punct_remove if not word in stopwords.words('english')]
			stemmer = PorterStemmer()
			stemmed_list = stem_porter(token_list_stopwords, stemmer)
			word_freq = Counter(stemmed_list)
			word_freq_title_final = processTitle(soup,path,stemmed_list)
			tags = processTags(soup,path)
			tag_final = createTagIndex(tags,path,stemmed_list)
			for word in word_freq:
				  # TODO : add check conditions from below
				 if(checkCondition7(word)):
				  indices = [i for i, x in enumerate(stemmed_list) if x == word]
				  length = word_freq[word]
				  totallength = len(word_freq)
				  posting = {}
				  posting["docID"] = path
				  # posting["occurences"] = indices
				  posting["TF"] = length
				  if(word_freq_final.get(word) == None):
					sample_list = list()
					sample_list.append(posting)
					word_freq_final[word] = sample_list
				  else:
					sample_list1 = word_freq_final.get(word)
					sample_list1.append(posting)
					word_freq_final[word] = sample_list1
	writeTitleIndex(word_freq_title_final)
	writeWordIndex(word_freq_final)
	writeLinks(link_analysis)
	writeTagIndex(tag_final)







def getIndex(word):
	with open('INDEXFILE.txt') as data_file:
		data = json.load(data_file)
		scores = data[word]
		for score in scores:
			print score["score"]

def getTitle(word):
	with open('TITLEINDEX.txt') as data_file:
		data = json.load(data_file)
		scores = data[word]
		for score in scores:
			print score["score"]




def processTitle(soup,path,stemmed_list):
		global word_freq_title_final
		if(soup.title is not None):
					if(soup.title.string is not None):
						title = soup.title.string.lower()
						tokenizer = RegexpTokenizer(r'\w+')
						punct_title_remove = tokenizer.tokenize(title)
						title_stopwords = [word for word in punct_title_remove if not word in stopwords.words('english')]
						title_stemmer = PorterStemmer()
						stemmed_list_title = stem_porter(title_stopwords, title_stemmer)
						word_freq_title = Counter(stemmed_list_title)
						dict_pair_title = {}
						for word in word_freq_title:
							indices1 = [i for i, x in enumerate(stemmed_list) if x == word]
							posting = {}
							posting["docID"] = path
							posting["TF"] = word_freq_title[word] + len(indices1)
							if(word_freq_title_final.get(word) == None):
								sample_list_title = list()
								sample_list_title.append(posting)
								word_freq_title_final[word] = sample_list_title
							else:
								sample_list_title = word_freq_title_final.get(word)
								sample_list_title.append(posting)
								word_freq_title_final[word] = sample_list_title
		return word_freq_title_final

def createTagIndex(sample_list,path,other_list):
	global tag_final
	tokenizer = RegexpTokenizer(r'\w+')
	punct_remove = tokenizer.tokenize(sample_list.lower())
	token_list_stopwords = [word for word in punct_remove if not word in stopwords.words('english')]
	stemmer = PorterStemmer()
	stemmed_list = stem_porter(token_list_stopwords, stemmer)
	word_freq = Counter(stemmed_list)
	for word in word_freq:
				  indices2 = [i for i, x in enumerate(other_list) if x == word]
				  length = word_freq[word]
				  posting = {}
				  posting["docID"] = path
				  posting["TF"] = length + len(indices2)
				  if(tag_final.get(word) == None):
					sample_list = list()
					sample_list.append(posting)
					tag_final[word] = sample_list
				  else:
					sample_list1 = tag_final.get(word)
					sample_list1.append(posting)
					tag_final[word] = sample_list1
	return tag_final


def writeTitleIndex(word_freq_title_final):
	with codecs.open("TITLEINDEX.txt",'w+',encoding='utf8') as file_output_title:
		data = {}
		for word in word_freq_title_final:
			post_lists = []
			DF = len(word_freq_title_final[word])
			values =  word_freq_title_final[word]
			for value in values:
				wordcontent ={}
				TF = value["TF"]
				logTF = math.log(1+TF)
				logDF = math.log(float(30397)/(float(DF)))
				score = logTF * logDF
				wordcontent["score"] = score
				wordcontent["docID"] = value['docID']
				post_lists.append(wordcontent)
			data[word] = post_lists
		try:
			file_output_title.write(json.dumps(data,ensure_ascii=False))
			file_output_title.write("\n")
		except UnicodeEncodeError:
			print "Unicode TITLE error"
			print word, word_freq_title_final[word]

def writeTagIndex(tag_final):
	with codecs.open("TAGINDEX.txt",'w+',encoding='utf8') as file_output_title:
		data = {}
		for word in tag_final:
			post_lists = []
			DF = len(tag_final[word])
			values =  tag_final[word]
			for value in values:
				wordcontent ={}
				TF = value["TF"]
				logTF = math.log(1+TF)
				logDF = math.log(float(30397)/(float(DF)))
				score = logTF * logDF
				wordcontent["score"] = score
				wordcontent["docID"] = value['docID']
				post_lists.append(wordcontent)
			data[word] = post_lists
		try:
			file_output_title.write(json.dumps(data,ensure_ascii=False))
			file_output_title.write("\n")
		except UnicodeEncodeError:
			print "Unicode TITLE error"
			print word, word_freq_title_final[word]

def writeWordIndex(word_freq_final):
	with codecs.open("INDEXFILE_7.txt",'w+',encoding='utf8') as file_output:
		data = {}
		for word in word_freq_final:
			post_lists = []
			DF = len(word_freq_final[word])
			values =  word_freq_final[word]
			for value in values:
				wordcontent ={}
				TF = value["TF"]
				logTF = math.log(1+TF)
				logDF = math.log(float(30397)/(float(DF)))
				score = logTF * logDF
				wordcontent["score"] = score
				wordcontent["docID"] = value['docID']
				post_lists.append(wordcontent)
			data[word] = post_lists
		try:
			file_output.write(json.dumps(data,ensure_ascii=False))
			file_output.write("\n")
		except UnicodeEncodeError:
			print "Unicode TITLE error"
			print word, word_freq_final[word]

def writeLinks(link_analysis):
	with codecs.open("test_anchor.txt",'w+',encoding='utf8') as file_output:
	 for word in link_analysis:
		try:
			link = {}
			link["link"] = word
			link["outLinks"] = link_analysis[word]
			link["totalOutLinks"] = len(link_analysis[word])
			json_link = json.dumps(link)
			file_output.write(json.dumps(link,ensure_ascii=False))
			file_output.write("\n")
		except UnicodeEncodeError:
			print "Unicode TITLE error"
			print word, link_analysis[word]


def checkCondition1(word):
	if(ord(word[0]) >= 97 and ord(word[0]) <= 99):
		return True

def checkCondition2(word):
	if(ord(word[0]) >= 100 and ord(word[0]) <= 102):
		return True

def checkCondition3(word):
	if(ord(word[0]) >= 103 and ord(word[0]) <= 106):
		return True

def checkCondition4(word):
	if(ord(word[0]) >= 107 and ord(word[0]) <= 108):
		return True

def checkCondition5(word):
	if(ord(word[0]) >= 109 and ord(word[0]) <= 110):
		return True

def checkCondition6(word):
	if(ord(word[0]) >= 111 and ord(word[0]) <= 113):
		return True

def checkCondition7(word):
	if(ord(word[0]) >= 114 and ord(word[0]) <= 115):
		return True

def checkCondition8(word):
	if(ord(word[0]) >= 116 and ord(word[0]) <= 118):
		return True

def checkCondition9(word):
	if(ord(word[0]) >= 119 and ord(word[0]) <= 122):
		return True

def processTags(soup,path):
		header = ""
		for tags in (soup.findAll("h1")):
			head_words = tags.get_text()
			header+=(head_words)
			header+= " "
		for tags in (soup.findAll("h2")):
			head_words = tags.get_text()
			header+=(head_words)
			header+= " "
		for tags in (soup.findAll("h3")):
			head_words = tags.get_text()
			header+=(head_words)
			header+= " "
		for tags in (soup.findAll("h4")):
			head_words = tags.get_text()
			header+=(head_words)
			header+= " "
		for tags in (soup.findAll("h5")):
			head_words = tags.get_text()
			header+=(head_words)
			header+= " "
		for tags in (soup.findAll("h6")):
			head_words = tags.get_text()
			header+=(head_words)
			header+= " "
		return header






indexer()


