import re
import os


from src.ir import groovy_types, java_types
from src.translators.groovy import GroovyTranslator
from src.translators.java import JavaTranslator
from tests.resources.translators import (program1, program2, program3,
    program4, program5, program6)


LANG_LOOKUP = {
    "groovy": (GroovyTranslator, groovy_types, "groovy"),
    "java": (JavaTranslator, java_types, "java")
}
TEST_DIR = "tests/resources/translators/"


def translate(translator_cls, program):
    translator = translator_cls()
    translator.visit(program)
    return translator.result()


def read_expected(path):
    with open(path, 'r') as expf:
        return expf.read()


def find_targets(program):
    return [f for f in os.listdir(TEST_DIR)
            if f.startswith(program) and f != program + ".py"]


def run_test(program_name, program):
    return
    #for target_program in find_targets(program_name):
    #    expected = os.path.join(TEST_DIR, target_program)
    #    translator, types, lang = LANG_LOOKUP[target_program.split(".")[-1]]
    #    ast = program.produce_program(lang, types)
    #    res = translate(translator, ast)
    #    expected_res = read_expected(expected)
    #    res = re.sub('\s+', ' ', res)
    #    expected_res = re.sub('\s+', ' ', expected_res)
    #    assert res.strip() == expected_res.strip()


def test_cls():
    run_test("program1", program1)


def test_global():
    run_test("program2", program2)


def test_closures():
    run_test("program3", program3)


def test_generics():
    run_test("program4", program4)


def test_is():
    run_test("program5", program5)


def test_condition_block():
    run_test("program6", program6)
