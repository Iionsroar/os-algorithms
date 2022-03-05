from collections import UserList
from random import randrange

import numpy as np
import os
import platform
import time

def input_num(string):
  if "-" in string:
    raise Exception("Please enter a positive number")
  if str(float(string)).endswith('.0') :
    try: 
      return int(string)
    except:
      return float(string)
  return float(string)

class Input:
  def __init__(self, default:dict = {}):
    ACTIVITY = "Fixed Partition - Best Fit"
    STUDENT = "HALLOWEEN"
    self.HEADER = f"{ACTIVITY}\n{STUDENT}" 
    self.inputs = default
    self.refresh()


  def header(self):
    # TODO: identify and get os
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
  

  def input_num(self, 
    input_msg, 
    err_msg=None, 
    default=None, 
    store=True, 
    new_line=False,
    max_num=None
  ):
    if default == 0: # For when default value becomes 0
      default = "0"
    while not default:
      try:
        default = input_num(input(input_msg))
        if max_num is not None:
          if default > max_num:
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


class Partition:
	length: int = 0

	def __init__(self, size: int):
		self.__class__.length += 1
		self.id = self.__class__.length
		self.size = size
		self.job = None


	def __repr__(self):
		return f"P{self.id}({self.size}k)"


class Job:
	length: int = 0
	jobs: list = []

	def __init__(self, size: int, is_placeholder=False):
		self.is_oldest = False
		self.partition = None
		if is_placeholder:
			# random num for dealloc in first-fit
			self.size = 232323839223232323839283 
			return
		self.__class__.length += 1
		self.id = self.__class__.length
		self.size = size
		self.is_done = False
		self.is_oldest = False
		if not is_placeholder:
			self.__class__.jobs.append(self)


	def __repr__(self):
		if self.size == 232323839223232323839283:
			return ""
		return f"J{self.id}({self.size}k)"


	@classmethod
	def allocation_possible(cls, partitions: list):
		for partition in partitions:
			for job in cls.jobs:
				if not job.is_done and job.size < partition.size:
					return True
		return False


class Set(UserList):
	length: int = 0

	def __init__(
		self, 
		length: int,
		default: list = [],
		is_placeholder: bool = False,
		is_alloc: bool = True, 
	):
		self.__class__.length += 1
		if default:
			self.id = self.__class__.length
			self.data = list(default)
		elif is_placeholder:
			self.data = [Job(0, is_placeholder=is_placeholder) for i in range(length)]
		else:
			self.id = self.__class__.length
			self.data = [Job(randrange(0,30)) for i in range(length)]

		self.jobs = self.data


	def __repr__(self):
		return " ".join([repr(job) for job in self.data]).strip()


	def set(self, index: int, current_job: Job):
		self.jobs[index] = current_job
		for job in self.jobs:
			if sum([job.is_oldest for job in self.jobs]) < 2:
				current_job.is_oldest = True


	def unset_oldest_two(self):
		if not sum([job.is_oldest for job in self.jobs]):
			for i, job in enumerate([job for job in self.jobs if repr(job)]):
				if i > 1:
					break
				else:
					job.is_oldest = True

		for job in [job for job in self.jobs if job.is_oldest]:
			i = self.jobs.index(job)
			if not self.jobs[i].partition is None:
				self.jobs[i].partition.job = None
			self.jobs[i].is_oldest = False
			self.jobs[i] = Job(0, is_placeholder=True)

		for job in [job for job in self.jobs if repr(job)]:
			job.is_oldest = True


class Memory:
	def __init__(
		self, 
		capacity: int, 
		os_size: int,
	):
		self.capacity = capacity
		self.os_size = os_size
		self.partitions = []
		self.jobs = []

		self.len_allocation_sets = 0


	def __repr__(self):
		return f"OS({self.os_size}k)"


	def best_fit(self, inp: Input):
		self.sets = []
		alloc_set = Set(len(self.partitions), is_placeholder=True)
		dealloc_set = Set(len(self.partitions), is_alloc=False, is_placeholder=True)
		first_iter = True
		while Job.allocation_possible(self.partitions) or repr(dealloc_set):
			if not first_iter:
				alloc_set = Set(len(self.partitions), dealloc_set)

			# ALLOCATE
			for job in self.jobs:
				if job.partition:
					continue

				fit_partitions = [partition for partition in self.partitions if job.size <= partition.size and not partition.job]
				if fit_partitions:
					best_fit_partition = min(fit_partitions, key=lambda partition: partition.size)
					p_index = self.partitions.index(best_fit_partition)

					alloc_set.set(p_index, job)
					best_fit_partition.job = job
					job.partition = best_fit_partition
					job.is_done = True

			self.sets.append(alloc_set)
			self.len_allocation_sets += 1
			first_iter = False

			self.pprint_simulation(inp)

			# DEALLOCATE
			dealloc_set = Set(len(self.partitions), alloc_set)
			dealloc_set.unset_oldest_two()

			self.sets.append(dealloc_set)
			if not Job.allocation_possible(self.partitions) and not repr(dealloc_set):
				self.pprint_simulation(inp, store=True)
			else:
				self.pprint_simulation(inp)


	def get_remaining(self, job: Job = None, arr: list = None) -> int:
		if job:
			return self.capacity - self.os_size - job.size
		elif arr:
			return self.capacity - self.os_size - sum([obj.size for obj in arr])
		return self.capacity - self.os_size


	def get_input(
		self, 
		inp: Input,
		num_partitions: int,
		num_jobs: int,
		is_testing: bool = False
	):
		for name, arr, length in [
			['partitions', self.partitions, num_partitions], 
			['jobs', self.jobs, num_jobs]
		]:
			while len(arr) < length:
				is_last = len(arr) == (length - 1)

				if name == 'partitions':
					remaining = self.get_remaining(arr=arr)
					input_msg = f"\nAvailable space: {remaining}k\nEnter {name.title().strip('s')} size [{len(arr)+1}/{length}]: "
				else:
					input_msg = f"\nEnter {name.title().strip('s')} size [{len(arr)+1}/{length}]: "

				if is_testing:
					default=(randrange(15,30) if name == "partitions" else randrange(0,40))
				else:
					default=(remaining if is_last and name == "partitions" else None)

				size = inp.input_num(
					input_msg=input_msg,
					err_msg=f'Please use positive numbers {f"less than or equal {remaining}" if name == "partitions" else "only."}',
					default=default,
					store=False,
					new_line=True,
					max_num=remaining if name == 'partitions' else None)

				if name == 'partitions':
					arr.append(Partition(size))
				elif name == 'jobs':
					arr.append(Job(size))

				inp.refresh(seconds=0)

			matrix = [[repr(obj)[:2] for obj in arr], [obj.size for obj in arr]]
			self.pprint_matrix(name, matrix, inp)


	def pprint_matrix(self, name:str, matrix, inp:Input):
		# https://stackoverflow.com/questions/13214809/pretty-print-2d-list

		s = [[str(e) for e in row] for row in matrix]
		fmt = '\t'.join('{{:{}}}'.format(x) for x in [max(map(len, col)) for col in zip(*s)])
		matrix = '\n'.join([fmt.format(*row) for row in s])

		inp.input_num(input_msg=f"{name.title()} List:\n{matrix}", default=" ", new_line=True)
		inp.refresh(seconds=0)


	def pprint_simulation(self, inp: Input, store=False):
		self.out = [
			["Memory", "Partition"],
			["OS Partition", f"{self.os_size}k"],
		]
		for partition in self.partitions:
			row = [f"Partition {partition.id}", f"{partition.size}k"]
			j = 0
			for i, _set in enumerate(self.sets, start=1):
				if partition.id == 1:
					self.out[1].append("OS")
					if i % 2 != 0:
						self.out[0].append(f"Set {i - j}  ")
						j += 1
					else:
						self.out[0].append(f"Dealloc")
				row.append(_set[partition.id - 1])
			self.out.append(row)

		a = np.array(self.out)
		formatted = ''
		for row in a:
			for i, item in enumerate(row):
				formatted += (repr(item) if type(item) == type(Job(0, True)) else item).ljust(max(len(a[0][i]), len(a[1][i])) + 2)
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
		len_alloc = sum([job.is_done is True for job in self.jobs])
		print(f"Memory was allocated for {len_alloc} job(s) out of {len(self.jobs)}.")
		print(f"There were {self.len_allocation_sets} set(s) of allocations.")


def main(is_test=True):
	if is_test:
		inp = Input()
		mem = Memory(100, 10)
		mem.get_input(inp, 4, 8, is_testing=True) 
		mem.best_fit(inp)
		print()
		mem.report()
	else:
		inp = Input()
		mem = Memory(inp.input_num("Enter memory capacity [in k-unit]: ", 'Please use positive numbers only.'), 
			inp.input_num("Enter OS size  [in k-unit]: ", 'Please use positive numbers only.'))

		mem.get_input(inp, 
			inp.input_num("Enter number of partitions: ", 'Please use positive numbers only.'), 
			inp.input_num("Enter number of jobs: ", 'Please use positive numbers only.'))

		mem.best_fit(inp)
		print()
		mem.report()


main(is_test=False)

    
