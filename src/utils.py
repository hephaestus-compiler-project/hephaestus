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


def random_string(length=5):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def safe_random_string(length=5, blacklist=[]):
    while True:
        r = random_string(length)
        if r not in blacklist:
            return r

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
        os.mkdir(directory_name)
    except Exception as e:
        print(e)
        sys.exit(0)
