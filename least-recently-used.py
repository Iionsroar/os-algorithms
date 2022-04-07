from collections import UserList
from typing import List

import logging
import numpy as np
import os
import platform
import random
import string
import time

logging.basicConfig(level=logging.DEBUG)

class Input:
	LETTERS = string.ascii_uppercase
	def __init__(self, default:dict = {}, seconds=1):
		ACTIVITY = "Replacement Algorithm: LRU"
		STUDENT = "HALLOWEEN"
		self.HEADER = f"{ACTIVITY}\n{STUDENT}" 
		self.inputs = default
		self.refresh(seconds=seconds)


	def header(self):
		if platform.system() == "Windows":
			os.system('cls')
		else:
			os.system('clear')
		print(self.HEADER, end="\n\n")


	def refresh(self, msg=None, seconds=1):
		if not msg is None:
			print(msg, end="")
			if seconds > 1:
				for i in range(seconds):
					time.sleep(0.5)
					print(".", end="")
				seconds = 0

		time.sleep(seconds)
		self.header()
		for msg, val in self.inputs.items():
			nl = "\n"
			if msg == ' ' and val == ' ':
				continue
			print(f"{nl if val == ' ' else ''}{msg}{val}")
	

	def input_num(
		self, 
		input_msg, 
		err_msg=None, 
		default=None, 
		store=True, 
		new_line=False,
		max_num=None,
		min_num=None
	):
		if default == 0: # For when default value becomes 0
			default = "0"
		while not default:
			try:
				default = self.to_positive_num(input(input_msg))
				if max_num is not None:
					if default > max_num:
						default = None
						raise Exception

				if min_num is not None:
					if default < min_num:
						default = None
						raise Exception

				if new_line:
					print()
				if store:
					self.inputs[input_msg] = default
				return default
				
			except:
				if not err_msg is None:
					print(err_msg)
				self.refresh(seconds=1.5)
				continue
		else:
			if default == "0": # For when default value becomes 0
				default = 0
			if store:
				self.inputs[input_msg] = default
			if input_msg:
				print(input_msg, default)
			else:
				print(default)
			if new_line:
				print()
				
			return default

	def input_char(
		self, 
		input_msg, 
		err_msg=None, 
		default=None, 
		store=True, 
		new_line=False,
		max_char=None,
		err_msg_seconds=1.5
	):
		if default == 0: # For when default value becomes 0
			default = "0"
		while not default:
			try:
				default = input(input_msg)
				if max_char is not None:
					if self.__class__.LETTERS.index(default.upper()) > (max_char) or len(default) == 0:
						raise Exception
				
				if new_line:
					print()
				if store:
					self.inputs[input_msg] = default
				return default
				
			except:
				default = None
				if not err_msg is None:
					print(err_msg)
				self.refresh(seconds=err_msg_seconds)
				continue
		else:
			if default == "0": # For when default value becomes 0
				default = 0
			if store:
				self.inputs[input_msg] = default
			if input_msg:
				print(input_msg, default)
			else:
				print(default)
			if new_line:
				print()
				
			return default

	def to_positive_num(self, string):
		if "-" in string:
			raise Exception("Please enter a positive number")
		if str(float(string)).endswith('.0') :
			try: 
				return int(string)
			except:
				return float(string)
		return float(string)

class Frame:
	def __init__(self, id: int):
		self.id = id
		self.page = None

	def __repr__(self):
		return f"{self.page if self.page else ''}"

class Page:
	pages = []
	def __init__(self, id: str):
		self.id = id
		self.frame = None
		self.__class__.pages.append(self)

	def __repr__(self):
		return self.id

	@classmethod
	def get_by_id(cls, id):
		for page in cls.pages:
			if page.id == id:
				return page
		return None


class Partition(UserList):
	def __init__(self, frame_count: int):
		self.frames = []
		self.data = self.frames
		self.sets = []
		self.page_faults = 0
		for i in range(1, frame_count + 1):
			self.frames.append(Frame(id=i))

		self.current_set = [repr(frame) for frame in self.frames] + [None]

	def has_vacant(self):
		for frame in self.frames:
			if not frame.page:
				return True
		return False

	def has_page(self, page: str):
		current_set = [repr(frame) for frame in self.frames]
		if page in current_set:
			return True
		return False

	def populate(self, page: str):
		current_set = self.current_set
		if self.has_page(page):
			current_set[-1] = ' '
		else:
			page = Page.get_by_id(page)
			index_empty_frame = current_set.index('')
			self.frames[index_empty_frame].page = page
			current_set[index_empty_frame] = repr(page)
			page.frame = self.frames[index_empty_frame]
			current_set[-1] = '*'
			self.page_faults += 1
		self.store(current_set)

	def store(self, _set: List[Frame]):
		self.sets.append(list(_set))

	def replace_LRU(self, previous_pages: List[str], page: str):
		current_set = self.current_set
		previous_pages.reverse()
		reference_pages = []
		# 4  7	3	0	1	7	3
		# 3 1 7
		# 3 7 1
		for i, pg in enumerate(previous_pages):
			if len(reference_pages) == len(self.frames):
				break
			if pg in current_set and not pg in reference_pages:
				reference_pages.append(pg)
		page_to_replace = max(current_set[:-1], key=lambda page: reference_pages.index(page))

		page = Page.get_by_id(page)
		index_page_to_replace = current_set.index(page_to_replace)

		self.frames[index_page_to_replace].page.frame = None
		page.frame = self.frames[index_page_to_replace]
		self.frames[index_page_to_replace].page = page
		current_set[index_page_to_replace] = repr(page)
		current_set[-1] = '*'
		self.page_faults += 1
		self.store(current_set)



class Memory:
	def __init__(
		self, 
		frame_count: int, 
		page_count: int, 
		page_request_count: int,
	):
		self.frame_count = frame_count
		self.page_count = page_count
		self.page_request_count = page_request_count
		self.page_list = [repr(Page(id=letter)) for letter in list(Input.LETTERS[:self.page_count])]
		self.requested_pages = [] # get_input() to fill

		self.partition = Partition(self.frame_count)

	def allocate(self, inp: Input):
		for i, requested_page in enumerate(self.requested_pages):
			if self.partition.has_page(requested_page) or self.partition.has_vacant():
				self.partition.populate(requested_page)
			else:
				self.partition.replace_LRU(
					previous_pages=self.requested_pages[:i+1],
					page=requested_page
				)
			self.pprint_simulation(inp, store=True if i == len(self.requested_pages) - 1 else False) 


	def get_input(
		self, 
		inp: Input,
		is_testing: bool = False
	):
		matrix = [
			[page for page in self.page_list],
		]
		self.pprint_matrix('page', matrix, inp)
		
		while len(self.requested_pages) < self.page_request_count:
			is_last = len(self.requested_pages) == (self.page_request_count - 1)

			input_msg = f"\nEnter page request [{len(self.requested_pages)+1}/{self.page_request_count}]: "
			default = random.choices(self.page_list)[0] if is_testing else None
			page_name = inp.input_char(
				input_msg=input_msg,
				err_msg=f'Please enter a single alphabetic character from: [{", ".join(self.page_list)}]',
				default=default,
				store=False,
				max_char=self.page_count - 1,
				err_msg_seconds=2)

			self.requested_pages.append(page_name.upper())

			inp.refresh(seconds=0)


	def pprint_matrix(self, name:str, matrix, inp:Input):
		# https://stackoverflow.com/questions/13214809/pretty-print-2d-list

		s = [[str(e) for e in row] for row in matrix]
		fmt = '\t'.join('{{:{}}}'.format(x) for x in [max(map(len, col)) for col in zip(*s)])
		matrix = '\n'.join([fmt.format(*row) for row in s])

		inp.input_num(input_msg=f"{name.title()} List:\n{matrix}", default=" ", new_line=True)
		inp.refresh(seconds=0)

	def pprint_simulation(self, inp: Input, store=False):
		pass
		self.out = [
			["       "] + [requested_page for requested_page in self.requested_pages],
		]
		for r in range(len(self.partition.sets[-1])):
			row = [f"Frame {r + 1}" if r != len(self.partition.sets[-1]) - 1 else "PF"]
			for i, _set in enumerate(self.partition.sets):
				row.append(_set[r])
			self.out.append(row)

		a = np.array(self.out, dtype=object)
		formatted = ''
		for row in a:
			for i, item in enumerate(row):
				formatted += item.ljust(len(a[0][i]) + 2)
			formatted += '\n'	

		print()
		inp.input_num(
			input_msg=formatted,
			default=" ",
			store=store,
			new_line=True
		)
		input("Press ENTER to continue")
		inp.refresh(seconds=0)

	def report(self):
		print(f"No. of Page Faults: {self.partition.page_faults}")
		print(f"No. of Page Hits: {self.page_request_count - self.partition.page_faults}")

def main(is_test=True):
	if is_test:
		inp = Input()
		mem = Memory(
			random.randrange(3, 5),
			# random.randrange(4, 8),
			# random.randrange(8, 16),
			random.randrange(5, 9),
			random.randrange(8, 16),
		)
		mem.get_input(inp, is_testing=True) 
		mem.allocate(inp)
		print()
		mem.report()
	else:
		inp = Input()
		mem = Memory(
			inp.input_num("Enter number of frames: ", 'Please use positive numbers only. Max = 9', min_num=1, max_num=9), 
			inp.input_num("Enter number of pages: ", 'Please use positive numbers only. Max = 26', min_num=1, max_num=26),
			inp.input_num("Enter number of requested pages: ", 'Please use positive numbers only. Max = 26', min_num=1, max_num=26),
			)

		mem.get_input(inp)
		mem.allocate(inp)
		print()
		mem.report()

main(is_test=False)
