import enigma
from itertools import permutations
from string import ascii_lowercase
from time import perf_counter

def check_validity(occupancy, plugboard_a, plugboard_b):
  for plug in plugboard_a, plugboard_b:
    i, j = plug
    if occupancy[i] != -1 and occupancy[i] != j:
      return None
    if occupancy[j] != -1 and occupancy[j] != i:
      return None
    occupancy[i] = j
    occupancy[j] = i
  return occupancy

def solve_enigma(constraints):
  count = 0
  for a, b, c in permutations(enigma.rotor_map, 3):
    for x in ascii_lowercase:
      print(a, b, c, x)
      for y in ascii_lowercase:
        for z in ascii_lowercase:
          rotors = [
            [a, "a", x],
            [b, "a", y],
            [c, "a", z],
          ]
          rotors = enigma.compile_rotors(rotors)
          options = [[-1] * 26]
          for constraint in constraints:
            input, output = constraint
            enigma.rotate(rotors)
            new_options = []
            enigma_cache = [None] * 26
            for i in range(26):
              enigma_cache[i] = enigma.path(i, rotors, reflector, plugboard)
            for occupancy in options:
              for i in range(26):
                path = enigma_cache[i]
                plugboard_a = [input, i]
                plugboard_b = [output, path]
                new_occupancy = occupancy[:]
                new_occupancy = check_validity(new_occupancy, plugboard_a, plugboard_b)
                if new_occupancy is not None:
                  new_options.append(new_occupancy)
            option_count = len(new_options)
            count += option_count
            if option_count == 0:
              break
            elif option_count > 5000:
              print(f"Performance issues: {option_count}")
              print(a, b, c, x, y, z)
            options = new_options
          if option_count > 0:
            print(a, b, c, x, y, z)
            for occupancy in options:
              print("".join(enigma.decode(i) for i in occupancy))
            return
    print(count)
    return

crib = input("Crib: ")
ciphertext = input("Ciphertext: ")

constraints = []

reflector = enigma.reflectors[input("Reflector: ")]
plugboard = enigma.compile_plugboard("")

for crib, cipher in zip(crib.lower(), ciphertext.lower()):
  constraints.append((enigma.encode[crib], enigma.encode[cipher]))

start = perf_counter()

solve_enigma(constraints)

elapsed = perf_counter() - start
print(f"{elapsed:.2f}s")
