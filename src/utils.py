from collections import defaultdict
import random
import string
import pickle
import os
import sys


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs)
        return cls._instances[cls]


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


def path2set(path):
    if os.path.isfile(path):
        with open(path, 'r') as f:
            return {
                line.strip()
                for line in f.readlines()
            }
    else:
        return set()


def get_reserved_words(resource_path, language):
    filename = "{}_keywords".format(language)
    path = os.path.join(resource_path, filename)
    return path2set(path)


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
        word = self.r.choice(tuple(self.WORDS))
        self.WORDS.remove(word)
        return word

    def remove_reserved_words(self, language):
        reserved_words = get_reserved_words(self.resource_path, language)
        self.INITIAL_WORDS = self.INITIAL_WORDS - reserved_words
        self.WORDS = self.WORDS - reserved_words

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

    def range(self, from_value, to_value):
        return range(0, self.integer(from_value, to_value))

    def identifier(self, ident_type:str=None) -> str:
        """Generate an identifier name.

        Args:
            ident_type: None or 'capitalize' or 'lower'

        Raises:
            AssertionError: Raises an AssertionError if the ident_type is neither
                'capitalize' nor 'lower'.
        """
        word = self.word()
        if ident_type is None:
            return word
        if ident_type == 'lower':
            return word.lower()
        if ident_type == 'capitalize':
            return word.capitalize()
        raise AssertionError("ident_type should be 'capitalize' or 'lower'")

    def shuffle(self, ll):
        return self.r.shuffle(ll)


random = RandomUtils()


class IdGen():
    def __init__(self):
        self._cache = defaultdict(lambda: 1)

    def get_node_id(self, node_id):
        if node_id not in self._cache:
            self._cache[node_id]
            return node_id, None
        else:
            value = self._cache[node_id]
            self._cache[node_id] += 1
            return node_id, str(value)
