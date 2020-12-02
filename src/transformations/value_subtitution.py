from src import utils
from src.ir import ast
from src.ir import kotlin_types as kt
from src.generators import Generator
from src.transformations.base import Transformation


class ValueSubtitution(Transformation):

    CORRECTNESS_PRESERVING = True
    NAME = 'Value Subtitution'

    def __init__(self):
        super(ValueSubtitution, self).__init__()
        self.program = None
        self.generator = None
        self.types = []

    def visit_program(self, node):
        self.generator = Generator(context=node.context)
        usr_types = [d for d in node.declarations
                     if isinstance(d, ast.ClassDeclaration)] + \
            self.generator.BUILTIN_TYPES
        self.types = usr_types
        usr_types.remove(kt.Any)
        new_node = super(ValueSubtitution, self).visit_program(node)
        if self.transform:
            self.program = new_node
        return node

    def generate_new(self, class_decl):
        return ast.New(
            class_decl.get_type(),
            args=[self.generator.generate_expr(f.field_type, only_leaves=True)
                  for f in class_decl.fields])

    def visit_new(self, node):
        con_type = node.class_type
        subclasses = []
        for sub_c in self.types:
            if isinstance(sub_c, ast.ClassDeclaration):
                sub_t = sub_c.get_type()
            else:
                sub_t = sub_c
            if sub_t == con_type:
                continue
            if sub_t.is_subtype(con_type):
                subclasses.append(sub_c)
        if not subclasses:
            return node
        sub_c = utils.random.choice(subclasses)
        generators = {
            kt.Boolean: self.generator.gen_bool_constant,
            kt.Char: self.generator.gen_char_constant,
            kt.String: self.generator.gen_string_constant,
            kt.Integer: self.generator.gen_integer_constant,
            kt.Short: self.generator.gen_integer_constant,
            kt.Long: self.generator.gen_integer_constant,
            kt.Float: lambda: self.generator.gen_real_constant(kt.Float),
            kt.Double: self.generator.gen_real_constant,
        }
        generate = generators.get(sub_c, lambda: self.generate_new(sub_c))
        new_node = generate()
        return new_node
