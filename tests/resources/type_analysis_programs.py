from src.ir import ast, types as tp, kotlin_types as kt, context as ctx


# program1
type_param1 = tp.TypeParameter("T")
cls = ast.ClassDeclaration("Foo", [], 0, fields=[], functions=[],
                           type_parameters=[type_param1])
t = cls.get_type().new([kt.String])

new = ast.New(t, [])
var_decl = ast.VariableDeclaration("x", new, var_type=t)
context = ctx.Context()
context.add_var(ast.GLOBAL_NAMESPACE, var_decl.name, var_decl)
context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
program1 = ast.Program(context, "kotlin")


# program2
field = ast.FieldDeclaration("f", field_type=type_param1)
cls = ast.ClassDeclaration("Foo", [], 0, fields=[field], functions=[],
                           type_parameters=[type_param1])
var_x = ast.VariableDeclaration("x", ast.StringConstant("x"),
                                var_type=kt.String)
t2 = cls.get_type().new([kt.String])
new2 = ast.New(t2, [ast.Variable("x")])
var_y = ast.VariableDeclaration("y", new2, var_type=t2)
context = ctx.Context()
context.add_var(ast.GLOBAL_NAMESPACE, var_x.name, var_x)
context.add_var(ast.GLOBAL_NAMESPACE, var_y.name, var_y)
context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
program2 = ast.Program(context, "kotlin")


# program3
field2 = ast.FieldDeclaration("f", field_type=t2)
cls2 = ast.ClassDeclaration("Bar", [], 0, fields=[field2])
new3 = ast.New(cls2.get_type(), [new2])
var_y2 = ast.VariableDeclaration("y", new3, var_type=cls2.get_type())
context = ctx.Context()
context.add_var(ast.GLOBAL_NAMESPACE, var_x.name, var_x)
context.add_var(ast.GLOBAL_NAMESPACE, var_y.name, var_y2)
context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
program3 = ast.Program(context, "kotlin")


# program4
type_param1 = tp.TypeParameter("T")
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1])
type_param2 = tp.TypeParameter("T2")
t1 = cls1.get_type().new([type_param2])
cls2 = ast.ClassDeclaration("B", [ast.SuperClassInstantiation(t1, [])],
                            0, type_parameters=[type_param1, type_param2])
t2 = cls2.get_type().new([kt.String, type_param1])
cls3 = ast.ClassDeclaration("C", [ast.SuperClassInstantiation(t2, [])],
                            0, type_parameters=[type_param1])
t1_str = cls1.get_type().new([kt.String])
t2_str = cls3.get_type().new([kt.String])
var = ast.VariableDeclaration("x", ast.New(t2_str, []), var_type=t1_str)
context = ctx.Context()
context.add_var(ast.GLOBAL_NAMESPACE, var.name, var)
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_class(ast.GLOBAL_NAMESPACE, cls3.name, cls3)
program4 = ast.Program(context, "kotlin")
