# -*- coding: utf-8 -*-

#start of import list
import urllib
import urllib.request
import urllib.parse
import requests
from bs4 import BeautifulSoup
import pyttsx3
import os
#end of import list





#------------------------------------------------------------------------------
#Working code below
#------------------------------------------------------------------------------
class lainChan():
    
    scriptDIR = os.path.dirname(__file__)
    pic_folder = os.path.join(scriptDIR, 'PICS')
    text_folder = os.path.join(scriptDIR, 'TEXTS')
    pdf_folder = os.path.join(scriptDIR, 'PDFS')
    swf_folder = os.path.join(scriptDIR, 'SWF')
    webm_folder = os.path.join(scriptDIR, 'WEBM')
    gif_folder = os.path.join(scriptDIR, 'GIFS')
    tesfolder = os.path.join(scriptDIR, 'test')
    
    BOARDurl = 'https://www.lainchan.org'
    #def __init__(self):

        #getting program and resouce paths
        #self.scriptDIR = os.path.dirname(__file__)
        #self.pic_folder = os.path.join(self.scriptDIR, 'PICS')
        #self.text_folder = os.path.join(self.scriptDIR, 'TEXTS')
        #self.pdf_folder = os.path.join(self.scriptDIR, 'PDFS')
        #self.swf_folder = os.path.join(self.scriptDIR, 'SWF')
        #self.webm_folder = os.path.join(self.scriptDIR, 'WEBM')
        #self.gif_folder = os.path.join(self.scriptDIR, 'GIFS')
        #self.tesfolder = os.path.join(self.scriptDIR, 'test')

    def after(self,value, a):
        # Find and validate first part.
        pos_a = value.rfind(a)
        if pos_a == -1: return ""
        # Returns chars after the found string.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= len(value): return ""
        return value[adjusted_pos_a:]

    def between(self,value, a, b):
        # Find and validate before-part.
        pos_a = value.find(a)
        if pos_a == -1: return ""
        # Find and validate after part.
        pos_b = value.rfind(b)
        if pos_b == -1: return ""
        # Return middle part.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= pos_b: return ""
        return value[adjusted_pos_a:pos_b]

    def get_boards(self):
        '''
        This will retrieve the boards from the header
        '''
        unformated = []
        formated = []
        
        result = requests.get(lainChan.BOARDurl)
        catalog = result.content
        soup = BeautifulSoup(catalog, 'html5lib')
        links = soup.find_all('a')
        for link in links:
            a = link.get('href')
            if 'index' in a:
                unformated.append(a)
            for item in unformated:
                item = urllib.parse.quote(item)
                item = self.between(item, '/', '/index')
                formated.append(item)
        return unformated, formated    
      

    def get_threads(self, boardNAME):
    
        """
        This extracts the thread catalogue,
        also extracts headers so you can find catalogues of other boards
        """
    
        #url goes here
        url = urllib.request.urlopen(lainChan.BOARDurl +'/'+boardNAME+'/catalog.html')
        #whole html
        catalog = url.read()
        #formated html into BS object
        soup = BeautifulSoup(catalog, 'html5lib')
        threads = []    
        links = soup.find_all('a')
        for link in links:
            a = link.get('href')
            if '/res/' in a:
                threads.append(a)
        return threads



    def get_op_post(self, threads, threadnum):

       """
       This will extract the op post
       """    
    
       link = urllib.parse.quote(threads[threadnum])
       try:
           url2 = urllib.request.urlopen('https://www.lainchan.org/{}'.format(link))
           thread = url2.read()
           soup = BeautifulSoup(thread, 'html5lib')
           thread = soup.findAll("div", {"class": "post op"})
           for item in thread:
               op = item.find('div',{'class':'body'})
           return op.get_text()
       except UnicodeEncodeError:
            print("'ascii' codec can't encode character") 
            pass
       except urllib.error.HTTPError:
            print('Thread is missing, pass')
            pass



    def get_texts_and_resources(self, threads, threadnum):
    
        """
        This will extract thread posts and resourses (images, pdfs etc.)
        """  
    
        texts = []
        resourses = []
        #NUMthreads = len(threads)
        link = urllib.parse.quote(threads[threadnum])
        try:
            url2 = urllib.request.urlopen('https://www.lainchan.org/{}'.format(link))
            thread = url2.read()
            soup = BeautifulSoup(thread, 'html5lib')
            postcontainers = soup.findAll("div", {"class": "postcontainer"})
            NUMposts = len(postcontainers)
            for posts in postcontainers:
                body = posts.findAll('div',{'class':'body'})
                for bodies in body:
                    text = bodies.get_text()
                    texts.append(text)
                    links = soup.find_all('a')
                    for link in links:
                        a = link.get('href')
                        if a != None:
                            if a not in resourses:
                                if '/src/' in a:
                                    if 'http://imgops' not in a and 'http://exif.regex.info/' not in a and 'http://iqdb.org/?url=' not in a:
                                        if '.jpg' in a or '.png' in a or '.pdf' in a:
                                            resourses.append(a)
                                    else: pass
                                else: pass
                            else: pass
                        else:pass
            NUMposts -= 1
        except urllib.error.HTTPError:pass
    #NUMthreads -=1
    #print('Threads remaining: ', NUMthreads)
        return (texts, resourses)
  

    def getresources(self, THresLinks):
    
        '''
        This will download resources into appropriate folders
        '''
    
        remaining = len(THresLinks)
        for res in THresLinks:
            try:
                if '.jpg' in res or '.png' in res or '.gif' in res:
                    if 'http://imgops' not in res and 'http://exif.regex.info/' not in res and 'http://iqdb.org/?url=' not in res:
                        name = self.after(res, 'src/')
                        res = urllib.parse.quote(res)
                        retrieveURL = lainChan.BOARDurl+res
                        urllib.request.urlretrieve(retrieveURL, lainChan.pic_folder+'\{}'.format(name))
                if '.pdf' in res:
                    if 'http://imgops' not in res and 'http://exif.regex.info/' not in res and 'http://iqdb.org/?url=' not in res:
                        name = res[6:]
                        res = urllib.parse.quote(res)
                        retrieveURL = lainChan.BOARDurl+res
                        urllib.request.urlretrieve(retrieveURL, lainChan.pdf_folder+'{}'.format(name))
                else:
                    pass
                remaining -= 1
            except PermissionError:pass
        

    def op_talk(self, texts):
    
        """
        This will voice the thread
        """ 
    
        talker = pyttsx3.init()
        voices = talker.getProperty('voices')
        talker.setProperty('voice', voices[0].id)
        talker.say(texts)
        talker.runAndWait()
        talker.stop()
        
        
    def talk(self, texts, idx):

        """
        This will voice the thread
        """ 
        try:
            talker = pyttsx3.init()
            voices = talker.getProperty('voices')
            talker.setProperty('voice', voices[0].id)
            talker.say(texts[idx])
            talker.runAndWait()
            talker.stop()
        except TypeError:
            if isinstance(texts, str):
                talker = pyttsx3.init()
                voices = talker.getProperty('voices')
                talker.setProperty('voice', voices[0].id)
                talker.say(texts)
                talker.runAndWait()
                talker.stop()
            else:pass

lain = lainChan()    
boardname = lain.get_boards()[1][0]
print(lain.get_threads(boardname))   
                
def spiderchan():
    '''
    retrieves board urls on keyword, filters sit-on domains
    you will need a dictionary txt
    '''
    links = []
    ending = ['.org', '.com']     
    dictionary = ['4','lain']
    #dfile = open('dictionary.txt', 'r')
    #dictionary = dfile.readlines()
    for word in dictionary:
        for adress in ending:
            link = "http://{}chan{}".format(word, adress)  
            try:
                r = requests.get(link)
                soup = BeautifulSoup(r.content, 'html5lib')
                if 'domain' and 'for sale' in soup.prettify():
                    continue
                else:
                    history = r.history
                    for item in history:
                        code = item.status_code
                        if code != 302:
                            links.append(link)
                    else: 
                        continue
            except requests.exceptions.ConnectionError:
                continue
    return links

#print(spiderchan())