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
word_freq_title_final = {}
tag_final = {}
document_count = 0
ignore_links = set()
link_analysis = {}

def extract_next_links(soup,url_in):
		outputLinks = list()
		links = soup.find_all('a')
		for tag in links:
			link = tag.get('href')
			if(link != None):
				if(link.startswith("http://") or link.startswith("https://")):
					if link not in outputLinks:
						outputLinks.append(link)
				elif(link.startswith("#") or link.startswith("mailto") or link.startswith("javascript")):
										pass
				elif(link.startswith("/")):
					url  = urlparse(url_in)
					if re.match(".*\.(asp|aspx|axd|asx|asmx|ashx|css|cfm|yaws|swf|xhtml" \
													+ "|jhtmljsp|jspx|wss|do|action|js|pl|php|php4|php3|phtml|py|rb|rhtml|shtml|rss|svg|cgi|dll|whl|ppt|pdf|whl|exe|bed|odc|jpe?g)$",url.path.lower()):
							 index = url.path.rfind("/")
							 parent = url.path[:index]
							 linkis = url.scheme + "://" + url.netloc + parent + link
							 if linkis not in outputLinks:
								outputLinks.append(linkis)
					else:
						linkis = url.scheme + "://" + url.netloc + url.path.rstrip('/')+link
						if linkis not in outputLinks:
						  outputLinks.append(linkis)
				else:
					final_url = urljoin(url_in,link)
					if final_url not in outputLinks:
						outputLinks.append(final_url)
		return outputLinks
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


def LINKindexer():
 with codecs.open("valid_URL.txt","r",encoding='utf8') as fh_book:
	global word_freq_title_final
	global document_count
	global word_freq_final
	global link_analysis
	links = {}
	for line in fh_book:
		info = line.split()
		path = info[0]
		url = info[1].replace('"',"")
		print "Path :" + str(path)
		url = "http:" + url
		if(path == "39/373") or (path == "56/176") or (path == "10/451") or (path == "55/433"):
			print "Pass_bad_URL_hardCode"
			continue
		return_val = is_valid(url)
		if return_val == True:
			if magic.from_file(path).startswith('HTML') or magic.from_file(path).startswith('XML'):
				fh = codecs.open(path,'r',encoding='utf8')
				soup = BeautifulSoup(fh,'lxml')
				outLinks = extract_next_links(soup,url)
				fh.close()
				links[url] = len(outLinks)
			else:
				links[url] = 0


	with codecs.open("links.txt",'w+',encoding='utf8') as file_output:
			file_output.write(json.dumps(links,ensure_ascii=False))
			file_output.write("\n")


LINKindexer()
