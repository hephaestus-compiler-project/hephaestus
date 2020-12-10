import random
import string
import os
import sys



def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def read_lines(path):
    lines = []
    with open(path, 'r') as f:
        for line in f:
            lines.append(line.rstrip('\n'))
    return lines


def mkdir(directory_name):
    """Safe mkdir
    """
    try:
        os.makedirs(directory_name, exist_ok=True)
    except Exception as e:
        print(e)
        sys.exit(0)


class RandomUtils(object):

    resource_path = os.path.join(os.path.split(__file__)[0], "resources")

    WORD_POOL_LEN = 10000
    # Construct a random word pool of size 'WORD_POOL_LEN'.
    WORDS = set(random.sample(
        read_lines(os.path.join(resource_path, 'words')), WORD_POOL_LEN))
    INITIAL_WORDS = set(WORDS)

    def __init__(self, seed=None):
        self.r = random.Random(seed)

    def reset_word_pool(self):
        self.WORDS = set(self.INITIAL_WORDS)

    def bool(self):
        return self.r.choice([True, False])

    def word(self):
        # TODO: revisit regarding efficiency
        w = self.r.choice(tuple(self.WORDS))
        self.WORDS.remove(w)
        return w

    def integer(self, min_int=0, max_int=10):
        return self.r.randint(min_int, max_int)

    def char(self):
        return self.r.choice(string.ascii_letters + string.digits)

    def choice(self, choices):
        return self.r.choice(choices)

    def sample(self, choices):
        k = self.integer(0, len(choices))
        return self.r.sample(choices, k)

    def str(self, length=5):
        return ''.join(self.r.sample(
            string.ascii_letters + string.digits, length))

    def caps(self, length=1, blacklist=[]):
        while True:
            res = ''.join(self.r.sample(string.ascii_uppercase, length))
            if res not in blacklist:
                return res


random = RandomUtils()
