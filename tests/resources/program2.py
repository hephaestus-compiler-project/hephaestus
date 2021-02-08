from src.ir.ast import *
from src.ir.kotlin_types import *
from src.ir.context import *

# open class Bam(val x: String) {
#   open fun getX(z: String): String {
#     return x
#   }
# }

xB_field = FieldDeclaration(
    "x",
    StringType(),
    is_final=True,
    override=False
)

z_get_param = ParameterDeclaration("z", StringType())
getX_func = FunctionDeclaration(
    "getX",
    params=[
        z_get_param
    ],
    func_type=FunctionDeclaration.CLASS_METHOD,
    is_final=False,
    ret_type=StringType(),
    body=Block([
        Variable(xB_field.name)

    ])
)

bam_cls = ClassDeclaration(
    "Bam",
    superclasses=[],
    class_type=ClassDeclaration.REGULAR,
    is_final=False,
    fields=[xB_field],
    functions=[getX_func]
)

ctx = Context()
ctx.add_class(GLOBAL_NAMESPACE, bam_cls.name, bam_cls)
ctx.add_var(GLOBAL_NAMESPACE + ('Bam',), 'x', xB_field)
ctx.add_var(GLOBAL_NAMESPACE + ('Bam', 'getX'), 'z', z_get_param)
ctx.add_func(GLOBAL_NAMESPACE + ('Bam',), getX_func.name, getX_func)
program = Program(ctx, language="kotlin")
