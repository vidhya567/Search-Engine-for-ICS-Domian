import logging
##from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
##from spacetime_local.IApplication import IApplication
##from spacetime_local.declarations import Producer, GetterSetter, Getter
from lxml import html,etree,cssselect
import re, os
from time import time
from bs4 import BeautifulSoup

try:
    # For python 2
    from urlparse import urlparse, parse_qs ,urljoin
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs

    outputLinks = list()
    outputLinks1 = list()
    ##	for raw in rawDatas:
    raw_content = "http://www.ics.uci.edu/~fowlkes/bioshape/batvis/Viewer/index.html"
    soup = BeautifulSoup(raw_content,"lxml")
    ##		filename6.write(raw.url)
    links = soup.find_all('a')
    for tag in links:
        link = tag.get('href')    
        if(link != None):
            if(link.startswith("http://") or link.startswith("https://")):
                outputLinks.append(link)
                print "http"
                print link
    ##		filename1.write(link)
            elif(link.startswith("#") or link.startswith("mailto") or link.startswith("javascript")):
                print "# JS" + link
    ##		filename2.write(link)
                pass
            elif(link.startswith("/")):
                url  = urlparse(link)
                if re.match(".*\.(asp|aspx|axd|asx|asmx|ashx|css|cfm|yaws|swf|html|htm|xhtml" \
                 + "|jhtmljsp|jspx|wss|do|action|js|pl|php|php4|php3|phtml|py|rb|rhtml|shtml|xml|rss|svg|cgi|dll|whl|exe|pdf|php|)$",url.path.lower()):                     
                        index = url.path.rfind("/")
                        parent = url.path[:index]
                        link = url.scheme + "://" + url.netloc + parent + link
                        print "html "+link
    ##		        filename3.write(link)
                        outputLinks.append(link)
                else:
                        link = url.scheme + "://" + url.netloc + url.path.rstrip('/')+link
                        print "Append_join" + link
    ##			filename4.write(link)
                        outputLinks.append(link)
            else: 
                url = urlparse(link)
                base = url.scheme+"://" + url.netloc + url.path
                final_url = urljoin(base,link)   
                print "Else" + link         
                outputLinks.append(final_url)
    ##		filename5.write(link)			
    ##	return outputLinks1

