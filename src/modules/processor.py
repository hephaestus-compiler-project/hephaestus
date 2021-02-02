# pylint: disable=too-few-public-methods
import sys
from copy import deepcopy

from src.generators.generator import Generator
from src.transformations.substitution import (
    ValueSubstitution, TypeSubstitution)
from src.transformations.type_creation import (
    SupertypeCreation, SubtypeCreation)
from src.transformations.parameterized import ParameterizedSubstitution
from src.transformations.type_erasure import TypeArgumentErasureSubstitution
from src.utils import random, read_lines, load_program
from src.modules.logging import Logger


class ProgramProcessor():

    TRANSFORMATIONS = {
        'SupertypeCreation': SupertypeCreation,
        'SubtypeCreation': SubtypeCreation,
        'ValueSubstitution': ValueSubstitution,
        'TypeSubstitution': TypeSubstitution,
        'ParameterizedSubstitution': ParameterizedSubstitution,
        'TypeArgumentErasureSubstitution': TypeArgumentErasureSubstitution
    }

    def __init__(self, proc_id, translator, args):
        self.proc_id = proc_id
        self.args = args
        self.transformations = [
            ProgramProcessor.TRANSFORMATIONS[t]
            for t in self.args.transformation_types
        ]
        self.transformation_schedule = self._get_transformation_schedule()
        self.current_transformation = 0

    def _apply_transformation(self, transformation_cls,
                              transformation_number, program):
        if self.args.log:
            logger = Logger(self.args.name, self.args.test_directory,
                            self.proc_id, transformation_cls.get_name(),
                            transformation_number)
        else:
            logger = None
        prev_p = deepcopy(program)
        transformer = transformation_cls(program, logger)
        if self.args.debug:
            print("Transformation " + str(transformation_number) + ": " +
                  transformer.get_name())
        transformer.transform()
        program = transformer.result()
        if not transformer.is_transformed:
            program = prev_p
        return program, transformer

    def _get_transformation_schedule(self):
        if self.args.transformations is not None:
            # Randomly generate a transformation schedule.
            return [
                random.choice(self.transformations)
                for i in range(self.args.transformations)
            ]
        # Get transformation schedule from file.
        lines = read_lines(self.args.transformation_schedule)
        schedule = []
        for line in lines:
            transformation = self.TRANSFORMATIONS.get(line)
            if transformation is None:
                sys.exit(
                    "Transformation " + line
                    + " found in schedule is not valid.")
            schedule.append(transformation)
        return schedule

    def get_program(self):
        if self.args.replay:
            if self.args.debug:
                print("\nLoading program: " + self.args.replay)
            # Load the program from the given file.
            return load_program(self.args.replay), True
        else:
            # Generate a new program.
            return self.generate_program()

    def get_transformations(self):
        return self.transformation_schedule[:self.current_transformation]

    def generate_program(self):
        if self.args.debug:
            print("\nGenerating program: " + str(self.proc_id))
        generator = Generator(
            max_depth=self.args.max_depth,
            disable_inference_in_closures=self.args.disable_inference_in_closures)
        program = generator.generate()
        return program, True

    def can_transform(self):
        return self.current_transformation < len(self.transformation_schedule)

    def transform_program(self, program):
        transformer_cls = (
            self.transformation_schedule[self.current_transformation])
        program, transformer = self._apply_transformation(
            transformer_cls, self.current_transformation + 1, program)
        self.current_transformation += 1
        return program, transformer.preserve_correctness()
