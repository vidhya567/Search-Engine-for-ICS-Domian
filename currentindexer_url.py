
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
word_freq_final = {}
word_freq_url_final = {}
word_freq_title_final = {}
document_count = 0
ignore_links = set()
link_analysis = {}

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
				link = parsed.scheme+"://" + parsed.netloc + parsed.path.lstrip("/")
				if link in ignore_links:
					returnval =  False
				else:
					returnval = True
					ignore_links.add(link)		
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
 with codecs.open("valid_URL_json.txt","r",encoding='utf8') as fh_book:
	global word_freq_title_final
	global document_count
	global word_freq_final
	global link_analysis
	outLinks = []
	data = json.load(fh_book)
##	data = {}
##	data["56/228"] = "//www.ics.uci.edu/~lopes/teaching/inf102S14"
##	data["67/16"]  = "//www.ics.uci.edu/~lopes/aop/aop.html"
##	data["20/58"]  = "//www.ics.uci.edu/~lopes"
	for line in data:
		file_path = line
                url = data[line]
		print "Path :" + str(file_path)
		url = "http:" + url
		if(file_path == "39/373") or (file_path == "56/176") or (file_path == "10/451") or (file_path == "55/433"):
			print "Pass_bad_URL_hardCode"
			continue
##		return_val = is_valid(url)
##		print "Return_val: " + str(return_val)
##		if return_val == True:
                if magic.from_file(file_path).startswith('HTML') or magic.from_file(file_path).startswith('XML'):
                                pass
		elif magic.from_file(file_path).startswith('ASCII') or magic.from_file(file_path).startswith('UTF'):
                                pass
		else:
				continue
		urlpath = url.replace("/"," ").replace("."," ").replace("http", " ")	
##		parse = urlparse(url)
##                index = parse.path.rfind('/')
####                print "Path, index", parse.path, index
##                if(index != 0):
##                        parent = parse.path[:index]
####                print "Parent", parent
####                        print "Netloc: " + str(parse.netloc)
####                        print "Parent: " + str(parent)
##                        urlpath = parse.netloc + parent
####                print "Before replace", urlpath
##                        urlpath = urlpath.replace("/"," ").replace("."," ")
####                print "After replace", urlpath
####                        print "path: " + str(urlpath)
####                        raw_input("Enter a key **** ")
####                print "Before ", urlpath
##                else:
##                        urlpath = url.replace("/"," ").replace("."," ").replace("http", " ")
####                        print "Urlpath....ELSE", urlpath
                urldata= processURL(file_path,urlpath)
##                        for word in urldata:
##                            print word, urldata[word]
##                            print "\n"
                            
                                                                           
##        writeTitleIndex(word_freq_title_final)
##	# writeWordIndex(word_freq_final)
##	#FwriteLinks(link_analysis)
        writeURLdata(urldata)
##        raw_input("Enter a key")


					    
def getURL(word):
	with open('URLdata_index_NEW_v4.txt') as data_file:    
		data = json.load(data_file)
		scores = data[word]
		for score in scores:
			print score["score"]
			print score["docID"]


def processURL(path,urlpath):
    global word_freq_url_final
##    print "ProcessURL"
##    print path, urlpath
    tokenizer = RegexpTokenizer(r'\w+')
    punct_url_remove = tokenizer.tokenize(urlpath)
    url_stopwords = [word for word in punct_url_remove if not word in stopwords.words('english')]
    url_stemmer = PorterStemmer()
    stemmed_list_url = stem_porter(url_stopwords, url_stemmer)
    word_freq_url = Counter(stemmed_list_url)
    dict_pair_url = {}
    for word in word_freq_url:
        indices1 = [i for i, x in enumerate(stemmed_list_url) if x == word]
        posting = {}
        posting["docID"] = path
        posting["TF"] = float(word_freq_url[word])/float(len(word_freq_url))
##        print "ProcessURL", word_freq_url[word], len(word_freq_url)
        if(word_freq_url_final.get(word) == None):
                sample_list_url = list()
                sample_list_url.append(posting)
                word_freq_url_final[word] = sample_list_url
        else:
                sample_list_url = word_freq_url_final.get(word)
                sample_list_url.append(posting)
                word_freq_url_final[word] = sample_list_url
##    print word_freq_url_final
    return word_freq_url_final

def processTitle(soup,path,stemmed_list):
		global word_freq_title_final
##		posting = {}
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
							posting["TF"] = word_freq_title[word]/len(word_freq_title)
							if(word_freq_title_final.get(word) == None):
								sample_list_title = list()
								sample_list_title.append(posting)
								word_freq_title_final[word] = sample_list_title
							else:
								sample_list_title = word_freq_title_final.get(word)
								sample_list_title.append(posting)
								word_freq_title_final[word] = sample_list_title
		return word_freq_title_final
		


def writeURLdata(urldata):
    with codecs.open("URLdata_index_NEW_v4.txt",'w+',encoding='utf8') as file_output_title: 
		data = {}               
		for word in urldata:
			post_lists = []      
			DF = len(urldata[word])
##			print "writeURLdata DF WORD ", DF, word
			values =  urldata[word]
			for value in values:
				wordcontent ={}
				TF = value["TF"]
##				print "Values", value
##				print "TF", TF
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
			print word, urldata[word]



indexer()
# getIndex("group")
##getIndex("credit")
##getURL("lope")
#urlpaths = "www ics uci edu ~lopes"
##processURL("20/58",urlpaths)
