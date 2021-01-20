import sys
import pickle
from src.examples.simple import program


with open("example.bin", "wb") as out:
    pickle.dump(program, out)
