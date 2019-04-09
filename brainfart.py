import sys
import os

#from enum import Enum
#class TokenT(Enum):
# source = 0
# keyword = 1
# op = 2
# id = 3
# literal = 4
# sep = 5
# newline = 6

#tt = {"source", "keyword", "op", "id", "literal","sep", "newline"}
source = {'+','-','>','<','[',']','.',','}
keywords = {"do","macro","macro2","var","rDisplace","lDisplace","alias"}
op = {}
#num = {0,1,2,3,4,5,6,7,8,9}
sep = {" ","\t","(",")"}
quotes = {"'","\""}

varT ={
  "int8" : 1,
  "char" : 1
}

class Tree(object):
  "Generic tree node."
  def __init__(self, name='root', children=None):
    self.name = name
    self.children = []
    if children is not None:
      for child in children:
        self.add_child(child)
  def __repr__(self):
    return self.name
  def add_child(self, node):
    assert isinstance(node, Tree)
    self.children.append(node)
  def remove_child(self, n):
    assert isinstance(n, int)
    assert 0 <= n < len(self.children)
    del self.children[n]
  def insert_child(self, n, node):
    assert isinstance(n, int)
    assert 0 <= n <= len(self.children)
    assert isinstance(node, Tree)
    self.children.insert(n,node)

#    *
#   /|\
#  1 2 +
#     / \
#    3   4

#t = Tree('*', [Tree('1'),
#               Tree('2'),
#               Tree('+', [Tree('3'),
#                          Tree('4')])])


def tokenize(raw):
  tokenList = []
  for line in raw:
    lexeme = ""
    token = -1
    escape = False
    inQuotes = False
    for c in line:
      #print(c,end="")
      if escape:
        lexeme += c
        escape = False
      elif c == "\\":
        escape = True
      elif c in quotes:
        inQuotes = not inQuotes
        token = "literal"
      elif inQuotes:
        lexeme += c
      elif c in source:
        #as in "c in sep"
        if token != -1:
          if lexeme in keywords:
            token = "keyword"
          tokenList.append((token,lexeme))
          #tokenList.append(("sep",c)) 
          lexeme = ""
          token = -1
        #extra
        tokenList.append(("source",c))
      elif c in {"(",")"}:
        #as in "c in sep"
        if token != -1:
          if lexeme in keywords:
            token = "keyword"
          tokenList.append((token,lexeme))
          #tokenList.append(("sep",c)) 
          lexeme = ""
          token = -1
        #extra
        tokenList.append(("bracket",c))
      elif token == -1:
        if c.isnumeric(): #or c=="\"":
          token = "literal"
          lexeme += c
        elif c.isalpha() or c == "_":
          token = "id"
          lexeme += c
        elif c in sep:
          tokenList.append(("sep",c))
      elif c in sep:
        if lexeme in keywords:
          token = "keyword"
        tokenList.append((token,lexeme))
        tokenList.append(("sep",c))
        lexeme = ""
        token = -1
      else:
        lexeme += c
      #elif token == TokenT.literal.value:
      # lexeme += c
      #elif c.isalpha() or c == "_":
      # lexeme += c
      #elif c in keywords:
      # 0
      #elif c in op:
      # 0
    if lexeme != '':
      tokenList.append((token,lexeme))
    lexeme = ""
    token = -1
    tokenList.append(("newline","\n"))

  return tokenList


def aliases(tokenList):
  # #expand literal
  nmax = len(tokenList)
  n = 0
  alias = {}
  while n < nmax:
    for i in range(n, nmax):
      if tokenList[i] == ("keyword","alias"):
        del tokenList[i]
        nmax -= 1
        assert tokenList[i] == ("sep"," ")
        del tokenList[i]
        nmax -= 1
        assert tokenList[i][0] == "id"
        name = tokenList[i][1]
        del tokenList[i]
        nmax -= 1
        assert tokenList[i] == ("sep"," ")
        del tokenList[i]
        nmax -= 1
        assert tokenList[i][0] == "literal"
        codeStr = tokenList[i][1]
        #print("'%s'"%codeStr)
        codeList = tokenize([codeStr])
        assert codeList[-1] == ("newline","\n")
        del codeList[-1]
        #print(codeList)
        alias[name] = codeList
        del tokenList[i]
        nmax -= 1
        break
      elif tokenList[i][0] == "id" and tokenList[i][1] in alias:
        tokenList[i+1:i+1] = alias[tokenList[i][1]]
        #print(alias[tokenList[i][1]])
        nmax += len(alias[tokenList[i][1]]) -1
        del tokenList[i]
        break
      else:
        n += 1


def parse(tokenList,i,root):
  t = Tree(root)
  while i[0] < len(tokenList):
    #print(tokenList[i[0]])
    if tokenList[i[0]] == ("bracket","("):
      i[0] += 1
      t.add_child(parse(tokenList,i,("brackets","")))
    elif tokenList[i[0]] == ("bracket",")"):
      break
    else:
      t.add_child(Tree(tokenList[i[0]]))
    i[0] += 1
  return t


def remove_spaces(AST):
  nmax = len(AST.children)
  #remove spaces
  n = 0
  while n < nmax:
    for i in range(n,nmax):
      if AST.children[i].name[0] == "sep":
        AST.remove_child(i)
        nmax -= 1
        break
      elif AST.children[i].name[0] == "brackets":
        remove_spaces(AST.children[i])
        n += 1
      else:
        n += 1
  return nmax


def do(AST,i,nmax):
  arg1 = AST.children[i+1]
  arg2 = AST.children[i+2]
  assert arg1.name[0] == "literal"
  assert arg1.name[1].isdigit()
  arg1 = int(arg1.name[1])
  AST.remove_child(i) #do
  AST.remove_child(i) #arg1 times
  AST.remove_child(i) #arg2
  nmax -= 3
  for j in range(0,arg1):
    AST.insert_child(i,arg2)
    nmax += 1
  return nmax


def expand_macro(AST,i,nmax, arg1,arg2):
  n = i
  while n < nmax:
    for j in range(n,nmax):
      #print(AST.children[j].name)
      if AST.children[j].name == arg1.name:
        AST.remove_child(j)
        nmax -= 1
        for k in range(0, len(arg2.children)):
          AST.insert_child(j+k, arg2.children[k])
          nmax += 1
        break
      elif AST.children[j].name[0] == "brackets":
        expand_macro(AST.children[j],0,len(AST.children[j].children),arg1,arg2)
        n += 1
      else:
        n += 1
  return nmax


def macro(AST,i,nmax):
  arg1 = AST.children[i+1]
  arg2 = AST.children[i+2]
  assert arg1.name[0] == "id"
  remove_spaces(arg2)
  if arg2.children[0].name[0] == "newline":
    arg2.remove_child(0)
  L = len(arg2.children)
  if arg2.children[L-1].name[0] == "newline":
    arg2.remove_child(L-1)
  AST.remove_child(i) #macro
  AST.remove_child(i) #name
  AST.remove_child(i) #content
  nmax -= 3
  
  nmax = expand_macro(AST,i,nmax,arg1,arg2)
  return nmax


def replaceVars(AST,j,m,intVars,extVars):
  for k in range(j,j+m):
    if AST.children[k].name in intVars:
      I = intVars.index(AST.children[k].name)
      AST.children[k] = extVars[I]
    elif AST.children[k].name == ("brackets",""):
      replaceVars(AST.children[k],0,len(AST.children[k].children),intVars,extVars)


def expand_macro2(AST,i,nmax, arg1,arg2,arg3):
  intVars = [k.name for k in arg2.children]  # placeholder vars used in arg3
  # print(type(intVars[0]))
  n = i
  while n < nmax:
    for j in range(n,nmax):
      name = AST.children[j].name
      # print(AST.children[j].name)
      if name == arg1.name: #call to expand macro arg1
        AST.remove_child(j)
        nmax -= 1
        extTree = AST.children[j]  # real vars to substitute placeholders (intVars)
        remove_spaces(extTree)
        extVars = extTree.children
        # [k.name for k in extTree.children]
        print("extVars ", end="")
        [print(c.name) for c in extVars]
        print("intVars", intVars)
        assert len(extVars) == len(intVars)
        AST.remove_child(j)
        nmax -= 1
        for k in range(0, len(arg3.children)):
          AST.insert_child(j+k, arg3.children[k])
          nmax += 1
          # print(AST.children[j+k].name)
        replaceVars(AST, j, len(arg3.children), intVars, extVars)
        # print(I)
        break
      elif name[0] == "brackets":
        expand_macro2(AST.children[j], 0, len(AST.children[j].children), arg1, arg2, arg3)
        n += 1
      else:
        n += 1
  return nmax


def macro2(AST,i,nmax):
  arg1 = AST.children[i+1] #macro name
  arg2 = AST.children[i+2] #placeholder vars
  arg3 = AST.children[i+3] #code
  assert arg1.name[0] == "id"
  remove_spaces(arg2)
  remove_spaces(arg3)
  if arg3.children[0].name[0] == "newline":
    arg3.remove_child(0)
  L = len(arg3.children)
  if arg3.children[L-1].name[0] == "newline":
    arg3.remove_child(L-1)
  #[print(c.name) for c in AST.children[i:]]
  #write(AST,"")
  AST.remove_child(i) #macro
  AST.remove_child(i) #name
  AST.remove_child(i) #variables
  AST.remove_child(i) #content
  nmax -= 4
  
  nmax = expand_macro2(AST,i,nmax,arg1,arg2,arg3)
  write(AST,"")
  return nmax



def transpile(AST):
  #nmax = len(AST.children)
  nmax = remove_spaces(AST)
  #write(AST,"")
  #expand BF expressions
  n = 0
  while n < nmax:
    for i in range(n, nmax):
      if AST.children[i].name[0] == "keyword":
        t = AST.children[i].name[1]
        if t == "macro":
          nmax = macro(AST,i,nmax)
          break
        if t == "macro2":
          #write(AST,"")
          nmax = macro2(AST,i,nmax)
          #write(AST,"")
          break
        elif t == "do":
          nmax = do(AST,i,nmax)
          break
      else:
        n += 1
  #recurse
  n = 0
  while n < nmax:
    for i in range(n, nmax):
      if AST.children[i].name[0] == "brackets":
        transpile(AST.children[i])
        cclen = len(AST.children[i].children)
        for j in range(0,cclen):
          AST.insert_child(i+j+1,AST.children[i].children[j])
        nmax += cclen - 1
        AST.remove_child(i)#bracket
        break
      else:
        n += 1
  #variables
  vars = {} #dict
  notUsed = 0
  pos = 0
  n = 0
  while n < nmax:
    for i in range(n, nmax):
      name = AST.children[i].name
      #print(pos,name)
      if name == ("keyword","var"):
        assert AST.children[i+1].name[0] == "id"
        vars[AST.children[i+1].name[1]] = notUsed
        notUsed += 1
        AST.remove_child(i)
        AST.remove_child(i)
        nmax -= 2
        break
      elif name[0] == "id" and name[1] in vars:
        AST.remove_child(i)
        d = vars[name[1]] - pos
        toAdd = ">"
        if d < 0:
          toAdd = "<"
          d *= -1
          #print("d")
        #print(d)
        for j in range(0,d):
          AST.insert_child(i, Tree(("source",toAdd)))
        AST.insert_child(i+d, Tree(("literal",name[1])))
        #AST.remove_child(i)
        nmax += d #-1
        #n += 1
        break
      elif name == ("source",">"):
        pos += 1
        n += 1
      elif name == ("source","<"):
        pos -= 1
        n += 1
      elif name == ("keyword","rDisplace"):
        assert AST.children[i+1].name[0] == "literal"
        pos += int(AST.children[i+1].name[1])
        AST.remove_child(i)
        AST.remove_child(i)
        nmax -= 2
        #n += 1
        break
      elif name == ("keyword","lDisplace"):
        assert AST.children[i+1].name[0] == "literal"
        pos -= int(AST.children[i+1].name[1])
        AST.remove_child(i)
        AST.remove_child(i)
        nmax -= 2
        #n += 1
        break
      else:
        n += 1
  #print(vars)
        

#remove superfluous code
def optimize(AST):
  nmax = len(AST.children)
  pm = ("+","-")
  lr = (">","<")
  someChange = True
  while someChange:
   someChange = False
   acc = 0 #accumulated ammount
   at = 0 #none/pm/lr
   ac = 0 #1st/2nd element of pm/lr
   last = ""
   pair = last
   n = 0
   while n < nmax:
    for i in range(n, nmax):
      name = AST.children[i].name
      #print(i,n,name,last,acc,end="\n")
      if at != 0 and name[0] == "source" and name[1] in {last,pair}:
        name = name[1]
        #print(acc)
        if name == last:
          acc += 1
        elif name == pair:
          acc -= 1
      elif at != 0:
        if acc != i-n:
          someChange = True
          #remove
          #print("REMOVING:",i-n)
          for j in range(0,i-n):
            AST.remove_child(n)
          nmax -= i-n
          if acc != 0:
            #add last
            if acc > 0:
              toAdd = last
            else:
              toAdd = pair
              acc *= -1
            #print("ADDING:",toAdd,acc)
            for j in range(0,acc):
              AST.insert_child(n, Tree(("source",toAdd)))
            nmax += acc
        n += acc
        at = 0
        acc = 0
        break
      elif name[0] != "source":
        n += 1
      else:
          name = name[1]
          last = name
          acc = 1
          if last in pm:
            at = 1
            if name == pm[0]:
              ac = 0
            else:
              ac = 1
            pair = pm[not ac]
            #print("NEW: pm",last)
          elif last in lr:
            at = 2
            acc = 1
            if name == lr[0]:
              ac = 0
            else:
              ac = 1
            pair = lr[not ac]
            #print("NEW: lr",last)
          else:
            n += 1
  #if someChange:
    #print("LOOP")
    #optimize(AST)


def process(raw,opt,short):
  #print(raw)
  tokenList = tokenize(raw)
  #[print(i) for i in tokenList]
  aliases(tokenList)
  #[print(i) for i in tokenList]
  i = [0] #index "pointer" for position in tokenList to be used and modified in recursive function "parse"
  AST = parse(tokenList,i,("root",""))
  #write(AST,"")
  transpile(AST)
  #write(AST,"")
  if opt:
    optimize(AST)
  while AST.children[0].name == ("newline","\n"):
    AST.remove_child(0)
    if len(AST.children) == 0:
      break
  if short:
    nmax = len(AST.children)-1
    n = 0
    while n < nmax:
      for i in range(n, nmax):
        if [AST.children[i].name,AST.children[i+1].name] == 2*[("newline","\n")]:
          AST.remove_child(i)
          nmax -= 1
          break
        else:
          n += 1
  return AST

#AbstractSyntaxTree
#raw = file.readlines()
#print(tokenList[i[0]])
#print(tokenList)
#for t in raw:
#print(raw)
#for t in tokenList:
# print(t)

def write(tree,sep):
  print("%s%-10s%s"%(sep,tree.name[0],tree.name[1]))
  for c in tree.children:
    write(c,sep + "  ")


fnIn = "test.BF"
f = open(fnIn,'r')
raw = f.read().splitlines()
f.close()

opt = True
short = True
if '--Nopt' in sys.argv:
  opt = False
if '--Nshort' in sys.argv:
  short = False
if '--Nbase' not in sys.argv:
  fnBase = "base.BF"
  if os.path.isfile(fnBase):
    f = open(fnBase,'r')
    base = f.read().splitlines()
    f.close()
    raw[0:0] = base
  else:
    print("base.BF not found")


AST = process(raw,opt,short)

fnOut = "out.bf"
f = open(fnOut, 'w')
for i in range(0,len(AST.children)):
  print(AST.children[i].name[1], file=f,end='')
#print('',file=f) #\n
f.close()