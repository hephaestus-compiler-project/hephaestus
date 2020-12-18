import sys
import pickle
from src.examples.parameterized import program


with open("example.bin", "wb") as out:
    pickle.dump(program, out)
