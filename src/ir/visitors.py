from src.ir import ast


class ASTVisitor(object):

    def visit(self, node):
        visitors = {
            ast.ClassDeclaration: self.visit_class_decl,
            ast.FieldDeclaration: self.visit_field_decl,
            ast.VariableDeclaration: self.visit_var_decl,
            ast.ParameterDeclaration: self.visit_param_decl,
            ast.FunctionDeclaration: self.visit_func_decl,
            ast.IntegerConstant: self.visit_integer_constant,
            ast.RealConstant: self.visit_real_constant,
            ast.CharConstant: self.visit_char_constant,
            ast.StringConstant: self.visit_string_constant,
            ast.BooleanConstant: self.visit_boolean_constant,
            ast.Variable: self.visit_variable,
            ast.LogicalExpr: self.visit_logical_expr,
            ast.EqualityExpr: self.visit_equality_expr,
            ast.ComparisonExpr: self.visit_comparison_expr,
            ast.ArithExpr: self.visit_arith_expr,
            ast.Conditional: self.visit_conditional,
            ast.New: self.visit_new,
            ast.FieldAccess: self.visit_field_access,
            ast.FunctionCall: self.visit_func_call,
            ast.Assignment: self.visit_assign,
            ast.Program: self.visit_program,
            ast.Block: self.visit_block,
        }
        visitor = visitors.get(node.__class__)
        if visitor is None:
            raise Exception(
                "Cannot find visitor for instance node " + str(node.__class__))
        visitor(node)

    def visit_program(self, node):
        raise NotImplementedError('visit_program() must be implemented')

    def visit_block(self, node):
        raise NotImplementedError('visit_block() must be implemented')

    def visit_class_decl(self, node):
        raise NotImplementedError('visit_class_decl() must be implemented')

    def visit_var_decl(self, node):
        raise NotImplementedError('visit_var_decl() must be implemented')

    def visit_field_decl(self, node):
        raise NotImplementedError('visit_field_decl() must be implemented')

    def visit_param_decl(self, node):
        raise NotImplementedError('visit_param_decl() must be implemented')

    def visit_func_decl(self, node):
        raise NotImplementedError('visit_func_decl() must be implemented')

    def visit_integer_constant(self, node):
        raise NotImplementedError(
            'visit_integer_constant() must be implemented')

    def visit_real_constant(self, node):
        raise NotImplementedError('visit_real_constant() must be implemented')

    def visit_char_constant(self, node):
        raise NotImplementedError('visit_char_constant() must be implemented')

    def visit_string_constant(self, node):
        raise NotImplementedError(
            'visit_string_constant() must be implemented')

    def visit_boolean_constant(self, node):
        raise NotImplementedError(
            'visit_boolean_constant() must be implemented')

    def visit_variable(self, node):
        raise NotImplementedError('visit_variable() must be implemented')

    def visit_logical_expr(self, node):
        raise NotImplementedError('visit_logical_expr() must be implemented')

    def visit_equality_expr(self, node):
        raise NotImplementedError('visit_equality_expr() must be implemented')

    def visit_comparison_expr(self, node):
        raise NotImplementedError('visit_comparison_expr() must be implemented')

    def visit_arith_expr(self, node):
        raise NotImplementedError('visit_arith_expr() must be implemented')

    def visit_conditional(self, node):
        raise NotImplementedError('visit_conditional() must be implemented')

    def visit_new(self, node):
        raise NotImplementedError('visit_new() must be implemented')

    def visit_field_access(self, node):
        raise NotImplementedError('visit_field_access() must be implemented')

    def visit_func_call(self, node):
        raise NotImplementedError('visit_func_call() must be implemented')

    def visit_assign(self, node):
        raise NotImplementedError('visit_assign() must be implemented')
