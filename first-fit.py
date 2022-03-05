from random import randrange
from collections import UserList

import os
import time
import numpy as np

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
    ACTIVITY = "Fixed Partition - First Fit"
    STUDENT = "HALLOWEEN"
    self.HEADER = f"{ACTIVITY}\n{STUDENT}" 
    self.inputs = default
    self.refresh()


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
    new_line=False
  ):
    while not default:
      try:
        default = input_num(input(input_msg))
        if new_line:
          print()
        if store:
          self.inputs[input_msg] = default
        return default
        
      except:
        if not err_msg is None:
          print(err_msg)
        self.refresh()
        continue
    else:
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
    if is_placeholder:
      # random num for dealloc in first-fit
      self.size = 232323839223232323839283 
      return
    self.__class__.length += 1
    self.id = self.__class__.length
    self.size = size
    self.partition = None
    self.is_done = False
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


  def first_fit(self, inp: Input):
    self.sets = []
    alloc_set = Set(len(self.partitions), is_placeholder=True)
    dealloc_set = Set(len(self.partitions), is_alloc=False, is_placeholder=True)
    first_iter = True
    # while repr(dealloc_set):
    while Job.allocation_possible(self.partitions) or repr(dealloc_set):
      # ALLOCATE
      if not first_iter:
        alloc_set = Set(len(self.partitions), dealloc_set)
      for p_index, partition in enumerate(self.partitions):
        if partition.job:
          continue

        for job in self.jobs:
          if job.partition:
            continue
          elif job.size <= partition.size:
            alloc_set[p_index] = job
            partition.job = job
            job.partition = partition
            job.is_done = True
            break
      self.sets.append(alloc_set)
      self.len_allocation_sets += 1
      first_iter = False

      self.pprint_first_fit(inp)

      # DEALLOCATE
      dealloc_set = Set(len(self.partitions), alloc_set)
      for i in range(2):
        try:
          index = dealloc_set.index(min(dealloc_set.jobs, key=lambda job: job.size))
          dealloc_set[index].partition.job = None
          dealloc_set[index] = Job(0, is_placeholder=True)
        except:
          break

      self.sets.append(dealloc_set)

      if not Job.allocation_possible(self.partitions) and not repr(dealloc_set):
        self.pprint_first_fit(inp, store=True)
      else:
        self.pprint_first_fit(inp)



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
          err_msg='Please use positive numbers only.',
          default=default,
          store=False,
          new_line=True)
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


  def pprint_first_fit(self, inp: Input, store=False):
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


inp = Input()
mem = Memory(inp.input_num("Enter memory capacity [in k-unit]: ", 'Please use positive numbers only.'), 
  inp.input_num("Enter OS size  [in k-unit]: ", 'Please use positive numbers only.'))

mem.get_input(inp, 
  inp.input_num("Enter number of partitions: ", 'Please use positive numbers only.'), 
  inp.input_num("Enter number of jobs: ", 'Please use positive numbers only.'))

mem.first_fit(inp)
print()
mem.report()