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
keywords = {"do","macro"}
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
      #print(c)
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
        tokenList.append(("source",c))
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


def parse(tokenList,i,root):
  t = Tree(root)
  while i[0] < len(tokenList):
    #print(tokenList[i[0]])
    if tokenList[i[0]][1] == "(":
      i[0] += 1
      t.add_child(parse(tokenList,i,("brackets","")))
    elif tokenList[i[0]][1] == ")":
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


def bfprint(AST,i,nmax):
  return nmax


def expand_macro(AST,i,nmax,arg1,arg2):
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
      elif AST.children[i].name[0] == "brackets":
        expand_macro(AST.children[i],0,len(AST.children[i].children),arg1,arg2)
        n += 1
      else:
        n += 1
  return nmax

def macro(AST,i,nmax):
  arg1 = AST.children[i+1]
  arg2 = AST.children[i+2]
  assert arg1.name[0] == "id"
  remove_spaces(arg2)
  AST.remove_child(i) #macro
  AST.remove_child(i) #name
  AST.remove_child(i) #content
  nmax -= 3
  
  nmax = expand_macro(AST,i,nmax,arg1,arg2)
  return nmax



def transpile(AST):
  #nmax = len(AST.children)
  nmax = remove_spaces(AST)
  #expand BF expressions
  n = 0
  while n < nmax:
    for i in range(n, nmax):
      if AST.children[i].name[0] == "keyword":
        t = AST.children[i].name[1]
        if t == "macro":
          write(AST,"")
          nmax = macro(AST,i,nmax)
          write(AST,"")
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


def process(raw):
  tokenList = tokenize(raw)
  i = [0] #index "pointer" for position in tokenList to be used and modified in recursive function "parse"
  AST = parse(tokenList,i,("root",""))
  #write(AST,"")
  transpile(AST)
  #write(AST,"")
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

AST = process(raw)

fnOut = "out.bf"
f = open(fnOut, 'w')
for i in range(0,len(AST.children)):
  print(AST.children[i].name[1], file=f,end='')
#print('',file=f) #\n
f.close()