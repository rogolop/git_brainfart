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
num = {0,1,2,3,4,5,6,7,8,9}
sep = {" ","\t"}


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


def lexer(raw):
	tokenList = []
	for line in raw:
		lexeme = ""
		token = -1
		for c in line:
			#print(c)
			if c in source:
				tokenList.append((TokenT.source.value,c))
			elif c.isnumeric(): # or token == TokenT.literal.value:
				lexeme += c
				if token == -1:
					token = TokenT.literal.value
			elif c.isalpha() or c == "_":
				lexeme += c
				if token == -1:
					token = TokenT.id.value
			elif c in keywords:
				0
			elif c in op:
				0
			elif c in num:
				0
			elif c in sep:
				if lexeme in keywords:
					token = TokenT.keyword.value
				if lexeme != '':
					tokenList.append((token,lexeme))
				tokenList.append((TokenT.sep.value,c))
				lexeme = ""
				token = -1
		if lexeme in keywords:
			token = TokenT.keyword.value
		if lexeme != '':
			tokenList.append((token,lexeme))
		lexeme = ""
		token = -1
		tokenList.append((TokenT.newline.value,""))

	return tokenList


def parser(tokenList):
	AST = Tree() #AbstractSyntaxTree


fn = "test.BF"
file = open(fn,'r')
raw = file.readlines()
file.close()

tokenList = lexer(raw)
AST = parser(tokenList)

print(tokenList)
