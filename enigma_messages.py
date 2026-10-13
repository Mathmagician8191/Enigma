import datetime
import enigma
from string import ascii_uppercase
from sys import argv

def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]

if "decrypt" in argv:
  message = input("Message to decrypt: ").strip()
  metadata, ciphertext = message.split(" | ")
  time, length, key = metadata.split(" = ")
  assert int(length) == len(ciphertext.replace(" ", "")), "Corrupted message - failed length check"
  date, time = time.split(" ")
  initial_key, actual_key = key.split(" ")
  
  current_date = datetime.datetime.now()
  year = input("Enter message year (if not current): ") or current_date.year
  month = input("Enter message month (if not current): ") or current_date.month
  codesheet_path = f"codesheets/codesheet_{month}_{year}.csv"
  try:
    with open(codesheet_path) as file:
      codesheet_data = file.readlines()
  except FileNotFoundError:
    print(f"Missing codesheet for {year}-{month}")
  valid_days = set()
  settings = {}
  for line in codesheet_data:
    day, *fields, keys = line.strip().split(",")
    settings[day] = fields
    for key in keys.split(" "):
      if key in date:
        valid_days.add(day)
  if len(valid_days) == 1:
    day = list(valid_days)[0]
  else:
    if len(valid_days) == 0:
      print("Valid day not found")
    else:
      print("Found multiple valid days: " + str(valid_days))
    day = None
    while day not in settings:
      day = input("Enter day: ")
  rotors, rings, plugboard = settings[day]
  rotors = rotors.split(" ")
  rings = rings.split(" ")

  rotor_settings = []
  for rotor, ring, position in zip(rotors, rings, initial_key, strict=True):
    rotor_settings.append([rotor, ring, position])

  data = {
    "plaintext" : ciphertext.lower(),
    "key" : actual_key,
    "reflector" : "B",
    "plugboard" : plugboard,
    "rotors" : rotor_settings,
    "decrypt" : True,
  }

  plaintext = enigma.encode_enigma(data).upper()

  print(data['actual_key'], actual_key)

  print(f"{year}-{month}-{day} {time} {data['actual_key']} - {plaintext}")
else:
  import random

  time = datetime.datetime.now()
  codesheet_path = f"codesheets/codesheet_{time.month}_{time.year}.csv"
  try:
    with open(codesheet_path) as file:
      codesheet_data = file.readlines()
  except FileNotFoundError:
    print(f"Missing codesheet for {time.year}-{time.month}")
  valid_segments = []
  invalid_segments = []
  for line in codesheet_data:
    day, *fields, keys = line.strip().split(",")
    if day == str(time.day):
      rotors, rings, plugboard = fields
      rotors = rotors.split(" ")
      rings = rings.split(" ")
      valid_segments += keys.split(" ")
    else:
      invalid_segments += keys.split(" ")
  if len(valid_segments) == 0:
    print(f"Missing data for {time.year}-{time.month}-{time.day}")
    quit()
  military_time = str(time.hour) + str(time.minute)

  for x in range(10 ** 7):
    result = "".join(random.choice(ascii_uppercase) for _ in range(5))
    if any(key in result for key in valid_segments):
      if any(key in result for key in invalid_segments):
        print(f"Disqualified {result}")
      else:
        print(f"Found {result} in {x} attempts")
        break
  else:
    print("Could not find valid day indicator")
    quit()

  plaintext = input("Message to encrypt: ").replace(" ", "")
  initial_key = ""
  actual_key = ""
  for _ in range(3):
    initial_key += random.choice(ascii_uppercase)
    actual_key += random.choice(ascii_uppercase)

  rotor_settings = []
  for rotor, ring, position in zip(rotors, rings, initial_key, strict=True):
    rotor_settings.append([rotor, ring, position])

  data = {
    "plaintext" : plaintext.lower(),
    "key" : actual_key,
    "reflector" : "B",
    "plugboard" : plugboard,
    "rotors" : rotor_settings,
  }

  ciphertext = enigma.encode_enigma(data).upper()

  cipher_chunks = chunks(ciphertext, 5)

  ciphertext = " ".join(cipher_chunks)

  metadata = f"{result} {military_time} = {len(plaintext)} = {initial_key} {data['actual_key'].upper()}"

  print(f"{metadata} | {ciphertext}")
