from tkinter import filedialog, Frame, Tk, BOTH, Text, Menu, END
from tkinter import *
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import numpy as np

fnames = []
filecontent = {}
fildoclist = []
ppcontent = {}
filwords =[]
pptokens =[]
c_dict = {}
wmatrix = []
smatrix = []
bmatrix = []
clusterslist = []

stop_words = stopwords.words('english')
stop_words.append('I')
stop_words.append('The')
stop_words.append("It")
stop_words.append('.')
stop_words.append(',')
stop_words.append(':')
stop_words.append("\'")
stop_words.append("\"")
stop_words.append("(")
stop_words.append(")")

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent        
        self.initUI()

    def initUI(self):
        self.parent.title("Document clustering using Conceptual Vector Space Model")
        self.parent.configure(background="#a1dbcd")
        #self.pack(fill=BOTH, expand=1)

        top = Frame(self.parent,bg="#a1dbcd")
        L = Label(top, text = "Document clustering using Conceptual Vector Space Model",bg="#a1dbcd", font=("Helvetica",25),bd=6)
        L.pack(side=TOP, expand=YES , fill=X)

        L1 = Label(top, text = "Choose Files to Upload (Only Text Files Allowed): ",bg="#a1dbcd",bd=8, font=("Helvetica",15))
        L1.pack(side=LEFT)
        B = Button(top, text = "Click to Upload Files",bg="#24E34A",bd=4,font=("Helvetica",13), command = self.onOpen)
        B.pack(side=LEFT)
        top.pack(fill=BOTH, expand=YES)

        self.S = Scrollbar(self.parent)
        self.txt = Text(self.parent, height=30, width=120)
        self.S.pack(side=RIGHT, fill=Y)
        self.txt.pack(side=LEFT, fill=BOTH, expand=1)
        self.S.config(command=self.txt.yview)
        self.txt.config(yscrollcommand=self.S.set)
        self.txt.tag_config('bold_italics', font=('Verdana','15','bold','italic'))
        self.txt.tag_config('bold', font=('Verdana','10','bold'))

    def onOpen(self):
        ftypes = [('Text files', '*.txt')]
        #self.filenames =  filedialog.askopenfilenames(initialdir = "/",title = "Select file", filetypes = ftypes)
        self.filenames =  filedialog.askopenfilenames(title = "Select file", filetypes = ftypes)
        global fnames
        global filecontent
        for fn in self.filenames:
            fnames.append(os.path.basename(fn))
            text = self.readFile(fn)
            filecontent[os.path.basename(fn)] = text
            self.txt.insert(INSERT, fn,'bold')
            self.txt.insert(INSERT, "\n\n")
            self.txt.insert(INSERT, text)
            self.txt.insert(INSERT, "\n\n")
        #self.txt.insert(INSERT, fnames)
        #self.txt.insert(INSERT, filecontent)
        self.B1 = Button(self.parent, text = "Preprocessing", command = self.pp,bd=6,font=("Helvetica",10))
        self.B1.pack()

    def readFile(self, filename):
        f = open(filename, "r")
        text = f.read()
        return text

    def pp(self):
        global fnames
        global filecontent
        global fildoclist
        global ppcontent
        global stop_words
        global pptokens
        global filwords
        self.txt.delete('1.0',END)
        self.txt.insert(END,"Documents after Pre-Processing\n","bold_italics")
        c = 0
        for file_name in filecontent:
            #Tokenization
            word_tokenize_list = word_tokenize(filecontent[file_name])
            # Stop word Removal
            filteredfilename = "filtered_docs" + "/" + "filter%d.txt" % c
            fildoclist.append(os.path.basename(filteredfilename))
            file2 = open(filteredfilename,'w+')
            for r in word_tokenize_list:
                if not r in stop_words:
                    file2.write(r.lower()+" ")
            file2.close()
            f = open(filteredfilename, "r")
            text = f.read()
            ppcontent[os.path.basename(filteredfilename)] = text
            #Collecting Unique Tokens
            for i in ppcontent:
                tokens = ppcontent[i].split()
                uniquetokens = []
                for i in tokens:
                    if i not in uniquetokens:
                        uniquetokens.append(i)
                # add each token to pptokens list
                filwords.append(uniquetokens)
                for i in uniquetokens:
                    if i not in pptokens:
                        pptokens.append(i)
            c+=1
        #print(pptokens)
        #print(filwords)
        for i in ppcontent:
            self.txt.insert(INSERT,i,'bold')
            self.txt.insert(INSERT, "\n\n")
            self.txt.insert(INSERT,ppcontent[i])
            self.txt.insert(INSERT, "\n\n")
        self.B2 = Button(self.parent, text = "Generate Concepts", command = self.concepts,bd=6,font=("Helvetica",10))
        self.B2.pack()

    def concepts(self):
        self.B1.destroy()
        self.txt.delete('1.0',END)
        self.txt.insert(END,"Concepts for each token\n","bold_italics")
        global c_dict
        global pptokens
        for word in pptokens:
            synonyms = []
            synunique = []
            for syn in wordnet.synsets(word):
                for l in syn.lemmas():
                    synonyms.append(l.name())
            for i in synonyms:
                if i not in synunique:
                    synunique.append(i)
            c_dict[word] = synunique
        for i in c_dict:
            self.txt.insert(INSERT,i,'bold')
            self.txt.insert(INSERT, " - ")
            self.txt.insert(INSERT,c_dict[i])
            self.txt.insert(INSERT, "\n")
        self.B3 = Button(self.parent, text = "Weighted Matrix", command = self.weighted_matrix,bd=6,font=("Helvetica",10))
        self.B3.pack()

    def weighted_matrix(self):
        self.B2.destroy()
        self.txt.delete('1.0',END)
        self.txt.insert(END,"Weighted Matrix\n","bold_italics")
        global c_dict
        global ppcontent
        global wmatrix
        wm = []
        for i in c_dict:
            a = []
            for j in ppcontent:
                ftokens = ppcontent[j].split()
                value,wvalue,wfreq,svalue,sfreq,count = 0,0,0,0,0,0
                if i in ftokens:
                    wvalue = 1
                    wfreq = ftokens.count(i)
                    count = count+1
                for s in c_dict[i]:
                    if s in ftokens:
                        svalue = svalue+1
                        sfreq = sfreq+ftokens.count(s)
                        count = count+1
                value = (wfreq*1)+(sfreq*0.5)
                if(count==0):
                    count = 1
                a.append(value/count)
                #f.close()
            wm.append(a)
            wmatrix = np.matrix(wm)
        self.txt.insert(INSERT,wmatrix)
        self.B4 = Button(self.parent, text = "Similarity Matrix", command = self.sim_matrix,bd=6,font=("Helvetica",10))
        self.B4.pack()

    def sim_matrix(self):
        self.B3.destroy()
        self.txt.delete('1.0',END)
        self.txt.insert(END,"Similarity Matrix\n","bold_italics")
        global c_dict
        global fildoclist
        global wmatrix
        global smatrix
        concepts = len(c_dict)
        docs = len(fildoclist)
        smatrix = np.zeros(shape=(docs,docs))
        for i in range(docs):
            for j in range(docs):
                if(i==j):
                    smatrix[i,j] = -1
                elif(smatrix[i,j]==0):
                    m=0
                    for x in range(concepts):
                        m = m+(wmatrix[x,i]*wmatrix[x,j])
                    smatrix[i,j] = m
                    smatrix[j,i] = m
                else:
                    n = 1
        self.txt.insert(INSERT,smatrix)
        self.B5 = Button(self.parent, text = "Binary Matrix", command = self.binary_matrix,bd=6,font=("Helvetica",10))
        self.B5.pack()

    def binary_matrix(self):
        self.B4.destroy()
        self.txt.delete('1.0',END)
        self.txt.insert(END,"Binary Matrix\n","bold_italics")
        global fildoclist
        global smatrix
        global bmatrix
        docs = len(fildoclist)
        bmatrix = np.zeros(shape=(docs,docs))
        threshold = 0
        thr = 0
        nt = 0
        for i in range(docs):
            for j in range(docs):
                if(i<j):
                    thr = thr + smatrix[i,j]
                    nt = nt + 1
        threshold = thr/nt
        #print(threshold)
        for i in range(docs):
            for j in range(docs):
                if(i==j):
                    bmatrix[i,j] = -1
                elif(smatrix[i,j]>=threshold):
                    bmatrix[i,j] = 1
                else:
                    bmatrix[i,j] = 0
        self.txt.insert(INSERT,bmatrix)
        self.B6 = Button(self.parent, text = "Cluster Documents", command = self.cliques,bd=6,font=("Helvetica",10))
        self.B6.pack()
        self.B6 = Button(self.parent, text = "Cluster Documents - VSM", command = self.vsm_clusters,bd=6,font=("Helvetica",10))
        self.B6.pack()

    def cliques(self):
        self.B5.destroy()
        self.txt.delete('1.0',END)
        self.txt.insert(END,"Clustered Documents\n","bold_italics")
        global fildoclist
        global bmatrix
        global clusterslist
        global fnames
        clusters = []
        docs = len(fildoclist)
        m=docs-1
        i=0
        j=0 #class count
        classes = {}
        while(i!=m):
            #f3
            #print(i)
            classes[j] = []
            classes[j].append(i)
            r=i+1
            k=i+1
            #print('k',k)
            while(1):
                #f1
                count = 0
                #if(k<=m):
                for x in classes[j]:
                    #print('x',x)
                    if(bmatrix[k,x]==1):
                        count=count+1
                    else:
                        break
                if(count == len(classes[j])):
                    classes[j].append(k)
                #
                #print(classes)
                k=k+1
                if(k>m):
                    r=r+1
                    if(r!=m):
                        k=r
                        j=j+1
                        classes[j] = []
                        classes[j].append(i)
                #f1
                if(k>m and r==m):
                     #f2
                     if(classes[j] == [i]):
                         #print('*')
                         del(classes[j])
                     #i=i+1
                     break
                if(k>m):
                    break
            i,j = i+1,j+1
        for key in classes:
            clusterslist.append(classes[key])
        n = 0
        while n < len(clusterslist):
            s = set(clusterslist[n])
            for x in range(len(clusterslist)):
                if x == n: continue
                if s <= set(clusterslist[x]):
                    clusterslist.pop(n)
                    n -= 1
                    break
            n += 1
        cn = 1
        for cl in clusterslist:
            for d in cl:
                cl[cl.index(d)] = fnames[d]
            self.txt.insert(INSERT,"Cluster %d - "%cn, 'bold')
            self.txt.insert(INSERT,cl)
            self.txt.insert(INSERT,"\n")
            cn=cn+1
        #self.txt.insert(INSERT,clusterslist)

    def vsm_clusters(self):
        self.B5.destroy()
        #        self.txt.delete('1.0',END)
        self.txt.insert(END,"Document Clustering Using Vector Space Model\n","bold_italics")
        global pptokens
        global fildoclist
        vsm = []
        for i in pptokens:
            a = []
            for j in ppcontent:
                count = 0
                ftokens = ppcontent[j].split()
                if i in ftokens:
                    count = ftokens.count(i)
                a.append(count)
            vsm.append(a)
        a = np.matrix(vsm)
        tokens = len(pptokens)
        docs = len(fildoclist)
        b = np.zeros(shape=(docs,docs))
        for i in range(docs):
            for j in range(docs):
                if(i==j):
                    b[i,j] = -1
                elif(b[i,j]==0):
                    m=0
                    for x in range(tokens):
                        m=m+(a[x,i]*a[x,j])
                    b[i,j] = m
                    b[j,i] = m
                else:
                    n=1
        c = np.zeros(shape=(tokens,tokens))
        threshold = 0
        thr = 0
        nt = 0
        for i in range(docs):
            for j in range(docs):
                if(i<j):
                    thr = thr + b[i,j]
                    nt = nt + 1
        threshold = thr/nt
        #print(threshold)
        for i in range(docs):
            for j in range(docs):
                if(i==j):
                    c[i,j] = -1
                elif(b[i,j]>=threshold):
                    c[i,j] = 1
                else:
                    c[i,j] = 0
        m=docs-1
        #cliques algorithm
        i=0
        j=0 #class count
        classes = {}
        clusters = []
        while(i!=m):
            #f3
            #print(i)
            classes[j] = []
            classes[j].append(i)
            r=i+1
            k=i+1
            #print('k',k)
            while(1):
                #f1
                count = 0
                #if(k<=m):
                for x in classes[j]:
                    #print('x',x)
                    if(c[k,x]==1):
                        count=count+1
                    else:
                        break
                if(count == len(classes[j])):
                    classes[j].append(k)
                #
                #print(classes)
                k=k+1
                if(k>m):
                    r=r+1
                    if(r!=m):
                        k=r
                        j=j+1
                        classes[j] = []
                        classes[j].append(i)
                #f1

                if(k>m and r==m):
                     #f2
                     if(classes[j] == [i]):
                         #print('*')
                         del(classes[j])
                     #i=i+1
                     break
                if(k>m):
                    break
            i,j = i+1,j+1
        clusterslist = []
        for key in classes:
            #print(key, classes[key])
            clusterslist.append(classes[key])
        n=0
        while n < len(clusterslist):
            s = set(clusterslist[n])
            for x in range(len(clusterslist)):
                if x == n: continue
                if s <= set(clusterslist[x]):
                    clusterslist.pop(n)
                    n -= 1
                    break
            n += 1
        cn = 1
        for cl in clusterslist:
            for d in cl:
                cl[cl.index(d)] = fnames[d]
            self.txt.insert(INSERT,"Cluster %d - "%cn, 'bold')
            self.txt.insert(INSERT,cl)
            self.txt.insert(INSERT,"\n")
            cn=cn+1                        

def main():
    root = Tk()
    ex = Example(root)
    root.mainloop()  

if __name__ == '__main__':
    main()  
