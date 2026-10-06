#!/usr/bin/env python3
"""Finite, corpus-free checks for the October research additions.

These compare optimized procedures with exhaustive sets, an independent algebraic
representation, hand-derived examples, or standard-library implementations. They
are not language-recovery experiments or security proofs. No external package or
private research input is required.
"""
import hashlib
import hmac
import itertools
import math
import random
import unittest
from collections import defaultdict


MASK = (1 << 32) - 1
SHA_INITIAL = tuple(int(x, 16) for x in (
    '6a09e667 bb67ae85 3c6ef372 a54ff53a 510e527f 9b05688c 1f83d9ab 5be0cd19'
).split())
SHA_CONSTANTS = tuple(int(x, 16) for x in (
    '428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 '
    'd807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7 c19bf174 '
    'e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da '
    '983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 '
    '27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85 '
    'a2bfe8a1 a81a664b c24b8b70 c76c51a3 d192e819 d6990624 f40e3585 106aa070 '
    '19a4c116 1e376c08 2748774c 34b0bcb5 391c0cb3 4ed8aa4a 5b9cca4f 682e6ff3 '
    '748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7 c67178f2'
).split())


def rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & MASK


def rolling_sha256(message):
    padded = message + b'\x80'
    padded += b'\0' * ((56 - len(padded)) % 64)
    padded += (8 * len(message)).to_bytes(8, 'big')
    state = list(SHA_INITIAL)
    for offset in range(0, len(padded), 64):
        words = [int.from_bytes(padded[offset+i:offset+i+4], 'big')
                 for i in range(0, 64, 4)]
        a, b, c, d, e, f, g, h = state
        for t in range(64):
            if t >= 16:
                x, y = words[(t-15) % 16], words[(t-2) % 16]
                words[t % 16] = (words[t % 16] + words[(t-7) % 16]
                                 + (rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3))
                                 + (rotr(y, 17) ^ rotr(y, 19) ^ (y >> 10))) & MASK
            u = (h + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25))
                 + ((e & f) ^ ((~e & MASK) & g)) + SHA_CONSTANTS[t] + words[t % 16]) & MASK
            v = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22))
                 + ((a & b) ^ (a & c) ^ (b & c))) & MASK
            a, b, c, d, e, f, g, h = (u+v) & MASK, a, b, c, (d+u) & MASK, e, f, g
        state = [(x+y) & MASK for x, y in zip(state, (a, b, c, d, e, f, g, h))]
    return b''.join(x.to_bytes(4, 'big') for x in state)


def cached_hmac(key):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()
    key = key.ljust(64, b'\0')
    inner = hashlib.sha256(bytes(x ^ 0x36 for x in key))
    outer = hashlib.sha256(bytes(x ^ 0x5c for x in key))

    def tag(message):
        a, b = inner.copy(), outer.copy()
        a.update(message)
        b.update(a.digest())
        return b.digest()
    return tag


def ghash_multiply(x, y):
    result = 0
    for i in range(128):
        if x & (1 << (127-i)):
            result ^= y
        y = (y >> 1) ^ (0xe1000000000000000000000000000000 if y & 1 else 0)
    return result


def polynomial_multiply(x, y):
    # Independently use ordinary low-bit polynomial coefficients and long division.
    reverse = lambda n: int(format(n, '0128b')[::-1], 2)
    x, y = reverse(x), reverse(y)
    result = 0
    while y:
        if y & 1:
            result ^= x
        x <<= 1
        y >>= 1
    modulus = (1 << 128) | (1 << 7) | (1 << 2) | (1 << 1) | 1
    while result.bit_length() > 128:
        result ^= modulus << (result.bit_length()-129)
    return reverse(result)


def zero_key_gcm_tag(aad, ciphertext):
    # Fixed, independently specified AES-128 block answers; no AES implementation.
    hash_key = int('66e94bd4ef8a2c3b884cfa59ca342b2e', 16)
    mask = int('58e2fccefa7e3061367f1d57a4e7455a', 16)
    blocks = (aad + b'\0' * (-len(aad) % 16)
              + ciphertext + b'\0' * (-len(ciphertext) % 16)
              + (8*len(aad)).to_bytes(8, 'big') + (8*len(ciphertext)).to_bytes(8, 'big'))
    value = 0
    for i in range(0, len(blocks), 16):
        value = ghash_multiply(value ^ int.from_bytes(blocks[i:i+16], 'big'), hash_key)
    return (value ^ mask).to_bytes(16, 'big')


def amsco_columns(n, width, start):
    columns = [[] for _ in range(width)]
    at = cell = 0
    while at < n:
        row, col = divmod(cell, width)
        size = min(n-at, 1 + ((row+col+start) % 2))
        columns[col].extend(range(at, at+size))
        at += size
        cell += 1
    return columns


def field_add(x, y):
    return sum(((x//3**i + y//3**i) % 3) * 3**i for i in range(3))


def field_product(x, y):
    coefficients = [0] * 5
    for i, j in itertools.product(range(3), repeat=2):
        coefficients[i+j] += (x//3**i % 3) * (y//3**j % 3)
    for degree in (4, 3):
        value = coefficients[degree] % 3
        coefficients[degree-3] -= value
        coefficients[degree-2] -= 2*value
    return sum((coefficients[i] % 3) * 3**i for i in range(3))


def bilinear_minimum(cipher, lag, parameters, q, cost):
    a, b, d, e = parameters
    roots = [[[] for _ in range(q)] for _ in range(q)]
    for coefficient, x in itertools.product(range(q), repeat=2):
        roots[coefficient][coefficient*x % q].append(x)
    total = 0
    for phase in range(lag):
        previous = [0] * q
        for i in range(phase, len(cipher), lag):
            following = [math.inf] * q
            for y in range(q):
                for x in roots[(a*y+b) % q][(cipher[i]-d*y-e) % q]:
                    following[x] = min(following[x], previous[y] + cost[i][x])
            previous = following
        total += min(previous)
    return total


def logsum(values):
    values = list(values)
    peak = max(values)
    return peak if peak == -math.inf else peak + math.log(sum(math.exp(v-peak) for v in values))


def key_evidence(cipher, period, initial, transition):
    q = len(initial)
    factors = [[[0.0]*q for _ in range(q)] for _ in range(period)]
    log_probability = lambda v: math.log(v) if v else -math.inf
    for i in range(len(cipher)-1):
        for a, b in itertools.product(range(q), repeat=2):
            factors[i % period][a][b] += log_probability(
                transition[(cipher[i]+a) % q][(cipher[i+1]+b) % q])
    for a, b in itertools.product(range(q), repeat=2):
        factors[0][a][b] += log_probability(initial[(cipher[0]+a) % q])
    mass = [[0 if a == b else -math.inf for b in range(q)] for a in range(q)]
    for factor in factors:
        mass = [[logsum(mass[start][mid]+factor[mid][end] for mid in range(q))
                 for end in range(q)] for start in range(q)]
    return logsum(mass[a][a] for a in range(q)) - period*math.log(q)


def has_matching(domains):
    owners = {}

    def augment(vertex, seen):
        for cell in domains[vertex]:
            if cell in seen:
                continue
            seen.add(cell)
            if cell not in owners or augment(owners[cell], seen):
                owners[cell] = vertex
                return True
        return False
    return all(augment(v, set()) for v in range(len(domains)))


def nonce_audit(records, complete=True):
    groups = defaultdict(list)
    gaps = set()
    for operation, key, nonce in records:
        if not operation:
            gaps.add('missing-operation')
        else:
            groups[operation].append((key, nonce))
    admitted = defaultdict(set)
    for operation, descriptions in sorted(groups.items()):
        if any(not key or not isinstance(nonce, bytes) or len(nonce) != 12
               for key, nonce in descriptions) or len(set(descriptions)) != 1:
            gaps.add(operation)
        else:
            admitted[descriptions[0]].add(operation)
    findings = {tuple(sorted(ops)) for ops in admitted.values() if len(ops) > 1}
    coverage = complete and not gaps
    verdict = 'REUSE' if findings else 'CLEAN' if coverage else 'INSUFFICIENT'
    return verdict, bool(coverage), findings, gaps


class ResearchAdditionChecks(unittest.TestCase):
    def test_sha256_rolling_schedule_against_hashlib(self):
        lengths = (0, 1, 2, 3, 7, 8, 15, 16, 31, 32, 55, 56, 57, 63, 64,
                   65, 119, 120, 121, 127, 128, 129, 255, 256, 257, 4095, 4096, 4097)
        for size in lengths:
            for message in (bytes(size), b'\xff'*size, bytes(i % 256 for i in range(size))):
                self.assertEqual(rolling_sha256(message), hashlib.sha256(message).digest())
        self.assertEqual(rolling_sha256(b'abc').hex(),
                         'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    def test_cached_hmac_against_standard_library_and_vector(self):
        messages = (b'', b'a\x00\xff', b'Hi There', b'Hi There\n', bytes(range(256)))
        for size in (0, 1, 20, 32, 63, 64, 65, 131):
            key = bytes(i % 256 for i in range(size))
            tag = cached_hmac(key)
            for message in messages + messages[::-1]:
                self.assertEqual(tag(message), hmac.digest(key, message, 'sha256'))
        self.assertEqual(cached_hmac(b'\x0b'*20)(b'Hi There').hex(),
                         'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7')

    def test_ghash_against_polynomial_reduction_and_gcm_vectors(self):
        rng = random.Random(260610)
        for _ in range(96):
            x, y = rng.getrandbits(128), rng.getrandbits(128)
            self.assertEqual(ghash_multiply(x, y), polynomial_multiply(x, y))
        self.assertEqual(zero_key_gcm_tag(b'', b'').hex(), '58e2fccefa7e3061367f1d57a4e7455a')
        ciphertext = bytes.fromhex('0388dace60b6a392f328c2b971b2fe78')
        expected = bytes.fromhex('ab6e47d42cec13bdf53a67b21257bddf')
        self.assertEqual(zero_key_gcm_tag(b'', ciphertext), expected)
        # No plaintext-producing callback runs when authentication fails.
        calls = []
        def open_fixture(aad, c, tag):
            if len(tag) != 16 or not hmac.compare_digest(zero_key_gcm_tag(aad, c), tag):
                return None
            calls.append('decrypt')
            return bytes(a ^ b for a, b in zip(c, ciphertext))
        for i in range(len(ciphertext)):
            changed = bytearray(ciphertext)
            changed[i] ^= 1
            self.assertIsNone(open_fixture(b'', bytes(changed), expected))
        for aad, tag in ((b'a', expected), (b'', expected[:-1]), (b'', bytes(16))):
            self.assertIsNone(open_fixture(aad, ciphertext, tag))
        self.assertEqual(calls, [])
        self.assertEqual(open_fixture(b'', ciphertext, expected), bytes(16))

    def test_amsco_geometry_and_even_width_example(self):
        columns = amsco_columns(13, 4, 0)
        plain = 'ABCDEFGHIJKLM'
        self.assertEqual([''.join(plain[i] for i in col) for col in columns],
                         ['AGHM', 'BCI', 'DJK', 'EFL'])
        self.assertEqual(''.join(plain[i] for col in (2, 0, 3, 1) for i in columns[col]),
                         'DJKAGHMEFLBCI')
        for width in range(1, 7):
            for size, start in itertools.product(range(41), range(2)):
                columns = amsco_columns(size, width, start)
                self.assertEqual(sorted(itertools.chain.from_iterable(columns)), list(range(size)))
                for order in (list(range(width)), list(reversed(range(width)))):
                    route = [x for col in order for x in columns[col]]
                    decoded = [None]*size
                    for at, value in zip(route, route):
                        decoded[at] = value
                    self.assertEqual(decoded, list(range(size)))

    def test_swagman_latin_routes_and_hand_rectangle(self):
        square = ((0, 1, 2), (1, 2, 0), (2, 0, 1))
        def encrypt(plain, key):
            h, width = len(key), len(plain)//len(key)
            out = [None]*len(plain)
            for row, col in itertools.product(range(h), range(width)):
                out[col*h+key[row][col % h]] = plain[row*width+col]
            return out
        self.assertEqual(''.join(encrypt('ABCDEFGHIJKL', square)), 'AEIJBFGKCDHL')
        permutations = list(itertools.permutations(range(3)))
        count = 0
        for key in itertools.product(permutations, repeat=3):
            if any(len(set(column)) != 3 for column in zip(*key)):
                continue
            count += 1
            for width in range(1, 8):
                route = encrypt(list(range(3*width)), key)
                self.assertEqual(sorted(route), list(range(3*width)))
                inverse = [[column.index(r) for r in range(3)] for column in zip(*key)]
                decoded = [None]*(3*width)
                for col, row in itertools.product(range(width), range(3)):
                    decoded[inverse[col % 3][row]*width+col] = route[col*3+row]
                self.assertEqual(decoded, list(range(3*width)))
        self.assertEqual(count, 12)

    def test_gf27_field_and_logarithm_identities(self):
        irreducible = [c for c in itertools.product(range(3), repeat=3)
                       if all((t**3 + c[2]*t*t + c[1]*t + c[0]) % 3 for t in range(3))]
        self.assertEqual(len(irreducible), 8)
        self.assertIn((1, 2, 0), irreducible)
        product = [[field_product(a, b) for b in range(27)] for a in range(27)]
        self.assertEqual(product[3][9], 5)
        self.assertEqual(field_add(2, 1), 0)
        for a in range(1, 27):
            self.assertEqual(sum(product[a][b] == 1 for b in range(1, 27)), 1)
        for a, b, c in itertools.product(range(27), repeat=3):
            self.assertEqual(product[product[a][b]][c], product[a][product[b][c]])
            self.assertEqual(product[a][field_add(b, c)], field_add(product[a][b], product[a][c]))
        for generator in range(1, 27):
            powers = [1]
            for _ in range(25):
                powers.append(product[powers[-1]][generator])
            if len(set(powers)) == 26:
                break
        self.assertEqual(set(powers), set(range(1, 27)))
        for a, b in itertools.product(range(26), repeat=2):
            self.assertEqual(product[powers[a]][powers[b]], powers[(a+b) % 26])

    def test_bilinear_minimum_against_complete_assignments(self):
        for q in (2, 3):
            n = 3
            cost = [[(i+1)*x*x-x for x in range(q)] for i in range(n)]
            for parameters in itertools.product(range(q), repeat=4):
                a, b, d, e = parameters
                for lag in (1, 2):
                    direct = defaultdict(lambda: math.inf)
                    for digits in itertools.product(range(q), repeat=n+lag):
                        primer, plain = digits[:lag], digits[lag:]
                        previous = primer + plain
                        cipher = tuple((a*x*previous[i]+b*x+d*previous[i]+e) % q
                                       for i, x in enumerate(plain))
                        value = sum(cost[i][x] for i, x in enumerate(plain))
                        direct[cipher] = min(direct[cipher], value)
                    for cipher in itertools.product(range(q), repeat=n):
                        self.assertEqual(bilinear_minimum(cipher, lag, parameters, q, cost), direct[cipher])
        self.assertEqual([x for x in range(26) if 13*x % 26 == 13], list(range(1, 26, 2)))
        self.assertEqual([x for x in range(26) if 13*x % 26 == 2], [])

    def test_bilinear_affine_coordinate_identity(self):
        rng = random.Random(26)
        for q in (6, 26):
            for _ in range(100):
                a, b, d, e, v = [rng.randrange(q) for _ in range(5)]
                u = rng.choice([x for x in range(q) if math.gcd(x, q) == 1])
                inv = pow(u, -1, q)
                A = a*inv*inv % q
                B, D = (b*inv-A*v) % q, (d*inv-A*v) % q
                E = (e-(b+d)*v*inv+A*v*v) % q
                for x, y in itertools.product(range(q), repeat=2):
                    X, Y = (u*x+v) % q, (u*y+v) % q
                    self.assertEqual((a*x*y+b*x+d*y+e) % q, (A*X*Y+B*X+D*Y+E) % q)

    def test_periodic_evidence_against_complete_keys(self):
        for q in (2, 3):
            initial = [(x+1)/(q*(q+1)/2) for x in range(q)]
            transition = [[((a+b) % q+1)/(q*(q+1)/2) for b in range(q)] for a in range(q)]
            for size in range(1, 5):
                for cipher in itertools.product(range(q), repeat=size):
                    for period in range(1, 5):
                        likelihoods = []
                        for key in itertools.product(range(q), repeat=period):
                            plain = [(c+key[i % period]) % q for i, c in enumerate(cipher)]
                            likelihoods.append(initial[plain[0]] * math.prod(
                                transition[a][b] for a, b in zip(plain, plain[1:])))
                        expected = math.log(sum(likelihoods)/q**period)
                        self.assertAlmostEqual(key_evidence(cipher, period, initial, transition), expected, places=12)
                    self.assertAlmostEqual(key_evidence(cipher, size, initial, transition), -size*math.log(q), places=12)
        # Impossible factors must stay -infinity without NaN.
        self.assertEqual(key_evidence((0, 1), 1, [1, 0], [[1, 0], [0, 1]]), -math.inf)

    def test_two_period_gauge_and_conditional_sum(self):
        q = 2
        for a, b in itertools.product(range(1, 5), repeat=2):
            g = math.gcd(a, b)
            n = math.lcm(a, b)
            weights = [[0.2+((i+2*x) % 4)/10 for x in range(q)] for i in range(n)]
            full = defaultdict(list)
            for A in itertools.product(range(q), repeat=a):
                for B in itertools.product(range(q), repeat=b):
                    key = tuple((A[i % a]+B[i % b]) % q for i in range(n))
                    full[key].append((A, B))
            self.assertEqual(len(full), q**(a+b-g))
            self.assertEqual({len(v) for v in full.values()}, {q**g})
            direct = sum(math.prod(weights[i][k] for i, k in enumerate(key)) for key in full)/len(full)
            total = 0
            # Fix one A coordinate per residue class; condition on its remaining coordinates.
            for free in itertools.product(range(q), repeat=a-g):
                A = (0,)*g + free
                partial = 1
                for j in range(b):
                    partial *= sum(math.prod(weights[i][(A[i % a]+v) % q]
                                             for i in range(j, n, b)) for v in range(q))
                total += partial
            self.assertAlmostEqual(total/q**(a+b-g), direct, places=12)

    def test_ternary_hall_formula_against_matching(self):
        cells = list(itertools.product(range(3), repeat=3))
        diagonal = [i for i, c in enumerate(cells) if c[0] == c[1] == c[2]]
        planes = [[i for i, c in enumerate(cells) if c[a] == c[b]] for a, b in ((0, 1), (0, 2), (1, 2))]
        for diagonal_count in range(5):
            for counts in itertools.product(range(11), repeat=3):
                domains = [diagonal]*diagonal_count
                for count, plane in zip(counts, planes):
                    domains += [plane]*count
                restricted = diagonal_count + sum(max(0, c-6) for c in counts) <= 3
                expected = len(domains) <= 27 and restricted
                self.assertEqual(has_matching(domains), expected)
                if expected:
                    self.assertTrue(has_matching(domains + [list(range(27))]*(27-len(domains))))
                    self.assertFalse(has_matching(domains + [list(range(27))]*(28-len(domains))))

    def test_nonce_audit_deduplication_conflicts_and_order(self):
        nonce = bytes.fromhex('000000000000000000000007')
        records = [('alpha', 'key-A', nonce), ('alpha', 'key-A', nonce),
                   ('beta', 'key-A', nonce), ('gamma', 'key-B', nonce)]
        expected = ('REUSE', True, {('alpha', 'beta')}, set())
        for order in itertools.permutations(records):
            self.assertEqual(nonce_audit(order), expected)
        self.assertEqual(nonce_audit(records + [('alpha', 'key-A', bytes(12))]),
                         ('INSUFFICIENT', False, set(), {'alpha'}))
        for extra in ((None, 'key-A', nonce), ('bad', None, nonce), ('bad', 'key-A', b'short')):
            result = nonce_audit(records + [extra])
            self.assertEqual(result[:3], ('REUSE', False, {('alpha', 'beta')}))
        self.assertEqual(nonce_audit(records[:2] + [records[-1]])[:2], ('CLEAN', True))
        self.assertEqual(nonce_audit([], complete=False)[:2], ('INSUFFICIENT', False))

    def test_slidefair_complete_pair_tables(self):
        for rule in ('vigenere', 'variant', 'beaufort'):
            for key in range(26):
                bottom = [((j+key) if rule == 'vigenere' else (j-key) if rule == 'variant'
                           else (key-j)) % 26 for j in range(26)]
                inverse = [bottom.index(x) for x in range(26)]
                def transform(a, b, direction):
                    column = inverse[b]
                    if a == column:
                        j = (a+direction) % 26
                        return j, bottom[j]
                    return column, bottom[a]
                outputs = set()
                for a, b in itertools.product(range(26), repeat=2):
                    encrypted = transform(a, b, 1)
                    outputs.add(encrypted)
                    self.assertEqual(transform(*encrypted, -1), (a, b))
                self.assertEqual(len(outputs), 26**2)

    def test_nonunit_memory_feedback_roundtrip(self):
        plain = [0, 1, 25, 13, 5, 8, 9, 2, 17]
        for lag, u, alpha, beta in itertools.product((1, 3), (1, 25), range(26), (0, 2, 13, 25)):
            primer = [i+7 for i in range(lag)]
            cipher = []
            for i, x in enumerate(plain):
                memory = primer[i] if i < lag else alpha*plain[i-lag]+beta*cipher[i-lag]+4
                cipher.append((u*x+memory) % 26)
            recovered = []
            for i, c in enumerate(cipher):
                memory = primer[i] if i < lag else alpha*recovered[i-lag]+beta*cipher[i-lag]+4
                recovered.append(pow(u, -1, 26)*(c-memory) % 26)
            self.assertEqual(recovered, plain)

    def test_coordinate_convention_gauge_orbits(self):
        permutations = list(itertools.permutations(range(3)))
        classes = defaultdict(int)
        for axes in permutations:
            for maps in itertools.product(permutations, repeat=3):
                inverse = [maps[0].index(v) for v in range(3)]
                normalized = tuple(tuple(inverse[v] for v in m) for m in maps)
                self.assertEqual(normalized[0], (0, 1, 2))
                classes[axes, normalized] += 1
                # Applying any common digit relabeling preserves the representative.
                for relabel in permutations:
                    moved = tuple(tuple(relabel[v] for v in m) for m in maps)
                    undo = [moved[0].index(v) for v in range(3)]
                    self.assertEqual(tuple(tuple(undo[v] for v in m) for m in moved), normalized)
        self.assertEqual(len(classes), 216)
        self.assertEqual(set(classes.values()), {6})


if __name__ == '__main__':
    unittest.main(verbosity=2)
