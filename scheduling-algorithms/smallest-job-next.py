import logging
import numpy as np
import os
import platform
import random
import time

logging.basicConfig(filename="logs.txt", level=logging.DEBUG)

class Input:
	def __init__(self, default:dict = {}, seconds=1):
		ACTIVITY = "Scheduling Algorithm: SJN"
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

	def to_positive_num(self, string):
		if "-" in string:
			raise Exception("Please enter a positive number")
		if str(float(string)).endswith('.0') :
			try: 
				return int(string)
			except:
				return float(string)
		return float(string)

	def pprint_matrix(self, matrix, name: str = None, store: bool = True):
		# https://stackoverflow.com/questions/13214809/pretty-print-2d-list

		s = [[str(e) for e in row] for row in matrix]
		fmt = '\t'.join('{{:{}}}'.format(x) for x in [max(map(len, col)) for col in zip(*s)])
		matrix = '\n'.join([fmt.format(*row) for row in s])

		output = self.input_num(
			input_msg=f"{name.title() if name else 'Given: '} \n{matrix}", 
			default=" ", 
			store=store,
			new_line=True
		)
		# self.refresh(seconds=0)
		return output

class Process:
	def __init__(self, id):
		self.id = id
		self.arrival_time = "-"
		self.burst_time = "-"
		self.is_completed = False
		self.time_completed = "-"

	def __repr__(self):
		if type(self.id) is not type(1):
			return f"{self.id}"
		return f"P{self.id}"

class ProcessManager:
	def __init__(self, num_process):
		self.num_process = num_process
		self.processes = []
		for i in range(1, self.num_process + 1):
			self.processes.append(Process(i))

	def get_input(
		self, 
		inp: Input,
		is_testing: bool = False,
		test_case: list = []
	):
		for i, process in enumerate(self.processes):
			temp_inp = Input(default=dict(inp.inputs), seconds=0)
			matrix = [
				["Process"] + [process for process in self.processes],
				["Arrival Time"] + [process.arrival_time for process in self.processes],
				["Burst Time"] + [process.burst_time for process in self.processes],
			]
			print() # spacer
			temp_inp.pprint_matrix(
				matrix, 
				name='', 
				store=True
			)

			input_msg = f"\nEnter arrival time for {process}: "
			default = random.randrange(0,100,10) if is_testing else None
			default = test_case[i][0] if test_case else default
			arrival_time = temp_inp.input_num(
				input_msg=input_msg,
				err_msg=f'Please enter a positive number',
				default=default,
				store=True,
				min_num=0)

			process.arrival_time = arrival_time

			input_msg = f"Enter burst time for {process}: "
			default = random.randrange(10,100,10) if is_testing else None
			default = test_case[i][1] if test_case else default
			burst_time = temp_inp.input_num(
				input_msg=input_msg,
				err_msg=f'Please enter a positive number',
				default=default,
				store=True,
				min_num=0)

			process.burst_time = burst_time

			inp.refresh(seconds=0)

		matrix = [
			["Process"] + [process for process in self.processes],
			["Arrival Time"] + [process.arrival_time for process in self.processes],
			["Burst Time"] + [process.burst_time for process in self.processes],
		]
		print() # spacer
		inp.pprint_matrix(
			matrix, 
			name='', 
			store=True
		)

	def has_pending_process(self) -> bool:
		for process in self.processes:
			if not process.is_completed:
				return True
		return False

	def run_sjn(self, inp: Input):
		time = 0
		self.timeline = []
		for process in self.processes:
			process.updated_arrival_time = process.arrival_time
		while self.has_pending_process():
			for process in self.processes:
				if process.arrival_time < time:
					process.updated_arrival_time = 0
			self.processes.sort(
				key=lambda process: (process.updated_arrival_time, process.burst_time, process.id if type(process.id) == type(1) else 1) # NOTE fallback val of 1 might yield errors
			)
			logging.info([process.id for process in self.processes])
			process = self.processes[0]
			process.is_completed = True
			if process.arrival_time - time > 0:
				idle = Process("Idle")
				idle.time_completed = process.arrival_time
				time += process.arrival_time
				self.timeline.append(idle)
			time += process.burst_time
			process.time_completed = time
			self.processes.remove(process)
			self.timeline.append(process)

		self.pprint_timeline(inp)

	def pprint_timeline(self, inp: Input):
		for i, process in enumerate(self.timeline):
			temp_inp = Input(default=dict(inp.inputs), seconds=0)
			matrix = [
				["Process"] + [process for process in self.timeline[:i+1]],
				["Time Completed"] + [process.time_completed for process in self.timeline[:i+1]],
			]
			print() # spacer
			temp_inp.pprint_matrix(
				matrix, 
				name='Timeline starts at 0: ', 
				store=False
			)
			if process != self.timeline[-1]:
				input("Press ENTER to continue . . . ")

	def report(self):
		self.average_tat = np.mean([process.time_completed - process.arrival_time for process in self.timeline if process.is_completed])
		self.average_wt = np.mean([process.time_completed - process.arrival_time - process.burst_time for process in self.timeline if process.is_completed])
		print(f"Average Turnaround Time: {round(self.average_tat, 2)}")
		print(f"Average Waiting Time: {round(self.average_wt, 2)}")

def main(is_test=True):
	if is_test:
		inp = Input()
		# test_case = [(0, 70), (10, 50), (20, 30), (30, 10), (40, 20), (50, 10)] 
		# test_case = [(0, 140), (40, 75), (50, 320), (300, 280), (315, 125)] 
		# test_case = [(10, 50), (20, 45), (30, 25), (55, 65), (60, 30)] 
		# test_case = [(10, 10), (30, 10), (50, 30), (30, 10), (40, 20), (30, 5)] # incorrect display: does not display idles
		# num_process = len(test_case)
		num_process = random.randrange(4,7)
		manager = ProcessManager(
			num_process,
		)
		manager.get_input(inp, is_testing=True, test_case=None) 
		# manager.get_input(inp, is_testing=True, test_case=test_case) 
		manager.run_sjn(inp)
		print()
		manager.report()
	else:
		inp = Input()
		manager = ProcessManager(
			inp.input_num(
				"Enter number of processes: ", 
				'Please use positive numbers only. Min = 2, Max = 9', 
				store=False,
				min_num=2, 
				max_num=9
				), 
		)
		manager.get_input(inp)
		manager.run_sjn(inp)
		print()
		manager.report()

main(is_test=True)