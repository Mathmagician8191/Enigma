use std::collections::{HashMap, HashSet};

pub(crate) const fn decode(number: u8) -> char {
  (number + b'a') as char
}

pub(crate) const fn encode(letter: char) -> u8 {
  letter as u8 - b'a'
}

pub(crate) type RotorMap = HashMap<String, ([u8; 26], Vec<u8>)>;

pub(crate) fn build_rotor_map() -> RotorMap {
  let data = std::fs::read_to_string("../rotor_map.json5").expect("Could not open file");
  let raw_rotor_map: HashMap<String, (&str, &str)> =
    json5::from_str(&data).expect("JSON data invalid");
  let mut rotor_map = HashMap::new();
  for (key, data) in raw_rotor_map {
    let (rotor, rotate_positions) = data;
    let rotor: [u8; 26] = rotor
      .to_ascii_lowercase()
      .chars()
      .map(encode)
      .collect::<Vec<u8>>()
      .try_into()
      .expect("Invalid rotor data");
    let rotate_positions = rotate_positions.chars().map(encode).collect();
    rotor_map.insert(key, (rotor, rotate_positions));
  }
  rotor_map
}

type CompiledRotor = Vec<([u8; 26], [u8; 26], Vec<u8>, u8)>;

pub(crate) fn compile_rotors(rotor_map: &RotorMap, rotors: &[(String, u8, u8)]) -> CompiledRotor {
  let mut result = Vec::new();
  for (rotor, ring, position) in rotors {
    let (rotor, rotate) = rotor_map[rotor].clone();
    let mut rotor = rotor.map(|x| (x + ring) % 26);
    rotor.rotate_right(usize::from(*ring));
    let mut reverse_rotor = [0; 26];
    for (i, item) in rotor.iter().enumerate() {
      reverse_rotor[usize::from(*item)] = i as u8;
    }
    assert_eq!(rotor.len(), 26);
    assert_eq!(reverse_rotor.len(), 26);
    for x in 0..26 {
      assert_eq!(x, usize::from(rotor[usize::from(reverse_rotor[x])]));
    }
    result.push((rotor, reverse_rotor, rotate, *position));
  }
  result
}

pub(crate) fn path(mut index: u8, rotors: &CompiledRotor, reflector: [u8; 26]) -> u8 {
  for (rotor, _, _, position) in rotors.iter().rev() {
    index = (rotor[usize::from(index + position) % 26] + 26 - position) % 26;
  }
  index = reflector[usize::from(index)];
  for (_, rotor, _, position) in rotors {
    index = (rotor[usize::from(index + position) % 26] + 26 - position) % 26;
  }
  index
}

pub(crate) fn rotate(rotors: &mut CompiledRotor) {
  let mut to_rotate = HashSet::new();
  to_rotate.insert(rotors.len() - 1);
  for (i, rotor) in rotors.iter().enumerate() {
    let (_, _, rotate, position) = rotor;
    if i > 0 && rotate.contains(position) {
      to_rotate.insert(i);
      to_rotate.insert(i - 1);
    }
  }
  for (i, rotor) in rotors.iter_mut().enumerate() {
    if to_rotate.contains(&i) {
      rotor.3 = (rotor.3 + 1) % 26;
    }
  }
}

pub(crate) fn reflectors(expected_reflector: &str) -> Option<[u8; 26]> {
  let data = std::fs::read_to_string("../reflectors.json5").expect("Could not open file");
  let reflectors: HashMap<&str, &str> = json5::from_str(&data).expect("JSON data invalid");
  for (reflector, data) in reflectors {
    if reflector == expected_reflector {
      let mut results = [None; 26];
      for (i, char) in data.to_ascii_lowercase().chars().enumerate() {
        let value = encode(char);
        assert_eq!(results[i], None);
        results[i] = Some(value);
      }
      return Some(results.map(|x| x.expect("Missing reflector data")));
    }
  }
  None
}
