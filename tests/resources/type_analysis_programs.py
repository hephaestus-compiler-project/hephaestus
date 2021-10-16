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


# program5
var1 = ast.VariableDeclaration("y", ast.Variable("x"), var_type=kt.String)
body = ast.Block([var1, ast.Variable("y")])
param1 = ast.ParameterDeclaration("x", param_type=kt.String)
func_decl = ast.FunctionDeclaration("foo", [param1], kt.String, body,
                                    ast.FunctionDeclaration.FUNCTION)

f1 = ast.FieldDeclaration("f", type_param1)
cls1 = ast.ClassDeclaration("A", [], 0, fields=[f1], type_parameters=[type_param1])
t1 = cls1.get_type().new([kt.String])
func_call = ast.FunctionCall("foo", [ast.StringConstant("x")])
var2 = ast.VariableDeclaration("y", ast.New(t1, [func_call]), var_type=t1)

FUNC_NAMESPACE = ast.GLOBAL_NAMESPACE + (func_decl.name,)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_func(ast.GLOBAL_NAMESPACE, func_decl.name, func_decl)
context.add_var(ast.GLOBAL_NAMESPACE, var2.name, var2)
context.add_var(FUNC_NAMESPACE, param1.name, param1)
context.add_var(FUNC_NAMESPACE, var1.name, var1)
program5 = ast.Program(context, "kotlin")


# program6
param1 = ast.ParameterDeclaration("x", type_param1)
func = ast.FunctionDeclaration("foo", [param1], type_param1, ast.Variable("x"),
                               ast.FunctionDeclaration.CLASS_METHOD)
cls1 = ast.ClassDeclaration("A", [], 0, functions=[func],
                            type_parameters=[type_param1])
t1 = cls1.get_type().new([kt.String])
new = ast.New(t1, [])
func_call = ast.FunctionCall("foo", [], receiver=new)
var = ast.VariableDeclaration("x", func_call, var_type=kt.String)

FUNC_NAMESPACE = ast.GLOBAL_NAMESPACE + (cls1.name, func.name)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_var(ast.GLOBAL_NAMESPACE, var.name, var)
context.add_func(ast.GLOBAL_NAMESPACE + (cls1.name,), func.name, func)
context.add_var(FUNC_NAMESPACE, param1.name, param1)
program6 = ast.Program(context, "kotlin")


# program7
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1])
t1 = cls1.get_type().new([kt.String])
var1 = ast.VariableDeclaration("x", new, var_type=t1)
cond = ast.Conditional(ast.BooleanConstant("true"), ast.Variable("x"), new,
                       t1)
var2 = ast.VariableDeclaration("y", cond, var_type=t1)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
context.add_var(ast.GLOBAL_NAMESPACE, var2.name, var2)
program7 = ast.Program(context, "kotlin")


# program 8
var1 = ast.VariableDeclaration("x", ast.BottomConstant(t1), var_type=t1,
                               is_final=False)
assign = ast.Assignment("x", new)
body = ast.Block([var1, assign])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.FUNCTION)

FUNC_NAMESPACE = ast.GLOBAL_NAMESPACE + (func.name,)
context = ctx.Context()
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_var(FUNC_NAMESPACE, var1.name, var1)
program8 = ast.Program(context, "kotlin")


# program9
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1])
t1 = cls1.get_type().new([kt.String])
f = ast.FieldDeclaration("f", t1)
cls2 = ast.ClassDeclaration("B", [], 0, fields=[f])
new1 = ast.New(t1, [])
var1 = ast.VariableDeclaration("x", ast.BottomConstant(cls2.get_type()),
                               var_type=cls2.get_type())
assign = ast.Assignment("f", new1, receiver=ast.Variable("x"))
body = ast.Block([var1, assign])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.FUNCTION)
FUNC_NAMESPACE = ast.GLOBAL_NAMESPACE + (func.name,)

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_var(ast.GLOBAL_NAMESPACE + (cls2.name,), f.name, f)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(FUNC_NAMESPACE, var1.name, var1)
program9 = ast.Program(context, "kotlin")


# program10
f = ast.FieldDeclaration("f", type_param1)
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1],
                            fields=[f])
t1 = cls1.get_type().new([kt.String])
new1 = ast.New(t1, [ast.StringConstant("x")])
assign = ast.Assignment("f", ast.StringConstant("x"), receiver=new1)
body = ast.Block([assign])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.FUNCTION)

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_var(ast.GLOBAL_NAMESPACE + (cls1.name,), f.name, f)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
program10 = ast.Program(context, "kotlin")


# program 11
t2 = cls1.get_type().new([t1])
new2 = ast.New(t2, [new1])
assign = ast.Assignment("f", new1, receiver=new2)
body = ast.Block([assign])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.FUNCTION)

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_var(ast.GLOBAL_NAMESPACE + (cls1.name,), f.name, f)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
program11 = ast.Program(context, "kotlin")


# program 12
t1 = cls1.get_type().new([kt.String])
cls2 = ast.ClassDeclaration("B",
                            [ast.SuperClassInstantiation(
                                t1, [ast.StringConstant("x")])],
                            0)
new1 = ast.New(t1, [ast.StringConstant("x")])
new2 = ast.New(cls2.get_type(), [])
var1 = ast.VariableDeclaration("x", new2, var_type=cls2.get_type())
cond = ast.Conditional(ast.BooleanConstant("true"), new1, ast.Variable("x"),
                       t1)
assign = ast.Assignment("f", ast.StringConstant("x"), cond)
body = ast.Block([var1, assign])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.FUNCTION)
FUNC_NAMESPACE = ast.GLOBAL_NAMESPACE + (func.name,)

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE + (cls1.name,), f.name, f)
context.add_var(FUNC_NAMESPACE, var1.name, var1)
program12 = ast.Program(context, "kotlin")


# program 13
f = ast.FieldDeclaration("f", type_param1)
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1],
                            fields=[f])
t1 = cls1.get_type().new([kt.String])
cls2 = ast.ClassDeclaration("B",
                            [ast.SuperClassInstantiation(
                                t1, [ast.StringConstant("x")])],
                            0)
new1 = ast.New(t1, [ast.Variable("t")])
new2 = ast.New(cls2.get_type(), [])
var1 = ast.VariableDeclaration("x", new2, var_type=cls2.get_type())
cond = ast.Conditional(ast.BooleanConstant("true"), new1, ast.Variable("x"),
                       t1)
var2 = ast.VariableDeclaration("y", ast.FieldAccess(cond, "f"),
                               var_type=kt.String)
var3 = ast.VariableDeclaration("t", ast.StringConstant("x"),
                               var_type=kt.String)
body = ast.Block([var3, var1, var2])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.FUNCTION)
FUNC_NAMESPACE = ast.GLOBAL_NAMESPACE + (func.name,)

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE + (cls1.name,), f.name, f)
context.add_var(FUNC_NAMESPACE, var1.name, var1)
context.add_var(FUNC_NAMESPACE, var2.name, var2)
context.add_var(FUNC_NAMESPACE, var3.name, var3)
program13 = ast.Program(context, "kotlin")


# program 14
var1 = ast.VariableDeclaration("x", ast.StringConstant("x"), var_type=kt.Any)
assign = ast.Assignment("x", ast.New(kt.Any, []), None)
body = ast.Block([var1, assign])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.FUNCTION)

FUNC_NAMESPACE = ast.GLOBAL_NAMESPACE + (func.name,)
context = ctx.Context()
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(FUNC_NAMESPACE, var1.name, var1)
program14 = ast.Program(context, "kotlin")


# program15
f = ast.FieldDeclaration("f", type_param1)
type_param2 = tp.TypeParameter("T2", bound=type_param1)
cls1 = ast.ClassDeclaration("A", [], 0, fields=[f],
                            type_parameters=[type_param1, type_param2])
t = cls1.get_type().new([kt.Number, kt.Integer])
new = ast.New(t, [ast.IntegerConstant(1, kt.Number)])
var = ast.VariableDeclaration("x", new, var_type=t)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_var(ast.GLOBAL_NAMESPACE + (cls1.name,), f.name, f)
context.add_var(ast.GLOBAL_NAMESPACE, var.name, var)
program15 = ast.Program(context, "kotlin")


# program16
param1 = ast.ParameterDeclaration("x", type_param1)
func = ast.FunctionDeclaration("foo", [param1], kt.String,
                               ast.BottomConstant(kt.String),
                               ast.FunctionDeclaration.FUNCTION,
                               type_parameters=[type_param1])
func_call = ast.FunctionCall("foo", [ast.StringConstant("x")],
                             type_args=[kt.String])
func2 = ast.FunctionDeclaration("bar", [], kt.Unit,
                                ast.Block([func_call]),
                                ast.FunctionDeclaration.FUNCTION)
context = ctx.Context()
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_func(ast.GLOBAL_NAMESPACE, func2.name, func2)
context.add_var(ast.GLOBAL_NAMESPACE + (func.name,), param1.name, param1)
program16 = ast.Program(context, "kotlin")


# program 17
type_param2 = tp.TypeParameter("T2")
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param2])
t = cls1.get_type().new([kt.String])
new = ast.New(t, [])
func_call = ast.FunctionCall("foo", [new], type_args=[t])
func2 = ast.FunctionDeclaration("bar", [], kt.Unit,
                                ast.Block([func_call]),
                                ast.FunctionDeclaration.FUNCTION)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_func(ast.GLOBAL_NAMESPACE, func2.name, func2)
context.add_var(ast.GLOBAL_NAMESPACE + (func.name,), param1.name, param1)
program17 = ast.Program(context, "kotlin")


# program 18
t1 = cls1.get_type().new([type_param1])
t2 = cls1.get_type().new([kt.String])
new = ast.New(t2, [])
param1 = ast.ParameterDeclaration("x", t1)
func = ast.FunctionDeclaration("foo", [param1], kt.String,
                               ast.BottomConstant(kt.String),
                               ast.FunctionDeclaration.FUNCTION,
                               type_parameters=[type_param1])
func_call = ast.FunctionCall("foo", [new], type_args=[kt.String])
func2 = ast.FunctionDeclaration("bar", [], kt.Unit,
                                ast.Block([func_call]),
                                ast.FunctionDeclaration.FUNCTION)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_func(ast.GLOBAL_NAMESPACE, func2.name, func2)
context.add_var(ast.GLOBAL_NAMESPACE + (func.name,), param1.name, param1)
program18 = ast.Program(context, "kotlin")


# program 19
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1])
t1 = cls1.get_type().new([kt.Integer])
new1 = ast.New(t1, [])
cls2 = ast.ClassDeclaration("B",
                            [ast.SuperClassInstantiation(t1, [])], 0)
f = ast.FieldDeclaration("f", cls1.get_type().new([type_param1]))
cls3 = ast.ClassDeclaration("C", [], 0, type_parameters=[type_param1],
                            fields=[f])
t2 = cls3.get_type().new([kt.Integer])
var1 = ast.VariableDeclaration("x",
                               ast.New(t2, [ast.New(cls2.get_type(), [])]),
                               var_type=t2)

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_class(ast.GLOBAL_NAMESPACE, cls3.name, cls3)
context.add_var(ast.GLOBAL_NAMESPACE + (cls3.name,), f.name, f)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program19 = ast.Program(context, "kotlin")


# program 20
f = ast.FieldDeclaration("f", cls1.get_type().new([type_param1]))
cls2 = ast.ClassDeclaration("B", [], 0, type_parameters=[type_param1],
                            fields=[f])

t1 = cls1.get_type().new([kt.String])
t2 = cls2.get_type().new([kt.String])
new = ast.New(t2, [ast.New(t1, [])])
var1 = ast.VariableDeclaration("x", new, var_type=t2)

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_var(ast.GLOBAL_NAMESPACE + (cls2.name,), cls2.name, cls2)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program20 = ast.Program(context, "kotlin")


# program 21
cl2 = ast.ClassDeclaration("B", [], 0, type_parameters=[type_param1])
t1 = cls1.get_type().new([type_param1])
t2 = cls2.get_type().new([t1])
f = ast.FieldDeclaration("f", t2)
cls3 = ast.ClassDeclaration("C", [], 0, fields=[f], type_parameters=[type_param1])
new = ast.New(cls2.get_type().new([cls1.get_type().new([kt.String])]), [])
new = ast.New(cls3.get_type().new([kt.String]), [new])
var1 = ast.VariableDeclaration("x", new, var_type=cls3.get_type().new([kt.String]))

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_class(ast.GLOBAL_NAMESPACE, cls3.name, cls3)
context.add_var(ast.GLOBAL_NAMESPACE + (cls3.name,), cls3.name, cls3)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program21 = ast.Program(context, "kotlin")


# program 22
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1])
type_param2 = tp.TypeParameter("T2")
f = ast.FieldDeclaration("f", type_param2)
cls2 = ast.ClassDeclaration("B", [], 0, type_parameters=[type_param2],
                            fields=[f])
t1 = cls1.get_type().new([kt.String])
t2 = cls2.get_type().new([t1])
new = ast.New(t1, [])
new2 = ast.New(t2, [new])
var1 = ast.VariableDeclaration("x", new2, var_type=t2)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_var(ast.GLOBAL_NAMESPACE + (cls2.name,), f.name, f)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program22 = ast.Program(context, "kotlin")


# program 23
func = ast.FunctionDeclaration("foo", [], type_param1,
                               ast.BottomConstant(type_param1),
                               ast.FunctionDeclaration.FUNCTION,
                               type_parameters=[type_param1])
func_call = ast.FunctionCall("foo", [], type_args=[kt.String])
var1 = ast.VariableDeclaration("x", func_call, var_type=kt.String)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program23 = ast.Program(context, "kotlin")


# program 24
func = ast.FunctionDeclaration("foo", [], type_param1,
                               ast.BottomConstant(type_param1),
                               ast.FunctionDeclaration.FUNCTION,
                               type_parameters=[type_param1])
func_call = ast.FunctionCall("foo", [], type_args=[kt.String])
t = cls1.get_type().new([kt.String])
var1 = ast.VariableDeclaration("x", func_call, var_type=t1)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program24 = ast.Program(context, "kotlin")


# program 25
func = ast.FunctionDeclaration("foo", [], cls1.get_type().new([type_param1]),
                               ast.BottomConstant(cls1.get_type().new([type_param1])),
                               ast.FunctionDeclaration.FUNCTION,
                               type_parameters=[type_param1])
func_call = ast.FunctionCall("foo", [], type_args=[kt.String])
t = cls1.get_type().new([kt.String])
var1 = ast.VariableDeclaration("x", func_call, var_type=t1)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program25 = ast.Program(context, "kotlin")


# program 26
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1])
t = cls1.get_type().new([type_param1])
cls2 = ast.ClassDeclaration("B",
                            [ast.SuperClassInstantiation(t, [])],
                            0, type_parameters=[type_param1])
b = cls2.get_type().new([type_param1])
func = ast.FunctionDeclaration("foo", [], b,
                               ast.BottomConstant(b),
                               ast.FunctionDeclaration.FUNCTION,
                               type_parameters=[type_param1])
t = cls1.get_type().new([kt.String])
func_call = ast.FunctionCall("foo", [], type_args=[kt.String])
var1 = ast.VariableDeclaration("x", func_call, var_type=t)
context= ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program26 = ast.Program(context, "kotlin")


# program 27
type_param2 = tp.TypeParameter("T2")
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1,
                                                         type_param2])
t = cls1.get_type().new([kt.String, type_param1])
cls2 = ast.ClassDeclaration("B",
                            [ast.SuperClassInstantiation(t, [])],
                            0, type_parameters=[type_param1])
b = cls2.get_type().new([type_param1])
func = ast.FunctionDeclaration("foo", [], b,
                               ast.BottomConstant(b),
                               ast.FunctionDeclaration.FUNCTION,
                               type_parameters=[type_param1])
t = cls1.get_type().new([kt.String, kt.Integer])
func_call = ast.FunctionCall("foo", [], type_args=[kt.String])
var1 = ast.VariableDeclaration("x", func_call, var_type=t)
context= ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program27 = ast.Program(context, "kotlin")


# program 28
cls1 = ast.ClassDeclaration("A", [], 0)
f = ast.FieldDeclaration("f", cls1.get_type())
cls2 = ast.ClassDeclaration("B", [], 0, fields=[f],
                            type_parameters=[type_param1])

t = cls2.get_type().new([type_param1])
new = ast.New(t, [ast.New(cls1.get_type(), [])])
var1 = ast.VariableDeclaration("x", new, var_type=t)
body = ast.Block([var1])
func = ast.FunctionDeclaration("foo", [], kt.Unit, body,
                               ast.FunctionDeclaration.CLASS_METHOD,
                               type_parameters=[type_param1])
cls3 = ast.ClassDeclaration("C", [], 0, functions=[func],
                            type_parameters=[type_param1])

context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_class(ast.GLOBAL_NAMESPACE, cls3.name, cls3)
context.add_var(ast.GLOBAL_NAMESPACE + (cls2.name,), f.name, f)
context.add_func(ast.GLOBAL_NAMESPACE + (cls3.name,), func.name, func)
context.add_var(ast.GLOBAL_NAMESPACE + (cls3.name, func.name), var1.name, var1)
program28 = ast.Program(context, "kotlin")


# program 29
cls1 = ast.ClassDeclaration("A", [], 0, type_parameters=[type_param1])
t = cls1.get_type().new([type_param1])
f2 = ast.FieldDeclaration("f", field_type=t)
cls2 = ast.ClassDeclaration("B", [], 0, type_parameters=[type_param1],
                            fields=[f2])
t2 = cls2.get_type().new([kt.String])
t3 = cls1.get_type().new([kt.String])
var1 = ast.VariableDeclaration("x", ast.New(t2, [ast.New(t3, [])]),
                               var_type=t2)
context = ctx.Context()
context.add_class(ast.GLOBAL_NAMESPACE, cls1.name, cls1)
context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
context.add_var(ast.GLOBAL_NAMESPACE + (cls2.name,), f.name, f)
context.add_var(ast.GLOBAL_NAMESPACE, var1.name, var1)
program29 = ast.Program(context, "kotlin")
