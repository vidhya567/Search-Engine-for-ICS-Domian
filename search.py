
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


#global variables
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
index_result = {}
url_to_path = {}
path_to_url = {}
page_rank = {}
final_result = {}
title_dict = {}
tag_dict ={}
index_dict = {}
url_dict = {}
url_to_path_json = {}
title_check = {}
tag_check = {}
index_check = {}
url_check = {}


def stem_porter(tokens, stemmer):
	stemmed_list = []
	for word in tokens:
		stemmed_list.append(stemmer.stem(word))
	return stemmed_list


def mapURLtoPath():
    global index_result
    global url_to_path
    with open("bookkeeping.json") as data_file:
        data = json.load(data_file)
        for word in index_result:
            url_text = data[word]
            url_to_path[url_text] = word

def mapPathtoURL():
    global index_result
    global path_to_url
    with open("bookkeeping.json") as data_file:
        data = json.load(data_file)
        for word in index_result:
            url_text = data[word]
            path_to_url[word] = url_text

def getIndex(word,input_file):
	global index_result
	global url_to_path_json
	global index_check
##        print "Input_file" + str(input_file)+ word
	with open(input_file) as data_file:
	    data = json.load(data_file)
	    try:
		scores = data[word]
		for score in scores:
			doc_score = score["score"]
			doc_id = score["docID"]
			url_text = url_to_path_json[doc_id]
			if(index_result.get(url_text) == None):
                            index_result[url_text] = (1*doc_score)
                        else:
                            index_result[url_text] += (1*doc_score)
                        index_check[url_text] = 1*doc_score
            except KeyError:
                return 0


def loadFiles():
	global title_dict
	global tag_dict
	global url_dict
	global page_rank
	global url_to_path_json
	with open('TITLEINDEX_new_json.txt') as data_file:
		title_dict = json.load(data_file)
	with open('TAGINDEX.txt') as data_file:
		tag_dict = json.load(data_file)
	with open('URLdata_index_NEW_v4.txt') as data_file:
		url_dict = json.load(data_file)
	with open('FINAL_PR.txt') as data_file:
		page_rank = json.load(data_file)
	with open('bookkeeping.json') as data_file:
		url_to_path_json = json.load(data_file)

def getTitle(word):
	global index_result
	global title_dict
	global url_to_path_json
	global title_check
	total_title_score = 0
	try:
		scores = title_dict[word]
		for score in scores:
			doc_score = score["score"]
			doc_id = score["docID"]
			url_text = url_to_path_json[doc_id]
			total_title_score += doc_score
			if(index_result.get(url_text) == None):
                            index_result[url_text] = 3.0 * doc_score
			else:
                            index_result[url_text] += (3.0 * doc_score)
                        title_check[url_text] = (3.0 * doc_score)

        except KeyError:
                return 0


def getTagIndex(word):
	global index_result
	global tag_dict
	global url_to_path_json
	global tag_check
        try:
			scores = tag_dict[word]
			for score in scores:
				doc_score = score["score"]
				doc_id = score["docID"]
				url_text = url_to_path_json[doc_id]
				if(index_result.get(url_text) == None):
                                    index_result[url_text] = .75 * doc_score
                                else:
                                    index_result[url_text] += (.75 * doc_score)
                                tag_check[url_text] = (.75 * doc_score)

        except KeyError:
                    return 0


def URLdataIndex(word):
	global index_result
	global url_dict
	global url_to_path_json
	global url_check
        try:
                                scores = url_dict[word]
				for score in scores:
					doc_score = score["score"]
					doc_id = score["docID"]
					url_text = url_to_path_json[doc_id]
                                        if(index_result.get(url_text) == None):
                                            index_result[url_text] = 24 * doc_score
                                        else:
                                            index_result[url_text] += (24 * doc_score)
                                        url_check[url_text] = (24 * doc_score)

        except KeyError:
                    return 0


def getLinks():
	global links_from_index
	with open('LINKINDEX_json.txt') as data_file:
		links_from_index = json.load(data_file)



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





def displayResult():
	global final_result
        global title_check
        global tag_check
        global url_check
        global index_check
    	count = 1
    	order = [v[0] for v in sorted(final_result.iteritems(),key=lambda(k, v): (-v, k))]
    	for key in order:
				value = final_result[key]
				print("%d) %s : %s\n" %(count,key,value))
			  	if(title_check.get(key) != None):
					print "Title Check: ", title_check[key]
			  	if(tag_check.get(key) != None):
					print "Tag Check: ", tag_check[key]
			  	if(url_check.get(key) != None):
					print "url Check: ", url_check[key]
			  	if(index_check.get(key) != None):
					print "index Check: ", index_check[key]
				print "count",count
				# break
				count += 1
				if(count > 10):
					break

def mapURLtoPath_json():
    global url_to_path_json
    with open("bookkeeping.json") as data_file:
        data = json.load(data_file)
        for line in data:
            path = line
            url = data[line]
            url_to_path_json[path] = url



def computeFinalResult():
    global index_result
    global page_rank
    global final_result
    for word in index_result:
        page_rank_key= "http://" + word
        final_result[word] = (index_result[word]) + 30*(page_rank[page_rank_key]/(93.804-0.15))






def user_search():
    user_input = input("Enter the query input (Enclose the input in " " ..In Double quotes \n")
    user_input = user_input.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    punct_remove = tokenizer.tokenize(user_input)
    token_list_stopwords = [word for word in punct_remove if not word in stopwords.words('english')]
    stemmer = PorterStemmer()
    stemmed_list = stem_porter(token_list_stopwords, stemmer)
    input_word_freq = Counter(stemmed_list)
    for word in input_word_freq:
    ##    print word
    ##    print "\n"
    ##    print "Normal Index File ****** "
        if(checkCondition1(word)):
            input_index_file = "INDEXFILE_ac.txt"
            getIndex(word,input_index_file)

        elif (checkCondition2(word)):
            input_index_file = "INDEXFILE_df.txt"
            getIndex(word,input_index_file)

        elif (checkCondition3(word)):
            input_index_file = "INDEXFILE_gj.txt"
            getIndex(word,input_index_file)

        elif (checkCondition4(word)):
            input_index_file = "INDEXFILE_kl.txt"
            getIndex(word,input_index_file)

        elif (checkCondition5(word)):
            input_index_file = "INDEXFILE_mn.txt"
            getIndex(word,input_index_file)

        elif (checkCondition6(word)):
            input_index_file = "INDEXFILE_oq.txt"
            getIndex(word,input_index_file)

        elif (checkCondition7(word)):
            input_index_file = "INDEXFILE_rs.txt"
            getIndex(word,input_index_file)

        elif (checkCondition8(word)):
            input_index_file = "INDEXFILE_tv.txt"
            getIndex(word,input_index_file)

        else:
            input_index_file = "INDEXFILE_wz.txt"
            getIndex(word,input_index_file)

    ##    print("Title Index ******")
        getTitle(word)
    ##    print("Tag Index ******")
        getTagIndex(word)
    ##    print("URL data Index ******")
        URLdataIndex(word)


loadFiles()
mapURLtoPath_json()
user_search()
computeFinalResult()
displayResult()


