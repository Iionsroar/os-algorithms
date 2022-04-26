from collections import UserList
from random import randrange

import logging
import numpy as np
import os
import platform
import time

logging.basicConfig(level=logging.DEBUG)
logging.disable(level=logging.DEBUG)

class Input:
  def __init__(self, default:dict = {}, seconds=1):
    ACTIVITY = "Relocatable Dynamic Partition"
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
  

  def input_num(self, 
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

  def to_positive_num(self, string):
	  if "-" in string:
	    raise Exception("Please enter a positive number")
	  if str(float(string)).endswith('.0') :
	    try: 
	      return int(string)
	    except:
	      return float(string)
	  return float(string)


class Partition:
	length: int = 0

	def __init__(self, size: int, is_placeholder: bool = False):
		self.__class__.length += 1
		self.id = self.__class__.length
		self.size = size
		self.job = None
		self.is_placeholder = is_placeholder

	def __repr__(self):
		return f"P{self.id}({self.size}k)"


class Job:
	length: int = 0
	jobs: list = []

	def __init__(self, size: int, turnaround_time: int = None, is_placeholder=False):
		self.is_placeholder = is_placeholder
		self.is_oldest = False
		self.partition = None
		self.turnaround_time = turnaround_time
		if self.is_placeholder:
			# random num for dealloc in first-fit
			self.size = 232323839223232323839283 
			return
		self.__class__.length += 1
		self.id = self.__class__.length
		self.name = f"J{self.id}"
		self.size = size
		self.is_done = False
		self.is_executed = False
		self.is_oldest = False
		if not self.is_placeholder:
			self.__class__.jobs.append(self)


	def __repr__(self):
		if self.size == 232323839223232323839283:
			return ""
		return f"J{self.id}({self.size}k)"


	@classmethod
	def allocation_possible(cls, jobs: list, partitions: list):
		for partition in partitions:
			for job in jobs:
				if not job.is_executed and job.size < partition.size:
					return job
		return None


class Set(UserList):
	length: int = 0

	def __init__(
		self, 
		length: int = None,
		default: list = [],
		is_placeholder: bool = False,
		is_alloc: bool = True, 
	):
		self.__class__.length += 1
		self.data = []
		if default:
			self.id = self.__class__.length
			self.data = list(default)
		elif is_placeholder:
			self.data = [Job(0, is_placeholder=is_placeholder) for i in range(length)]

		self.jobs = self.data


	def __repr__(self):
		return " ".join([repr(job) if repr(job) else "J0(0k)" for job in self.data]).strip()

	def has_jobs(self):
		if " ".join([repr(job) for job in self.data]).strip():
			return True
		else:
			return False

	def has_vacant(self):
		for job in self.data:
			if job.is_placeholder:
				return True
		return False

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

	def turnaround(self):
		for job in self.jobs:
			if not job.is_placeholder:
				if job.turnaround_time > 0:
					job.turnaround_time -= 1


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
		self.sets = []

		self.len_allocation_sets = 0

	def __repr__(self):
		return f"OS({self.os_size}k)"

	def relocatable_part(self, inp: Input):
		if self.create_partitions().has_jobs():
			self.len_allocation_sets += 1

		alloc_set = Set(default=self.sets[0])
		# logging.info(f"Alloc: {alloc_set}")
		dealloc_set = Set(default=alloc_set)
		first_iter = True
		self.pprint_simulation(inp)
		while Job.allocation_possible(jobs=self.jobs, partitions=self.partitions) or dealloc_set.has_jobs():
			# ALLOCATE
			if not first_iter:
				alloc_set = Set(default=dealloc_set)
				while alloc_set.has_vacant():
					for job in alloc_set:
						if job.is_placeholder:
							alloc_set.remove(job)
				alloc_set = self.create_partitions(default=alloc_set)
				# logging.info(f"Parti: {self.partitions}; Alloc: {alloc_set}")
				diff = len(self.sets[0]) - len(alloc_set)
				if diff:
					for i in range(diff):
						alloc_set.append(Job(0, is_placeholder=True))

				self.len_allocation_sets += 1

				# logging.info(f"Alloc: {alloc_set.jobs}")
				self.pprint_simulation(inp)


			first_iter = False

			# TURNAROUND
			alloc_set.turnaround()

			# DEALLOCATE
			dealloc_set = Set(default=alloc_set)
			for i, job in enumerate(dealloc_set):
				if job.turnaround_time == 0:
					if not dealloc_set[i].partition:
						dealloc_set[i].partition = None
					dealloc_set[i] = Job(0, is_placeholder=True)
			self.sets.append(dealloc_set)

			# logging.info(f"Deall: {dealloc_set}")
			if not Job.allocation_possible(jobs=self.jobs, partitions=self.partitions) and not dealloc_set.has_jobs():
				self.pprint_simulation(inp, store=True)
				pass
			else:
				self.pprint_simulation(inp)
				pass


	def get_remaining(self, job: Job = None, arr: list = None) -> int:
		if job:
			return self.capacity - self.os_size - job.size
		elif arr:
			return self.capacity - self.os_size - sum([obj.size for obj in arr])
		return self.capacity - self.os_size


	def get_input(
		self, 
		inp: Input,
		num_jobs: int,
		is_testing: bool = False
	):
		arr = self.jobs
		while len(arr) < num_jobs:
			is_last = len(arr) == (num_jobs - 1)

			# USED IN ACTIV 
			# test_case = [(40, 2), (50, 3), (35, 2), (20, 1), (25, 2), 
			# 						(60, 3), (10, 1), (15, 1), (45, 3), (30, 2)]

			# EXISTING BUG # 1 
			test_case = [(91, 1), (47, 2), (52, 1), (86, 3), (98, 1),
										(26, 1), (57, 2), (63, 3), (27, 2), (97, 2)]

			input_msg = f"\nEnter job size [{len(arr)+1}/{num_jobs}]: "
			# default = randrange(1,100) if is_testing else None
			default = randrange(100,1000) if is_testing else None
			default = test_case[len(arr)][0] if is_testing else None
			temp_inp = Input(default=dict(inp.inputs), seconds=0)
			size = temp_inp.input_num(
				input_msg=input_msg,
				err_msg=f'Please use positive numbers only. Minimum job size for this program is 1.',
				default=default,
				store=True,
				min_num=1)

			input_msg = f"Enter turnaround size for this job: "
			default = randrange(1,4) if is_testing else None
			default = test_case[len(arr)][1] if is_testing else None
			turnaround_time = temp_inp.input_num(
				input_msg=input_msg,
				err_msg=f'Please use positive numbers only. Maximum TAT for this program is 3.',
				default=default,
				store=True,
				new_line=True,
				min_num=1,
				max_num=3)

			arr.append(Job(size, turnaround_time))

			inp.refresh(seconds=0)

		matrix = [
			['Name'] + [obj.name for obj in arr], 
			['Size'] + [obj.size for obj in arr], 
			['TAT'] + [obj.turnaround_time for obj in arr]
		]
		self.pprint_matrix('job', matrix, inp)


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
		partition_count = 1
		partitions = list(self.partitions)
		if len(partitions) < len(self.sets[0]):
			for i in range(len(self.sets[0]) - len(partitions)):
				partitions.append(Partition(0, is_placeholder=True))
		# logging.info(f"Partitions in simul: {partitions}")

		# for set_ in self.sets:
			# logging.info(f"Set: {set_}")
		for i, partition in enumerate(partitions):
			try:
				name_out = f"Partition {partition_count}" if partition.size or partitions[i-1].size else ""
				size_out = f"{partition.size}k" if partition.size else ""
				if not partition.size and partitions[i-1].size:
					size_out = f"{self.get_remaining(arr=partitions)}k"
			except:
				name_out = f"Partition {partition_count}" if partition.size else ""
				size_out = f"{partition.size}k" if partition.size else ""

			row = [name_out, size_out]
			j = 0
			for i, _set in enumerate(self.sets, start=1):
				if partition_count == 1:
					self.out[1].append("OS")
					if i % 2 != 0:
						self.out[0].append(f"Set {i - j}  ")
						j += 1
					else:
						self.out[0].append(f"Dealloc")
				# row.append(_set[partition.id - 1])
				row.append(_set[partition_count - 1])
			partition_count += 1

			str_row = ''.join([repr(obj) for obj in row]) 
			is_empty = True if "'0k'" in str_row else False
			if not is_empty and str_row.strip().strip("'"): # append only rows with values
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
		len_alloc = sum([job.is_executed is True for job in self.jobs])
		print(f"Memory was allocated for {len_alloc} job(s) out of {len(self.jobs)}.")
		print(f"There were {self.len_allocation_sets} set(s) of allocations.")

		if len(self.jobs) - len_alloc:
			print(f"\nThe following job(s) were not served because of huge size:")
			print(f"{Set(default=[job for job in self.jobs if not job.is_executed])}")

	def create_partitions(self, default: list = None):
		alloc_set = []
		self.partitions = []
		if default:
			for job in default:
				self.partitions.append(Partition(job.size))
				alloc_set.append(job)

		for job in self.jobs:
			if job.size <= self.get_remaining(arr=self.partitions) and not job.is_executed:
				partition = Partition(job.size)
				self.partitions.append(partition)

				alloc_set.append(job)
				partition.job = job
				job.is_executed = True

		if not default: # create_partition is called during start of algo
			if self.get_remaining(arr=self.partitions):
				remaining = self.get_remaining(arr=self.partitions)
				self.partitions.append(Partition(remaining))
				for job in self.jobs:
					if not job.is_executed and job.size < remaining:
						alloc_set.append(job)
					else:
						alloc_set.append(Job(0, is_placeholder=True))
		else: # create_partition is called in-allocation
			for i in range(len(self.sets[0]) - len(alloc_set)):
				alloc_set.append(Job(0, is_placeholder=True))

		alloc_set = Set(default=alloc_set)
		self.sets.append(alloc_set)

		return alloc_set



def main(is_test=True):
	if is_test:
		inp = Input()
		mem = Memory(200, 10)
		mem.get_input(inp, 10, is_testing=True) 
		mem.relocatable_part(inp)
		print()
		mem.report()
	else:
		inp = Input()
		mem = Memory(inp.input_num("Enter memory capacity [in k-unit]: ", 'Please use positive numbers only.', min_num=1), 
			inp.input_num("Enter OS size  [in k-unit]: ", 'Please use positive numbers only.', min_num=1))

		mem.get_input(inp, 
			inp.input_num("Enter number of jobs: ", 'Please use positive numbers only.', min_num=1))

		mem.relocatable_part(inp)
		print()
		mem.report()

# TODO: looks better if size is placed at last column
# TODO: python tool to remove unused libraries, functions, etc
main(is_test=False)

    
