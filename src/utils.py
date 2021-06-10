import random
import string
import pickle
import os
import sys


def prefix_lst(prefix, lst):
    return any(prefix == lst[:i]
               for i in range(1, len(prefix) + 1))


def is_number(string_var):
    try:
        float(string_var)
        return True
    except ValueError:
        return False


def lst_get(lst, index=0, default=None):
    """Safely get an element from a list"""
    try:
        return lst[index]
    except IndexError:
        return default


def leading_spaces(input_string):
    """Count leading spaces of a string"""
    return len(input_string) - len(input_string.lstrip(' '))


def add_string_at(input_string, substring, pos):
    """Add a substring to the given position of the string"""
    return input_string[:pos] + substring + input_string[pos:]


def read_lines(path):
    lines = []
    with open(path, 'r') as infile:
        for line in infile:
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


def fprint(text):
    """Full screen print"""
    try:
        terminal_width = os.get_terminal_size().columns
        print(text.center(int(terminal_width), "="))
    except OSError:  # This error may occur when run under cron
        print(text)


def translate_program(translator, program):
    translator.visit(program)
    return translator.result()


def load_program(path):
    with open(path, 'rb') as initial_bin:
        return pickle.load(initial_bin)


def dump_program(path, program):
    with open(path, 'wb') as out:
        pickle.dump(program, out)


def save_text(path, text):
    with open(path, 'w') as out:
        out.write(text)


class RandomUtils():

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

    def bool(self, prob=0.5):
        return self.r.random() < prob

    def word(self):
        # TODO: revisit regarding efficiency
        word = self.r.choice(tuple(self.WORDS))
        self.WORDS.remove(word)
        return word

    def integer(self, min_int=0, max_int=10):
        return self.r.randint(min_int, max_int)

    def char(self):
        return self.r.choice(string.ascii_letters + string.digits)

    def choice(self, choices):
        return self.r.choice(choices)

    def sample(self, choices, k=None):
        k = k or self.integer(0, len(choices))
        return self.r.sample(choices, k)

    def str(self, length=5):
        return ''.join(self.r.sample(
            string.ascii_letters + string.digits, length))

    def caps(self, length=1, blacklist=None):
        blacklist = blacklist if blacklist is not None else []
        while True:
            res = ''.join(self.r.sample(string.ascii_uppercase, length))
            if res not in blacklist:
                return res


random = RandomUtils()
