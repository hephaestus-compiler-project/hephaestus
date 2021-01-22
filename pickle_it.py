import sys
import pickle
from src.examples.type_args_erasure import program


with open("example.bin", "wb") as out:
    pickle.dump(program, out)
