
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
links = {}
links_from_index = {}
PR = {}
page_rank = {}


def loadFiles():
	global links
	global links_from_index
	with open('links_json.txt') as data_file:
		links = json.load(data_file)
	with open('InvertedLinkIndex.txt') as data_file:
		links_from_index = json.load(data_file)
	print"Load Finish"

def getCOunts(link):
	global links
	return links[link]


def getOutLinks(link):
		global links_from_index
		if(links_from_index.get(link) == None):
			# print"miss"
			return 0
		else :
			# print len(links_from_index.get(link))
			return links_from_index.get(link)

def computePageRanks():
	global links
	global PR
	initialValue = float(1)/float(30397)
	# initializiation
	# print "links",links
	for link in links:
		PR[link] = initialValue
	print"initializiation DOne"
	for i in range(0,50):
		for link in links:
			print "link",link
			directingLinks = getOutLinks(link)
			score = 0
			if directingLinks != 0:
				for dirlinks in directingLinks:
					score += (float(PR[dirlinks])/float(getCOunts(dirlinks)))
			PR[link] = (0.15) + (0.85)*score
			print PR[link]


def writeRanks():
	global links
	global PR
	data = {}
	for link in links:
		data[link] = PR[link]
	try:
		with codecs.open("FINAL_PR.txt",'w+',encoding='utf8') as file_output:
			file_output.write(json.dumps(data,ensure_ascii=False))
			file_output.write("\n")
	except UnicodeEncodeError:
			print "Unicode TITLE error"
			print word, link_analysis[word]

def loadPR():
		global page_rank
		with open('FINAL_PR.txt') as data_file:
			page_rank = json.load(data_file)

def sortPR():
	for w in sorted(page_rank, key=page_rank.get, reverse=True):
					print(w," ",page_rank[w])
					print("\n")
# loadFiles()
# computePageRanks()
# writeRanks()
loadPR()
sortPR()
