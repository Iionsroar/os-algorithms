import os
import time
os.system('clear')
  
ACTIVITY = "Sorting 1"
STUDENT = "HALLOWEEN"

print(f"{ACTIVITY}\n{STUDENT}")

def convert(string):
  if str(float(string)).endswith('.0') :
    try: 
      return int(string)
    except:
      return float(string)
  return float(string)

numbers = []
while len(numbers)<10:
  num = input(f'Enter a number [{len(numbers) + 1}]:')
  try:
    numbers.append(convert(num))
  except:
    print('Please use numeric digits.')
    time.sleep(1)
    os.system('clear')
    
    print(f"{ACTIVITY}\n{STUDENT}")
    for i, num in enumerate(numbers):
      print(f'Enter a number [{i + 1}] : {num}')
    continue

print("\nInput Array:\n", numbers)

numbers.sort()
print("\nArray in Ascending Order:\n", numbers)

numbers.sort(reverse=True)
print("\nArray in Descending Order:\n", numbers)
