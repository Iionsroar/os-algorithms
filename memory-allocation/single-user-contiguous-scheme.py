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
  def __init__(self, default:dict = {}, seconds=0):
    ACTIVITY = "Single-User Contiguous Scheme"
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
    refresh=False,
    new_line=False
  ):
    while not default:
      if refresh:
        self.refresh()
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
      print(input_msg, default)
      if new_line:
        print()
      return default
    

class SingleUserContiguousScheme:
  def __init__(self, 
    mem_capacity:int, 
    os_size:int, 
    default:dict = {},
    seconds=0
  ):
    self.mem_capacity = mem_capacity

    self.os_size = os_size
    self.os = f"OS({self.os_size}k)" 

    self.unused_space = self.mem_capacity - self.os_size
    self.current_job_size = None
    self.current_job = None

    self.default = dict(default)
    self.temp = Input(dict(default), seconds=seconds)
    self.temp.refresh("\nBuilding the system", seconds=3)

    self.successful_allocations = []
    self.unsuccessful_allocations = {'size': [], 'status': []}


  def allocate(self, job_num:int, job_size:int):
    job = f"J{job_num}({job_size}k)"

    if self.current_job:
      print(f"Allocation failed. Partition is currently handling a job: {self.current_job}")
      self.unsuccessful_allocations['status'].append(job)
      return " "

    elif job_size > self.unused_space:
      print(f"Memory for {job} could not be allocated.")
      print(f"Remaining capacity is {self.unused_space}k.")
      self.unsuccessful_allocations['size'].append(job)
      return " "

    else:
      self.unused_space = self.unused_space - job_size
      self.current_job_size = job_size
      self.current_job = job

      unused = f"Unused({self.unused_space}k)"
      self.successful_allocations.append(self.current_job)
      if self.current_job in self.unsuccessful_allocations['status']:
        self.unsuccessful_allocations['status'].remove(self.current_job)
      return  f"{self.os}, {job}, {unused}\nMemory for {job} was successfully allocated."


  def report(self):
    print("\nConclusions: ")
    print(f"Successfully allocated memory for {len(self.successful_allocations)} job(s):")
    print(' '.join(self.successful_allocations), end="\n\n")
    print(f"Allocation failed for {len(self.unsuccessful_allocations['size'])} job(s) because of huge size:")
    print(' '.join(self.unsuccessful_allocations['size']), end="\n\n")
    print(f"Allocation failed for {len(set(self.unsuccessful_allocations['status']))} job(s) because partition is currently handling a job:")
    print(' '.join(set(self.unsuccessful_allocations['status'])))


  def deallocate(self):
    if self.current_job:
      print(f"Memory for {self.current_job} was successfully deallocated.")
      self.unused_space += self.current_job_size
      self.current_job = None
      self.current_job_size = None
      self.temp.inputs = dict(self.default)
    else:
      print(f"Deallocation failed.\nPartition is not handling a job.")


  def exec(self, action:int, job_num, job_size, inp:Input):
    if action == 1:
      self.temp.input_num(self.allocate(job_num, job_size), default=" ", new_line=True)
    elif action == 2:
      self.deallocate()



inp = Input()
mem_capacity = inp.input_num("Enter memory capacity [in k-unit]: ", 
  'Please use positive numbers only.')
os_size = inp.input_num("Enter OS size  [in k-unit]: ", 
  'Please use positive numbers only.')

JOB_LENGTH = 6
job_labels = []
jobs = []
while len(jobs) < JOB_LENGTH:
  is_last = len(jobs) == (JOB_LENGTH - 1)
  input_msg = f"\nEnter the size for this job [{len(jobs)+1}/{JOB_LENGTH}]: "
  jobs.append(inp.input_num(
    input_msg=input_msg,
    err_msg='Please use positive numbers only.',
    # default=remaining,
    store=False,
    new_line=True
    ))
  job_labels.append(f"J{len(jobs)}")
  if not is_last: 
    inp.refresh(seconds=0)

# https://stackoverflow.com/questions/13214809/pretty-print-2d-list
matrix = [job_labels, jobs]
s = [[str(e) for e in row] for row in matrix]
fmt = '\t'.join('{{:{}}}'.format(x) for x in [max(map(len, col)) for col in zip(*s)])
matrix = '\n'.join([fmt.format(*row) for row in s])

inp.input_num(input_msg=f"Job List:\n{matrix}", default=" ", new_line=True)
mem = SingleUserContiguousScheme(mem_capacity, os_size, default=dict(inp.inputs))
for i, job in enumerate(jobs):
  i = i + 1 # standard counting

  mem.temp.refresh(seconds=1)
  prompt = f"\nLoading J{i}({job}k) into memory:\nAllocate[1], Deallocate[2], or Proceed[ENTER]? " 
  user_in = input(prompt)
  while user_in in ("1","2"):
    print()
    mem.exec(int(user_in), i, job, inp)
    mem.temp.refresh(seconds=4 if len(mem.temp.inputs) > 4 else 2)
    user_in = input(prompt)
  else:
    if i < JOB_LENGTH:
      print(f"\nTask finished. Proceeding to J{i+1}...")
    else:
      inp.refresh()
    continue

print("\nTask finished. Generating report...")
inp.refresh(seconds=3)
mem.report()