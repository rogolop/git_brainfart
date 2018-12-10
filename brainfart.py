from enum import Enum

class TokenT(Enum):
	source = 0
	keyword = 1
	op = 2
	id = 3
	literal = 4
	sep = 5
	newline = 6

source = {'+','-','>','<','[',']','.',','}
keywords = {"shit"}
op = {}
#num = {0,1,2,3,4,5,6,7,8,9}
sep = {" ","\t","(",")"}

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
		for c in line:
			#print(c)
			if escape:
				lexeme += c
				escape = False
			elif c == "\\":
				escape = True
			elif c in source:
				tokenList.append((TokenT.source,c))
			elif token == -1:
				if c.isnumeric(): # or c == "\"":
					token = TokenT.literal
					lexeme += c
				elif c.isalpha() or c == "_":
					token = TokenT.id
					lexeme += c
				elif c in sep:
					tokenList.append((TokenT.sep,c))
			elif c in sep:
				if lexeme in keywords:
					token = TokenT.keyword
				tokenList.append((token,lexeme))
				tokenList.append((TokenT.sep,c))
				lexeme = ""
				token = -1
			else:
				lexeme += c
			#elif token == TokenT.literal.value:
			#	lexeme += c
			#elif c.isalpha() or c == "_":
			#	lexeme += c
			#elif c in keywords:
			#	0
			#elif c in op:
			#	0
		if lexeme != '':
			tokenList.append((token,lexeme))
		lexeme = ""
		token = -1
		tokenList.append((TokenT.newline,""))

	return tokenList


def parse(tokenList,i,root):
	t = Tree(root)
	while i[0] < len(tokenList):
		#print(tokenList[i[0]])
		if tokenList[i[0]][1] == "(":
			i[0] += 1
			t.add_child(parse(tokenList,i,"brackets"))
		elif tokenList[i[0]][1] == ")":
			break
		else:
			t.add_child(Tree(tokenList[i[0]]))
		i[0] += 1

	return t


def transpile(AST):
	return 0


#AbstractSyntaxTree
#raw = file.readlines()
#print(tokenList[i[0]])
#print(tokenList)
#for t in raw:
#print(raw)
#for t in tokenList:
#	print(t)

def write(tree,sep):
	print(sep,tree.name)
	for c in tree.children:
		write(c,sep + "  ")


fn = "test.BF"
file = open(fn,'r')
raw = file.read().splitlines()
file.close()

tokenList = tokenize(raw)
i = [0]
AST = parse(tokenList,i,"root")

write(AST,"")

transpile(AST)

