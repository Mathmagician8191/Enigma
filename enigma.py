import pyjson5
import string

def decode(number):
  return string.ascii_lowercase[number]

encode = {
  "a" : 0,
  "b" : 1,
  "c" : 2,
  "d" : 3,
  "e" : 4,
  "f" : 5,
  "g" : 6,
  "h" : 7,
  "i" : 8,
  "j" : 9,
  "k" : 10,
  "l" : 11,
  "m" : 12,
  "n" : 13,
  "o" : 14,
  "p" : 15,
  "q" : 16,
  "r" : 17,
  "s" : 18,
  "t" : 19,
  "u" : 20,
  "v" : 21,
  "w" : 22,
  "x" : 23,
  "y" : 24,
  "z" : 25
}

def build_rotor_map(raw_rotor_map):
  rotor_map = {}
  for key, data in raw_rotor_map.items():
    rotor, rotate_positions = data
    rotor = [encode[char] for char in rotor.lower()]
    rotate_positions = [encode[position] for position in rotate_positions]
    rotor_map[key] = (rotor, rotate_positions)
  return rotor_map

def compile_rotors(rotors):
  result = []
  for rotor, ring, position in rotors:
    ring = -encode[ring.lower()]
    position = encode[position.lower()]
    rotor, rotate = rotor_map[rotor]
    rotor = [(x - ring) % 26 for x in rotor]
    rotor = rotor[ring:] + rotor[:ring]
    reverse_rotor = [0] * 26
    for i, item in enumerate(rotor):
      reverse_rotor[item] = i
    assert len(rotor) == 26
    assert len(set(rotor)) == 26
    assert len(reverse_rotor) == 26
    assert len(set(reverse_rotor)) == 26
    for x in range(26):
      assert x == rotor[reverse_rotor[x]], f"{rotor} {reverse} {x}"
    result.append([rotor, reverse_rotor, rotate, position])
  return result

def compile_plugboard(plugboard):
  result = {i: i for i in range(26)}
  for plug in plugboard.lower().split(" "):
    if plug:
      a, b = [encode[char] for char in plug]
      result[a] = b
      result[b] = a
  return result

def path(index, rotors, reflector, plugboard):
  index = plugboard[index]
  for rotor, _, _, position in reversed(rotors):
    index = (rotor[(index + position) % 26] - position) % 26
  index = reflector[index]
  for _, rotor, _, position in rotors:
    index = (rotor[(index + position) % 26] - position) % 26
  index = plugboard[index]
  return index

def rotate(rotors):
  to_rotate = set([len(rotors) - 1])
  for i, rotor in enumerate(rotors):
    _, _, rotate, position = rotor
    if i > 0 and position in rotate:
      to_rotate.add(i)
      to_rotate.add(i - 1)
  for i, rotor in enumerate(rotors):
    if i in to_rotate:
      rotor[-1] = (rotor[-1] + 1) % 26

def encrypt_enigma(plaintext, rotors, reflector, plugboard):
  plaintext = plaintext.lower()
  ciphertext = ""
  for letter in plaintext:
    if letter in string.ascii_lowercase:
      index = encode[letter]
      rotate(rotors)
      index = path(index, rotors, reflector, plugboard)
      assert index != encode[letter]
      ciphertext += decode(index)
    else: ciphertext += letter
  return ciphertext

def encode_enigma(test_data):
  plaintext = test_data["plaintext"]
  rotors = compile_rotors(test_data["rotors"])
  plugboard = compile_plugboard(test_data["plugboard"])
  reflector = reflectors[test_data["reflector"]]
  assert all([i != reflector[i] for i in range(26)])
  assert all([i == reflector[reflector[i]] for i in range(26)])
  if "key" in test_data:
    key = encrypt_enigma(test_data["key"], rotors, reflector, plugboard).lower()
    test_data["actual_key"] = key
    if "decrypt" in test_data and test_data["decrypt"]:
      actual_key = key
    else:
      actual_key = test_data["key"].lower()
    assert len(key) == len(rotors), "Invalid key length"
    for i, letter in enumerate(actual_key):
      rotors[i][-1] = encode[letter]
    return encrypt_enigma(plaintext, rotors, reflector, plugboard)
  else: return encrypt_enigma(plaintext, rotors, reflector, plugboard)

with open("rotor_map.json5") as file:
  rotor_data = pyjson5.load(file)
rotor_map = build_rotor_map(rotor_data)

with open("reflectors.json5") as file:
  reflectors = pyjson5.load(file)
reflectors = {key: [encode[char] for char in data.lower()] for key, data in reflectors.items()}

if __name__ == "__main__":
  import shutil
  import os
  from sys import argv
  if "test" in argv:
    for test in os.listdir("tests"):
      with open(f"tests/{test}") as file:
        test_data = pyjson5.load(file)
      ciphertext = encode_enigma(test_data)
      assert test_data["result"] == ciphertext, f"{test}: {ciphertext}"
      print(f"Passed test {test.split(".")[0]}")
  elif "new" in argv:
    filename = input("Enter file name: ")
    shutil.copy("tests/example.json5", f"messages/{filename}.json5")
  else:
    filename = input("Enter file name: ")
    with open(f"messages/{filename}.json5") as file:
      test_data = pyjson5.load(file)
    ciphertext = encode_enigma(test_data)
    print(ciphertext)
