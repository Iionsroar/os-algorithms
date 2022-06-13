import os
import time

ACTIVITY = "Sorting 2"
STUDENT = "HALLOWEEN"
HEADER = f"{ACTIVITY}\n{STUDENT}" 
os.system('clear')
print(HEADER)

def refresh(msg=None, seconds=1):
  if not msg is None:
    print(msg)
  time.sleep(seconds)
  os.system('clear')

  print(HEADER)

def sort(arr):
  arr.sort()
  print("\nArray in Ascending Order:\n", arr)

  arr.sort(reverse=True)
  print("\nArray in Descending Order:\n", arr)

def to_number(string):
  if str(float(string)).endswith('.0') :
    try: 
      return int(string)
    except:
      return float(string)
  return float(string)

while True:
  length = input("Enter array length: ")
  if not length.isnumeric(): 
    refresh('Please enter a whole number greater than one.', 1.5)
    continue

  length = int(length)
  if length < 2:
    refresh('Please use a whole number greater than one.', 1.5)
    continue

  break

numbers = []
while len(numbers) < length:
  num = input(f'Enter a number [{len(numbers) + 1}/{length}]:')
  try:
    numbers.append(to_number(num))
  except:
    refresh('Please use numeric digits.')
    continue

  sort(numbers)
  input('\nPress ENTER to continue.')
  refresh(seconds=0)

print('FINAL OUTPUT:')
sort(numbers)