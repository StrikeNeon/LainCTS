import npyscreen
import threading
import LainCTS_v1 as Lain

dictionary = {0:'%CE%BB',
              1:'%CE%94',
              2:'sec',
              3:'inter',
              4:'lit',
              5:'music',
              6:'vis',
              7:'hum',
              8:'drug',
              9:'zzz',
              10:'layer',
              11:'q',
              12:'r',
              13:'culture',
              14:'psy',
              15:'mega',
              16:'random'}

CTS = Lain.lainChan()

class App(npyscreen.NPSAppManaged):
    
    def onStart(self):
        
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm("MAIN", MainForm, name="LainCTS")
        self.addForm("OP", OPForm, name="Operations")
        
class SelectOneBox(npyscreen.BoxTitle):
    # SelectOne is now boxed
    _contained_widget = npyscreen.SelectOne

class SelectMultyBox(npyscreen.BoxTitle):
    # MultiSelect is now boxed
    _contained_widget = npyscreen.MultiSelect

class OutputBox(npyscreen.BoxTitle):
    # MultiLineEdit is now boxed
    _contained_widget = npyscreen.MultiLineEdit 


class MainForm(npyscreen.ActionForm):
    # constructor
    def create(self):

    # TitleText/TitleSelectOne added to the form
        self.title = self.add(npyscreen.TitleText, name="Press ok to begin")
        self.boards = self.add(npyscreen.TitleSelectOne, scroll_exit=True, name='Choose board', values = CTS.get_boards()[0])
    # cancel method
    def on_cancel(self):
        ok_cancel = npyscreen.notify_yes_no("Are you sure you want to exit?", "Warning", editw=2)
        if ok_cancel:
            if ok_cancel:
                self.parentApp.setNextForm(None)
        else:
            self.parentApp.setNextFormPrevious
        
    # ok method
    def on_ok(self):
        try:
            Operations = self.parentApp.getForm("OP")
            Operations.board = dictionary[self.boards.value[0]]
            self.parentApp.switchForm("OP")
        except IndexError:
            Operations = self.parentApp.getForm("OP")
            Operations.board = dictionary[0]
            self.parentApp.switchForm("OP")
        
class OPForm(npyscreen.ActionForm): 

    def create(self):
        self.y, self.x = self.useable_space()
        self.selected = False
        self.TBRead = False
        self.board = None
        self.threads = []
        self.texts = []
        self.resources = []
        self.output = ''
        self.OPBox = self.add(SelectOneBox,
                         scroll_exit=True,
                         name="Operations",
                         custom_highlighting=True,
                         values=["scan cataloge"], 
                         rely=self.y // 15,
                         max_width=self.x // 2 - 5,
                         max_height=self.y // 5)
        
        self.OUTBox = self.add(OutputBox,
                          scroll_exit=True,
                          name="Output",
                          relx=self.x // 2,
                          rely=2)
        
    def resource(self, threadnum):
          resources = CTS.get_texts_and_resources(self.threads, threadnum)[1]
          CTS.getresources(resources) 
          return resources
      
    def on_ok(self):
    
        try:

            # scan cataloge scenario
            if self.OPBox.value[0] == 0:
                self.threads = CTS.get_threads(self.board)
                for i in self.threads:
                    self.output += (i+"\n")
                self.OUTBox.value = self.output + "Cataloge Scanned"
                self.OPBox.values = ["scan cataloge","dump resources","scan thread"]
                if not self.selected:
                    self.threadselect = self.add(SelectOneBox,
                         scroll_exit=True,
                         name="Threads",
                         custom_highlighting=True,
                         values=self.threads, 
                         rely=self.y // 4,
                         max_width=self.x // 2 - 5,
                         max_height=self.y // 4)
                    self.selected = True
                else:pass
            
            #resource dump scenario 
            elif self.OPBox.value[0] == 1:
                threads = self.threads
                i = len(threads)
                while i > 0:
                    t1 = threading.Thread(target = self.resource, args = (i,))
                    t2 = threading.Thread(target = self.resource, args = (i,))
                    t1.start()
                    t2.start()
                    t1.join()
                    i-=1
                    t2.join()
                    i-=1

            # scan thread scenario
            elif self.OPBox.value[0] == 2:
                try:
                    threadnum = self.threadselect.value[0] 
                    self.output = ("OP Post" + "\n" + 
                                   CTS.get_op_post(self.threads,
                                                   threadnum) + "\n\n") 
                    self.texts = CTS.get_texts_and_resources(self.threads,
                                                             threadnum)[0]
                    self.output = ''
                    for i in self.texts:
                        self.output += (i+"\n")
                    self.OPBox.values = ["scan cataloge","dump resources", "scan thread","collect resources","save thread", "read scanned thread"]
                    self.OUTBox.value = self.output + "Thread Scanned"
                except IndexError:
                    self.OUTBox.value = "No Thread Selected"
            
            #resource collector scenario
            elif self.OPBox.value[0] == 3:
                try:
                    threadnum = self.threadselect.value[0] 
                    self.resource(threadnum)
                    self.output = ''
                    for i in self.resources:
                        self.output += (i+"\n")
                    self.OUTBox.value = self.output + "Resources Collected"
                except IndexError:
                    self.OUTBox.value = "No Thread Selected"
            
            #text archival scenario        
            elif self.OPBox.value[0] == 4:
                try:
                    threadnum = self.threadselect.value[0] 
                    threadname = CTS.between(self.threads[threadnum], '/res/', '.html')
                    self.texts = CTS.get_texts_and_resources(self.threads, threadnum)[0]
                    file = open(CTS.text_folder+"\{}.txt".format(threadname),"w", encoding="utf-8")
                    op_post = CTS.get_op_post(self.threads, threadnum)
                    file.write(op_post)
                    file.write('\n')
                    for post in self.texts:
                        file.write(post)
                        file.write('\n')
                    file.close()
                    self.OUTBox.value ="Thread Saved"                    
                except IndexError:
                    self.OUTBox.value = "No Thread Selected"
            
            #read control scenario
            elif self.OPBox.value[0] == 5:
                try:
                    threadnum = self.threadselect.value[0] 
                    if not self.TBRead:
                        self.reader = self.add(SelectMultyBox,
                                                     scroll_exit=True,
                                                     name="Read Control",
                                                     custom_highlighting=True,
                                                     values=self.texts, 
                                                     rely=self.y // 2,
                                                     max_width=self.x // 2 - 5,
                                                     max_height=self.y // 4)
                        CTS.op_talk(self.texts[0])
                        self.reader.values=self.texts[1:]
                        self.TBRead = True
                    else:
                        try:
                            postnum = self.reader.value
                            print(postnum)
                            for i in range(len(postnum)):
                                print(postnum)
                                CTS.talk(self.texts[1:], i)
                        except IndexError:
                            self.OUTBox.value = "No more posts"
                except IndexError:
                    self.OUTBox.value = "No Post Slice selected"
                    
        except IndexError:
            self.OUTBox.value = "Select operation"
        
    def on_cancel(self):
        ok_cancel = npyscreen.notify_yes_no("Are you sure you want to return? \nThis will delete catalog and threads", "Warning", editw=2)
        if ok_cancel:
            if ok_cancel:
                self.OPBox.values = ["scan cataloge"]
                self.threads = []
                self.texts = []
                self.output = ''
                self.parentApp.setNextForm("MAIN")
        else:
            self.parentApp.setNextFormPrevious


if __name__ == "__main__":
    CTS = App().run()
