from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk 
import pickle
import numpy as np
from nltk.corpus import stopwords
from nltk.corpus import words
from nltk.corpus import wordnet
import re
from conversion import convert

class Application(tk.Frame):
    global model_direct
    model_direct = pickle.load(open('objectivity-detection-direct.sav','rb'))
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.title = tk.Label(self, text='Text Objectivity Detector and Text Voice Converter', font=('Roboto',30))
        self.title.grid(row=1,column=0,padx=10,pady=10,sticky=W)
        
        self.field = tk.Text(self)
        self.field.grid(row=2,column=0,padx=10,pady=5)
               
        self.upload = tk.Button(self, text = 'Upload .txt File', width = 60, command = self.uploadTxt)
        self.upload.grid(row=3,column=0,padx=10,pady=3)
        
        self.btn = tk.Button(self, text='Detect Objectivity', command = self.detectObjectivity)
        self.btn.grid(row=4,column=0,padx=50,pady=3,sticky=W)
        
        self.btn2 = tk.Button(self, text='Objectify/Subjectify (Auto)', command = self.transform)
        self.btn2.grid(row=4,column=0,padx=40,pady=3,sticky=E)

        self.res = tk.Label(self, text='', font=('Roboto',13))
        self.res.grid(row=5,column=0,padx=10,pady=10)  
        
        
    def detectObjectivity(self):
        arr = model_direct.predict_proba([self.field.get(1.0,'end')])
        self.res.config(text = 'Objective: ' + str(round(arr[0][1]*100,2)) + 
                        '%\nSubjective: ' + str(round(arr[0][0]*100,2)) + '%')
    def uploadTxt(self):
        tf = filedialog.askopenfilename(
            title="Open Text file", 
            filetypes=(("Text Files", "*.txt"),)
            )
        with open(tf, 'r') as file:
            data = file.read()
        self.field.insert(1.0,data)
        
    def transform(self):
        text = self.field.get(1.0,'end')
        result = convert([text])
        file = open('subjectified.txt','w')
        file.write(text)
        file.close()
        self.res.config(text = 'Text converted. Please check your file system.')
        self.alert('Hello','Please wait as we download about 4Gb of data. This is a one-time process.\nThis will take a while')
    
    def alert(self,title, message, kind='info', hidemain=True):
        if kind not in ('error', 'warning', 'info'):
            raise ValueError('Unsupported alert kind.')
        show_method = getattr(messagebox, 'show{}'.format(kind))
        show_method(title, message)
    
    def makeMoreSubjective(self):
        text = self.test(self.field.get(1.0,'end'),True)
        file = open('subjectified.txt','w')
        file.write(text)
        file.close()
        self.res.config(text = 'Text converted to be more subjective.\nPlease check your file system.')
        
    def makeMoreObjective(self):
        text = self.test(self.field.get(1.0,'end'),False)
        file = open('objectified.txt','w')
        file.write(text)
        file.close()
        self.res.config(text = 'Text converted to be more objective.\nPlease check your file system.')
        
    def test(self,string,isSubjective):
        strings = string.split(' ')
        stop_words = set(stopwords.words('english')) 
        res = ''
        for string in strings: 
            if string in stop_words or not string.islower(): 
                temp = ' ' + string + ' '
                res+=temp
                continue
            if len(wordnet.synsets(string)) != 0:
                temp = ' ' + self.find_synonyms(string,isSubjective)[0][1] + ' '
            else: temp = string + ' '
            res += temp 
        regex = re.compile(r"\s+")
        res = regex.sub(" ", res).strip()
        return res
    
    def find_synonyms(self,word,isSubjective):
        list_synonyms = []
        for syn in wordnet.synsets(word):
            for lemm in syn.lemmas():
                list_synonyms.append(lemm.name())
        #list_synonyms = [item.lower() for item in list_synonyms]
        scores = [(model_direct.predict_proba([text])[0][0],text) for text in list_synonyms]
        scores.append((model_direct.predict_proba([word])[0][0],word))
        if isSubjective:
            scores.sort(reverse=True)
        else: scores.sort()
        return scores
        
        

root = tk.Tk()
root.title('Not a Fact Checker')
        
app = Application(master=root)

root.mainloop()

