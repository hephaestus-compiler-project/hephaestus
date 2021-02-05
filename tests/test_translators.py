import re

from src.translators.groovy import GroovyTranslator
from tests.resources.translators.groovy import (program1, program2, program3,
    program4)


def translate(translator_cls, program):
    translator = translator_cls()
    translator.visit(program)
    return translator.result()


def read_expected(path):
    with open(path, 'r') as expf:
        return expf.read()

def test_groovy_cls():
    expected = "tests/resources/translators/groovy/program1.groovy"
    program = program1.program
    res = translate(GroovyTranslator, program)
    expected_res = read_expected(expected)
    res = re.sub('\s+', ' ', res)
    expected_res = re.sub('\s+', ' ', expected_res)
    assert res.strip() == expected_res.strip()


def test_groovy_global():
    expected = "tests/resources/translators/groovy/program2.groovy"
    program = program2.program
    res = translate(GroovyTranslator, program)
    expected_res = read_expected(expected)
    res = re.sub('\s+', ' ', res)
    expected_res = re.sub('\s+', ' ', expected_res)
    assert res.strip() == expected_res.strip()


def test_groovy_closures():
    expected = "tests/resources/translators/groovy/program3.groovy"
    program = program3.program
    res = translate(GroovyTranslator, program)
    expected_res = read_expected(expected)
    res = re.sub('\s+', ' ', res)
    expected_res = re.sub('\s+', ' ', expected_res)
    assert res.strip() == expected_res.strip()


def test_groovy_generics():
    expected = "tests/resources/translators/groovy/program4.groovy"
    program = program4.program
    res = translate(GroovyTranslator, program)
    print(res)
    expected_res = read_expected(expected)
    res = re.sub('\s+', ' ', res)
    expected_res = re.sub('\s+', ' ', expected_res)
    assert res.strip() == expected_res.strip()
