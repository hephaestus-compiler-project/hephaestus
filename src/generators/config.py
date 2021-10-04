"""
This file contains the classes that are responsible for configuring the
generation policies.
"""
import json
from dataclasses import dataclass


def process_arg(config, name, value):
    assert hasattr(config, name), \
        f"{type(config).__name__} has not {name} argument"
    if isinstance(getattr(config, name), (int, float)):
        assert isinstance(value, (int, float)), \
            f"{name}={value} is not int or float"
        setattr(config, name, value)
    else:
        for key, val in value.items():
            process_arg(getattr(config, name), key, val)


@dataclass
class ClassLimits:
    max_fields: int
    max_funcs: int


@dataclass
class FunctionLimits:
    max_side_effects: int
    max_params: int


@dataclass
class GenLimits:
    cls: ClassLimits
    fn: FunctionLimits
    max_var_decls: int  # max variable declarations in a scope.
    max_type_params: int # max type parameters in parameterized classes and functions
    max_functional_params: int # max number of parameters in functional interfaces
    max_top_level: int # max number of top-level declarations
    min_top_level: int # min number of top-level declarations
    max_depth: int # max depth of leaves in programs


@dataclass
class Probabilities:
    function_expr: float # functions that their body are expressions
    bounded_type_parameters: float


class GenConfig:
    def __init__(self, kwargs={}):
        # Default values
        self.limits = GenLimits(
            cls=ClassLimits(
                max_fields=2,
                max_funcs=2
            ),
            fn=FunctionLimits(
                max_side_effects=1,
                max_params=2
            ),
            max_var_decls=3,
            max_type_params=3,
            max_functional_params=3,
            max_top_level=10,
            min_top_level=5,
            max_depth=7
        )
        self.prob=Probabilities(
                function_expr=1.0,
                bounded_type_parameters=0.0
        )
        for key, value in kwargs.items():
            process_arg(self, key, value)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


def main():
    gen_config = GenConfig()
    __import__('pprint').pprint(gen_config.to_json())


if __name__ == "__main__":
    main()
