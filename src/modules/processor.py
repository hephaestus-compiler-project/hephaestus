# pylint: disable=too-few-public-methods
import sys

from src.generators.generator import Generator
from src.transformations.type_erasure import TypeErasure
from src.transformations.type_overwriting import TypeOverwriting
from src.utils import random, read_lines, load_program
from src.modules.logging import Logger


class ProgramProcessor():

    # Correctness-preserving transformations
    CP_TRANSFORMATIONS = {
        'TypeErasure': TypeErasure,
    }

    # Non correctness-preserving transformations
    NCP_TRANSFORMATIONS = {
        'TypeOverwriting': TypeOverwriting,
    }

    def __init__(self, proc_id, args):
        self.proc_id = proc_id
        self.args = args
        self.transformations = [
            ProgramProcessor.CP_TRANSFORMATIONS[t]
            for t in self.args.transformation_types
        ]
        self.ncp_transformations = list(
            ProgramProcessor.NCP_TRANSFORMATIONS.values())
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
        transformer = transformation_cls(
            program, self.args.language, logger,
            self.args.options[transformation_cls.get_name()])
        if self.args.debug:
            print("Transformation " + str(transformation_number) + ": " +
                  transformer.get_name())
        transformer.transform()
        program = transformer.result()
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
            transformation = self.CP_TRANSFORMATIONS.get(line)
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
        if self.args.log:
            logger = Logger(self.args.name, self.args.test_directory,
                            self.proc_id, "Generator",
                            self.proc_id)
        else:
            logger = None
        generator = Generator(
            language=self.args.language,
            logger=logger,
            options=self.args.options["Generator"])
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
        if not transformer.is_transformed:
            return None
        return program, transformer.preserve_correctness()

    def inject_fault(self, program):
        transformer_cls = random.choice(self.ncp_transformations)
        program, transformer = self._apply_transformation(
            transformer_cls, self.current_transformation + 1, program)
        self.current_transformation += 1
        if not transformer.is_transformed:
            return None
        return program, transformer.error_injected
