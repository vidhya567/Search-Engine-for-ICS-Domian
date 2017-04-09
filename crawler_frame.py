import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Producer, GetterSetter, Getter
from lxml import html,etree,cssselect
import re, os
from time import time
from bs4 import BeautifulSoup
import codecs
try:
	# For python 2
	from urlparse import urlparse, parse_qs ,urljoin
except ImportError:
	# For python 3
	from urllib.parse import urlparse, parse_qs


logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
url_count = (set() 
	if not os.path.exists("successful_urls.txt") else 
	set([line.strip() for line in open("successful_urls.txt").readlines() if line.strip() != ""]))
MAX_LINKS_TO_DOWNLOAD = 3000

ignore_links = set()
links_extracted = 0
invalid_links = 0
max_url_count = 0
max_url = ""
subdomain_list = dict()

@Producer(ProducedLink)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):

	def __init__(self, frame):
		self.starttime = time()
		# Set app_id <student_id1>_<student_id2>...
		self.app_id = "51125254_54081024"
		# Set user agent string to IR W17 UnderGrad <student_id1>, <student_id2> ...
		# If Graduate studetn, change the UnderGrad part to Grad.
		self.UserAgentString = "IR W17 Grad 51125254 54081024"
		
		self.frame = frame
		assert(self.UserAgentString != None)
		assert(self.app_id != "")
		if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
			self.done = True

	def initialize(self):
		self.count = 0
		l = ProducedLink("http://www.ics.uci.edu", self.UserAgentString)
		print l.full_url
		self.frame.add(l)

	def update(self):
		for g in self.frame.get(OneUnProcessedGroup):
			print "Got a Group"
			outputLinks, urlResps = process_url_group(g, self.UserAgentString)
			for urlResp in urlResps:
				if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
					urlResp.dataframe_obj.bad_url += [self.UserAgentString]
			for l in outputLinks:
				if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
					lObj = ProducedLink(l, self.UserAgentString)
					self.frame.add(lObj)
		if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
			self.done = True

	def shutdown(self):
		print "downloaded ", len(url_count), " in ", time() - self.starttime, " seconds."
		url_time = time() - self.starttime
		average_time = url_time / MAX_LINKS_TO_DOWNLOAD
                file_analytics = codecs.open("analytics_data.txt",'a+',encoding='utf8')
                file_analytics.write('\n' + "Invalid_Links : " + str(invalid_links) + '\n')
                file_analytics.write("URL with Maximum outgoing links : " + max_url + '\t' + "Maximum Links: " + str(max_url_count))
                file_analytics.write('\n' + "Avergae downloaded time per URL :" + str(average_time))
                for key in subdomain_list:
                        file_analytics.write('\n' + "Subdomain: " + key + '\t' + "Subdomain_count " + str(subdomain_list[key]))
                file_analytics.close()
                pass

def save_count(urls):
	global url_count
	urls = set(urls).difference(url_count)
	url_count.update(urls)
	if len(urls):
		with open("successful_urls.txt", "a") as surls:
			surls.write(("\n".join(urls) + "\n").encode("utf-8"))

def process_url_group(group, useragentstr):
	rawDatas, successfull_urls = group.download(useragentstr, is_valid)
	save_count(successfull_urls)
	return extract_next_links(rawDatas), rawDatas
	
#######################################################################################
'''
STUB FUNCTIONS TO BE FILLED OUT BY THE STUDENT.
'''
def extract_next_links(rawDatas):
	outputLinks = list()
	outputLinks1 = list()
	'''
	rawDatas is a list of objs -> [raw_content_obj1, raw_content_obj2, ....]
	Each obj is of type UrlResponse  declared at L28-42 datamodel/search/datamodel.py
	the return of this function should be a list of urls in their absolute form
	Validation of link via is_valid function is done later (see line 42).
	It is not required to remove duplicates that have already been downloaded. 
	The frontier takes care of that.

	Suggested library: lxml
	'''
	
	filename1 = codecs.open("output_http.txt",'a+',encoding='utf8')
	filename2 = codecs.open("output_mailto.txt",'a+',encoding='utf8')
	filename3 = codecs.open("output_append_match.txt",'a+',encoding='utf8')
	filename4 = codecs.open("output_append_join.txt",'a+',encoding='utf8')
	filename5 = codecs.open("output_else.txt",'a+',encoding='utf8')
	filename6 = codecs.open("Input_URL.txt",'a+',encoding='utf8')
	filename7 = codecs.open("count.txt",'a+',encoding='utf8')
	count = 0
	global max_url
	global max_url_count
	global subdomain_list
	for raw in rawDatas:		
		soup = BeautifulSoup(raw.content,"lxml")
		parse =  urlparse(raw.url)
		subdomain_list[parse.netloc] = subdomain_list.get(parse.netloc,0) + 1
                out_links = list()
                
		links = soup.find_all('a')
		for tag in links:
			link = tag.get('href')    
			if(link != None):
				if(link.startswith("http://") or link.startswith("https://")):
					outputLinks.append(link)
					count = count + 1
					out_links.append(link)
				elif(link.startswith("#") or link.startswith("mailto") or link.startswith("javascript")):
                                        pass
				elif(link.startswith("/")):
					url  = urlparse(raw.url)
					if re.match(".*\.(asp|aspx|axd|asx|asmx|ashx|css|cfm|yaws|swf|html|htm|xhtml" \
													+ "|jhtmljsp|jspx|wss|do|action|js|pl|php|php4|php3|phtml|py|rb|rhtml|shtml|xml|rss|svg|cgi|dll|whl|ppt|pdf|whl|exe|txt|bed|odc|jpe?g)$",url.path.lower()):                     
							 index = url.path.rfind("/")
							 parent = url.path[:index]
							 linkis = url.scheme + "://" + url.netloc + parent + link
							 count = count+1
							 outputLinks.append(linkis)
							 out_links.append(linkis)
					else:
						linkis = url.scheme + "://" + url.netloc + url.path.rstrip('/')+link
						count = count+1
						outputLinks.append(linkis)
						out_links.append(linkis)
				else: 
					url = urlparse(raw.url)
					base = url.scheme+"://" + url.netloc + url.path
					final_url = urljoin(base,link)  
					count = count+1      
					# print final_url   
					outputLinks.append(final_url)
					out_links.append(final_url)
		filename7.write(str(count)) 
		filename7.write('\n')
		if(len(out_links) > max_url_count ):
                        max_url_count = len(out_links)
                        max_url = raw.url
	return outputLinks

def is_valid(url):
	'''
	Function returns True or False based on whether the url has to be downloaded or not.
	Robot rules and duplication rules are checked separately.

	This is a great place to filter out crawler traps.
	'''
	
	parsed = urlparse(url)
	global invalid_links
	f1 = codecs.open("Invalid_http.txt",'a+',encoding='utf8')
	f2 = codecs.open("Invalid_directories.txt",'a+',encoding='utf8')
	f3 = codecs.open("Invalid_calendar.txt",'a+',encoding='utf8')
	f4 = codecs.open("Valid_addition.txt",'a+',encoding='utf8')
	f5 = codecs.open("Invalid_REGEX_match.txt",'a+',encoding='utf8')
	f6 = codecs.open("INvalid_count.txt",'a+',encoding='utf8')
	if parsed.scheme not in set(["http", "https"]):
                f1.write(url)
		f1.write('\n')
		invalid_links = invalid_links+1
		return False
	if (url == "http://www.ics.uci.edu/~cs224/"):
                invalid_links = invalid_links + 1
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
                                f2.write(url)
				f2.write('\n')
				returnval = False
				# print"regex match pass"
                                pass				
			else:
				link = parsed.scheme+"://" + parsed.netloc + parsed.path.lstrip("/")
				# print ignore_links
				if link in ignore_links:
					returnval =  False
					f3.write(url)
					f3.write('\n')                                  
										
					# print "ignore_links false"
				else:
					ignore_links.add(link)
					try:
                                                f4.write(url)
                                                f4.write('\n')
					except UnicodeEncodeError:
                                                print "Unicode Error\n"
					returnval = True
		if(returnval == False):
			invalid_links = invalid_links+1;
		f6.write(str(invalid_links))
		f6.write('\n')
		return returnval
	except TypeError:
		print ("TypeError for ", parsed)
