import string

class SubstitutionCipher(object):
    def __init__(self, cipher):
        self.cipher = cipher
        self.alphabet = string.ascii_lowercase

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.cipher)

    def __str__(self):
        return 'IN:  {}\nOUT: {}'.format(self.alphabet, self.cipher)

    @staticmethod
    def __translate(msg, alph_in, alph_out):
        assert len(alph_in) == len(alph_out)
        assert len(msg) == 1

        pos = alph_in.index(msg)
        return alph_out[pos]

    def encode(self, plaintext):
        return self.__translate(plaintext,
                                self.alphabet,
                                self.cipher)

    def decode(self, ciphertext):
        return self.__translate(ciphertext,
                                self.cipher,
                                self.alphabet)


class Plugboard(SubstitutionCipher):
    def __init__(self, wiring):
        """
        wiring diagram example: "at bf jp"
          -> substitute positions of a and t, b and f, j and p.
        """
        alphabet = list(string.ascii_lowercase)
        seen = set()
        for pair in wiring.split():
            l1, l2 = pair
            if l1 in seen or l2 in seen or l1 == l2:
                raise ValueError('No repeated letters allowed in wiring')
            else:
                seen.update((l1, l2))
            p1 = alphabet.index(l1)
            p2 = alphabet.index(l2)
            alphabet[p1], alphabet[p2] = l2, l1

        super(Plugboard, self).__init__(''.join(alphabet))


class Rotor(SubstitutionCipher):
    def __init__(self, cipher, ring_setting, turnover):
        self.rotation = 0
        self.turnover = set(turnover)
        super(Rotor, self).__init__(cipher)
        self.apply_ring_setting(ring_setting)

    def apply_ring_setting(self, ring_setting):
        ring_setting = 26 - (ring_setting % 26)
        for _ in range(ring_setting):
            self.rotate()
        self.rotation = 0

    def rotate(self):
        rotated_cipher = self.cipher[1:] + self.cipher[0:1]
        shifted_cipher = []
        for letter in rotated_cipher:
            pos = (self.alphabet.index(letter) - 1) % 26
            shifted_cipher.append(self.alphabet[pos])
        self.rotation = (self.rotation + 1) % 26
        self.cipher = ''.join(shifted_cipher)

    def get_position(self):
        return self.alphabet[self.rotation]

    def set_position(self, letter):
        if not letter in self.alphabet:
            raise ValueError('{} is not in the rotor\'s alphabet'
                             .format(letter))
        while self.get_position() != letter:
            self.rotate()

    def trigger_rotation(self):
        return self.get_position() in self.turnover


class Reflector(SubstitutionCipher):
    def __init__(self, cipher):
        super(Reflector, self).__init__(cipher)
        for letter in self.alphabet:
            if not self.encode(letter) == self.decode(letter):
                raise ValueError('Invalid cipher for Reflector - must be symmetric')


class Enigma(object):
    def __init__(self, reflector, rotors, plugboard):
        self.reflector = reflector
        self.rotors = rotors
        self.plugboard = plugboard

    def get_position(self):
        return ''.join(rotor.get_position() for rotor in self.rotors)

    def set_position(self, letters):
        for (rotor, letter) in zip(self.rotors, letters):
            rotor.set_position(letter)

    def rotate(self):
        rotate1 = enigma_rotors[1].trigger_rotation()
        rotate2 = enigma_rotors[2].trigger_rotation() or rotate1

        if rotate1:
            enigma_rotors[0].rotate()
        if rotate2:
            enigma_rotors[1].rotate()
        enigma_rotors[2].rotate()

    def encode_decode(self, letter):
        # Real enigma machines rotate the rotors before encoding anything
        self.rotate()

        letter = self.plugboard.encode(letter)
        for rotor in reversed(self.rotors):
            letter = rotor.encode(letter)
        letter = self.reflector.encode(letter)
        for rotor in self.rotors:
            letter = rotor.decode(letter)
        letter = self.plugboard.decode(letter)
        return letter

    def process_message(self, message):
        output = []
        for letter in message:
            if not letter in string.ascii_lowercase:
                letter = 'x'
            output.append(self.encode_decode(letter))
        return ''.join(output)


ri =          Rotor('ekmflgdqvzntowyhxuspaibrcj', 0, 'q')
rii =         Rotor('ajdksiruxblhwtmcqgznpyfvoe', 0, 'e')
riii =        Rotor('bdfhjlcprtxvznyeiwgakmusqo', 0, 'v')
riv =         Rotor('esovpzjayquirhxlnftgkdcmwb', 0, 'j')
rv =          Rotor('vzbrgityupsdnhlxawmjqofeck', 0, 'z')
rvi =         Rotor('jpgvoumfyqbenhzrdkasxlictw', 0, 'zm')
rvii =        Rotor('nzjhgrcxmyswboufaivlpekqdt', 0, 'zm')
rviii =       Rotor('fkqhtlxocbjspdzramewniuygv', 0, 'zm')
b_reflector = Reflector("yruhqsldpxngokmiebfzcwvjat")
bthin_reflector = \
              Reflector("enkqauywjicopblmdxzvfthrgs")
c_reflector = Reflector("fvpjiaoyedrzxwgctkuqsbnmhl")
cthin_reflector = \
              Reflector("rdobjntkvehmlfcwzaxgyipsuq")


if __name__ == '__main__':
    enigma_rotors = [ri, riv, rii]
    enigma_rotors[1].apply_ring_setting(15)
    enigma_plugboard = Plugboard('am pw bz fo')
    enigma_reflector = b_reflector
    enigma = Enigma(enigma_reflector, enigma_rotors, enigma_plugboard)
    enigma.set_position('bbb')
    plaintext = "ixthinkxenigmaxmachinesxmightxbexaxlittlexoutxofxdate"
    ciphertext = enigma.process_message(plaintext)
    print("Enigma settings:")
    print("  Rotors (left to right): I, IV, II")
    print("  Rotor settings: 1 16 1")
    print("  Rotor positions: b b b")
    print("  Reflector: B")
    print("  Plugboard: am pw bz fo")
    print()
    print("Plaintext:\n  {}\n".format(plaintext))
    print("Ciphertext:\n  {}\n".format(ciphertext))

