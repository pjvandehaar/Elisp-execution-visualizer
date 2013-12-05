#!/usr/bin/env python

# By Peter VandeHaar
# for CS214 final project
# completed 2013 May 8

from subprocess import Popen, PIPE

class Parser:
	"The Parser class converts a string into a list-based parse-tree"
	def __init__(self, code):
		"like self.tokens = code.split() with intelligent handling of strings and parens."
		code = code.replace('\n',' ').rstrip()
		self.tokens = []
		while code:
			code = code.lstrip()
			if code[0] in ['(',')']:
				nChars = 1
			elif code[0] == '"':
				nChars = code[1:].find('"')+2
			else:
				nChars = min( code.find(" "), code.find(")"), len(code), key=(lambda x: float("inf") if x==-1 else x))
			self.tokens.append(code[:nChars])
			code = code[nChars:]

	def get_file_parse(self):
		"a list of the expressions in a file, obtained by repeatedly invoking get_expr_parse()."
		stack = []
		while self.tokens:
			stack.append(self.get_expr_parse())
		return stack

	def get_expr_parse(self):
		"the parse of a single expression"
		if self.tokens[0] == '(':
			self.tokens.pop(0)
			stack = []
			while self.tokens[0] != ')':
				stack.append(self.get_expr_parse())
			self.tokens.pop(0)
			return stack
		else:
			return self.tokens.pop(0)

class Completed_Step_Exception(Exception):
	"Indication that the code has been modified and so the program should terminate soon.  Very much not an error."
	pass

class Expr:
	"An atom (string, int, etc) or a list of other Exprs."
	def __init__(self, pt, prgm=None):
		"Accepts a list-based parse-tree or another Expression.  Works recursively.  A prgm may be passed in for access to global functions."
		if isinstance(pt,list):
			self.contents = list(Expr(_pt, prgm=prgm) for _pt in pt)
		elif isinstance(pt,Expr):
			self.contents = pt.contents
		else:
			self.contents = pt
		self.prgm = prgm

	def __str__(self):
		if self.is_atom():
			return self.contents
		else:
			#this is a mess.  It should use list comprehensions.
			result = '('
			i = 0
			while i<len(self.contents) and (self.contents[i].is_atom() or i==0):
				result += str(self.contents[i]) + ' '
				i+=1
			result = result.rstrip()
			while i<len(self.contents):
				result += '\n ' + str(self.contents[i]).replace('\n','\n ')
				i+=1
			return result + ')'

	def is_atom(self):
		return not isinstance(self.contents,list)

	def is_terminal(self):
		return all(e.is_atom() for e in self.contents)

	def is_function(self):
		"only recognizes built-in functions"
		return Expr(['functionp', "'"+self.contents[0].contents]).calculate().contents == 't'

	def as_defconst(self):
		"returns [string, Expr] if it's a defconst else None"
		if not self.is_atom() and len(self.contents)==3 and self.contents[0].contents == 'defconst':
			return [self.contents[1].contents, self.contents[2]]

	def as_func(self):
		"returns [string, [string,...], Expr] if it's a defun else None"
		if not self.is_atom() and len(self.contents)>=4 and self.contents[0].contents == 'defun':
			return [self.contents[1].contents, 
				list(e.contents for e in self.contents[2].contents), 
				self.contents[3] if len(self.contents)==4 else Expr(['progn'] + self.contents[3:])]

	def get_matching_func(self):
		funcs = self.prgm.funcs if self.prgm else []
		for f in funcs:
			if f[0] == self.contents[0].contents:
				return f

	def collapse(self, terminal=True):
		"Collapses the Expr to an atom"
		self.contents = self.calculate(include_funcs=not terminal).contents
		raise Completed_Step_Exception("Collapsed to "+str(self.contents))
		
	def expand(self, f):
		"Expands the Expr out using function definition f, substituting actual parameters for formal parameters."
		formal_args = f[1]
		actual_args = self.contents[1:]
		self.contents = Expr(Parser(str(f[2])).get_expr_parse(),prgm=self.prgm).contents #deep copy for cool kids ;)
		for f_arg,a_arg in zip(formal_args,actual_args):
			self.substitute([f_arg,a_arg])
		raise Completed_Step_Exception("Expanded func "+f[0])
		
	def try_special(self):
		"If the expr is a special (ie, neither a macro nor function), this will simplify the code and throw."
		f = self.contents[0].contents
		if f == 'if':
			if self.contents[1].is_atom():
				if self.contents[1].contents == 't':
					self.contents = self.contents[2].contents
				else:
					self.contents = self.contents[3].contents if len(self.contents)>3 else 'nil'
				raise Completed_Step_Exception("Collapsed if special")
			else:
				self.contents[1].step()
		elif f == 'cond':
			if len(self.contents)==1:
				self.contents='nil'
			else:
				e = self.contents[1]
				first_part = e.contents[0]
				if first_part.is_atom():
					if first_part.contents == 'nil':
						self.contents.pop(1)
					else:
						self.contents = e.contents[1].contents
				else:
					first_part.step()
			raise Completed_Step_Exception("Collapsed cond special")
		elif f == 'and':
			if len(self.contents)==1:
				self.contents='t'
			else:
				e = self.contents[1]
				if e.is_atom():
					if e.contents == 'nil' or len(self.contents) == 2:
						self.contents = e.contents
					else:
						self.contents.pop(1)
				else:
					e.step()
			raise Completed_Step_Exception("Collapsed and special")
		elif f == 'or':
			if len(self.contents)==1:
				self.contents='nil'
			else:
				e = self.contents[1]
				if e.is_atom():
					if e.contents != 'nil' or len(self.contents) == 2:
						self.contents = e.contents
					else:
						self.contents.pop(1)
				else:
					e.step()
			raise Completed_Step_Exception("Collapsed or special")

	def step(self):
		"Simplifies this expr slightly and then throws."
		if self.is_atom():
			return True
		f = self.get_matching_func()
		if f:
			if self.is_terminal():
				self.expand(f)
			else:
				for e in self.contents:
					e.step()
		self.try_special()
		if self.is_terminal():
			self.collapse()
		if self.is_function():
			for e in self.contents:
				e.step()
		self.collapse(terminal=False)
	
	def calculate(self, include_funcs=False):
		"Runs this Expr in Emacs to get the result.  This requires access to the globally defined functions."
		code = "(print " +  self.__str__() + ")"
		if include_funcs:
			for f in prgm.funcs:
				code = str(prgm.func_to_expr(f))+"\n"+code
		with open('/tmp/ELPY.el','w') as f: #use tempfile module?
			f.write(code)
		p = Popen(["emacs", "--script", "/tmp/ELPY.el"], stdout=PIPE, stderr=PIPE)
		c = p.communicate()
		with open('log.txt','w') as f:
			f.write("CODE\n"+ code + "\nSTDERR\n" + c[1].decode())
		pt = Parser(c[0].decode()).get_expr_parse()
		return Expr(pt, prgm=self.prgm)
	
	def substitute(self,defconst):
		"Substitutes constants"
		if self.is_atom():
			if self.contents == defconst[0]:
				self.contents = defconst[1].contents
		else:
			for e in self.contents:
				e.substitute(defconst)
	
class Prgm:
	"Contains funcs, defconsts, Exprs."
	def __init__(self, pt):
		contents = list(Expr(_pt, prgm=self) for _pt in pt)
		self.defconsts = []
		self.funcs = []
		self.exprs = []
		for e in contents:
			defconst = e.as_defconst()
			if defconst:
				self.defconsts.append(defconst)
			else:
				func = e.as_func()
				if func:
					self.funcs.append(func)
				else:
					self.exprs.append(e)

	def defconst_to_expr(self,defconst):
		return Expr(['defconst', defconst[0], defconst[1]])

	def func_to_expr(self,func):
		return Expr(['defun']+func, prgm=self)

	def get_contents(self):
		return list(map(self.defconst_to_expr, self.defconsts)) + list(map(self.func_to_expr, self.funcs)) + self.exprs

	def __str__(self):
		return "\n\n\n".join(str(e) for e in self.get_contents())

	def step(self):
		if self.defconsts:
			self.substitute()
		elif not all(e.is_atom() for e in self.exprs):
			self.step_exprs()
	
	def substitute(self):
		defconst = self.defconsts[0]
		if defconst[1].is_atom():
			for e in list(defconst[1] for defconst in self.defconsts) + list(func[2] for func in self.funcs) + self.exprs:
				e.substitute(defconst)
			self.defconsts.pop(0)
		else:
			self.step_exprs(expr=defconst[1])
		
	def step_exprs(self, expr=None):
		exprs = self.exprs if expr==None else [expr]
		try:
			for e in exprs:
				e.step()
		except Completed_Step_Exception as ex:
			pass

if __name__ == '__main__':
	from argparse import ArgumentParser
	from sys import executable

	ap = ArgumentParser()
	ap.add_argument('filename', help='the path to an elisp program')
	ap.add_argument('--nostep', action='store_true', help='prevents the program from actually modifying the code, simply formatting it instead.')
	args = ap.parse_args()
	
	code = open(args.filename).read()
	prgm = Prgm(Parser(code).get_file_parse())
	if not args.nostep:
		prgm.step()
	print(prgm)
