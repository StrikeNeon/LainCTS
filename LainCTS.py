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

#getting program and resouce paths
scriptDIR = os.path.dirname(__file__)
pic_folder = os.path.join(scriptDIR, 'PICS')
text_folder = os.path.join(scriptDIR, 'TEXTS')
pdf_folder = os.path.join(scriptDIR, 'PDFS')
gif_folder = os.path.join(scriptDIR, 'GIFS')
tesfolder = os.path.join(scriptDIR, 'test')

def after(value, a):
    # Find and validate first part.
    pos_a = value.rfind(a)
    if pos_a == -1: return ""
    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= len(value): return ""
    return value[adjusted_pos_a:]

def between(value, a, b):
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

#------------------------------------------------------------------------------
#Working code below
#------------------------------------------------------------------------------
class lainChan:
    
    BOARDurl = 'https://www.lainchan.org'


    def after(value, a):
        # Find and validate first part.
        pos_a = value.rfind(a)
        if pos_a == -1: return ""
        # Returns chars after the found string.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= len(value): return ""
        return value[adjusted_pos_a:]

    def between(value, a, b):
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

    def get_boards(BOARDurl):
        '''
        This will retrieve the boards from the header
        '''
        unformated = []
        formated = []
        
        result = requests.get(BOARDurl)
        catalog = result.content
        soup = BeautifulSoup(catalog, 'html5lib')
        links = soup.find_all('a')
        for link in links:
            a = link.get('href')
            if 'index' in a:
                unformated.append(a)
            for item in unformated:
                item = urllib.parse.quote(item)
                item = between(item, '/', '/index')
                formated.append(item)
        return unformated, formated    
      

    def get_threads(BOARDurl, boardNAME):
    
        """
        This extracts the thread catalogue,
        also extracts headers so you can find catalogues of other boards
        """
    
        #url goes here
        url = urllib.request.urlopen(BOARDurl +'/'+boardNAME+'/catalog.html')
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



    def get_op_post(threads, threadnum):

       """
       This will extract the op post
       """    
    
       link = urllib.parse.quote(threads[threadnum])
       print(link)
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



    def get_texts_and_resources(threads, threadnum):
    
        """
        This will extract thread posts and resourses (images, pdfs etc.)
        """  
    
        texts = []
        resourses = []
        #NUMthreads = len(threads)
        link = urllib.parse.quote(threads[threadnum])
        print(link)
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
                                        if '.jpg' in a or '.png' in a or '.pdf' in a or '.gif' in a:
                                            resourses.append(a)
                                    else: pass
                                else: pass
                            else: pass
                        else:pass
            NUMposts -= 1
            print('Posts remaining: ', NUMposts)
        except urllib.error.HTTPError:
            print('Thread is missing, pass')
            pass
    #NUMthreads -=1
    #print('Threads remaining: ', NUMthreads)
        return (texts, resourses)
  

    def getresources(BOARDurl, THresLinks):
    
        '''
        This will download resources into appropriate folders
        '''
    
        remaining = len(THresLinks)
        for res in THresLinks:
            print(res)
            try:
                if '.jpg' in res or '.png' in res:
                    if 'http://imgops' not in res and 'http://exif.regex.info/' not in res and 'http://iqdb.org/?url=' not in res:
                        name = after(res, 'src/')
                        res = urllib.parse.quote(res)
                        retrieveURL = BOARDurl+res
                        urllib.request.urlretrieve(retrieveURL, pic_folder+'\{}'.format(name))
		if '.gif' in res:
                    if 'http://imgops' not in res and 'http://exif.regex.info/' not in res and 'http://iqdb.org/?url=' not in res:
                        name = after(res, 'src/')
                        res = urllib.parse.quote(res)
                        retrieveURL = BOARDurl+res
                        urllib.request.urlretrieve(retrieveURL, gif_folder +'\{}'.format(name))
                if '.pdf' in res:
                    if 'http://imgops' not in res and 'http://exif.regex.info/' not in res and 'http://iqdb.org/?url=' not in res:
                        name = res[6:]
                        res = urllib.parse.quote(res)
                        retrieveURL = BOARDurl+res
                        urllib.request.urlretrieve(retrieveURL, pdf_folder+'{}'.format(name))
                else:
                    pass
                remaining -= 1
                print(remaining)
            except PermissionError:
                print('Permission Denied')
                pass
        

    def op_talk(texts):
    
        """
        This will voice the thread
        """ 
    
        talker = pyttsx3.init()
        voices = talker.getProperty('voices')
        talker.setProperty('voice', voices[0].id)
        talker.say(texts)
        talker.runAndWait()
        talker.stop()
        
        
    def talk(texts, idx):

        """
        This will voice the thread
        """ 
    
        talker = pyttsx3.init()
        voices = talker.getProperty('voices')
        talker.setProperty('voice', voices[0].id)
        for text in texts[:idx]:
            talker.say(text)
            talker.runAndWait()
            talker.stop()

    def ThreadSimulator():
    
        """
        This will run the console program
        """ 
    
        run = True
        start = True
        while start:
            names = lainChan.get_boards(lainChan.BOARDurl)[0]
            boards = lainChan.get_boards(lainChan.BOARDurl)[1]
            print(names)
            print('index got')
            start = False
            command = int(input(''' 
                            select board
                                           
                            COMMAND:  '''))
            if command in range (len(names)):
                boardNAME = boards[command]
                start = False
                while run == True:
                    command = int(input(''' 
                    input command: [1] - scan catalogue
                                   [2] - scan thread
                                   [3] - collect resources
                                   [4] - save thread
                                   [5] - read scanned thread
                                   [6] - select new board
                                   [7] - end operation
                                           
                                COMMAND:  '''))
                    if command == 1:
                        threads = lainChan.get_threads(lainChan.BOARDurl, boardNAME)
                        print(threads)
                    elif command == 2:
                        try:
                            threadnum = int(input('input thread (maxindex = {}): '.format(len(threads))))
                            op_post = lainChan.get_op_post(threads, threadnum)
                            print(op_post)
                            made = False
                            while not made:
                                choice = str(input("Read op post?  "))
                                if choice == 'y' or choice == 'yes':
                                    lainChan.op_talk(op_post)
                                    made = True
                                elif choice == 'n' or choice == 'no':
                                    made = True
                                else: print('illegal')
                            texts = lainChan.get_texts_and_resources(threads,threadnum)[0]
                            print('texts got')
                        except UnboundLocalError:
                            print('no catalogue scanned')
                    elif command == 3:
                        try:
                            resourses = lainChan.get_texts_and_resources(threads, threadnum)[1]
                            lainChan.getresources(lainChan.BOARDurl, resourses)
                            print('resources got')
                        except UnboundLocalError:
                            print('no thread scanned')
                    elif command == 4:
                        try:
                            threadname = between(threads[threadnum], '/res/', '.html')
                            resourses = lainChan.get_texts_and_resources(threads, threadnum)[0]
                            file= open(text_folder+"\{}.txt".format(threadname),"w", encoding="utf-8")
                            op_post = lainChan.get_op_post(threads, threadnum)
                            file.write(op_post)
                            file.write('\n')
                            for post in resourses:
                                file.write(post)
                                file.write('\n')
                            print('text got')
                            file.close()
                        except UnboundLocalError:
                            print('no thread scanned')
                    elif command == 5:
                        try:
                            if texts != None:
                                idx = int(input('input index (maxindex = {}): '.format(len(texts))))
                                print(texts[:idx])
                                lainChan.talk(texts, idx)
                        except UnboundLocalError:
                            print('no thread scanned')
                    elif command == 6:
                        lainChan.ThreadSimulator()
                    elif command == 7:
                        run = False
                    else:
                        print('illegal')
            else: 
                print('out of range')
                lainChan.ThreadSimulator()


#running TS
#board = lainChan
#board.ThreadSimulator()