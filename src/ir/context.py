from collections import OrderedDict

from src import utils
from src.ir import ast


class Context():

    def __init__(self):
        self._context = {}
        # A lookup from declarations to namespaces
        self._namespaces = {}

    def _add_entity(self, namespace, entity, name, value):
        if namespace in self._context:
            self._context[namespace][entity][name] = value
        else:
            self._context[namespace] = {
                'types': {},
                'funcs': {},
                'lambdas': {},
                'vars': {},
                'classes': {},
                'decls': OrderedDict()  # Here we keep the declaration order
            }
            self._context[namespace][entity][name] = value
        self._namespaces[value] = namespace

    def _remove_entity(self, namespace, entity, name):
        if namespace not in self._context:
            return
        if name in self._context[namespace][entity]:
            decl = self._context[namespace][entity][name]
            if decl in self._namespaces:
                del self._namespaces[decl]
            del self._context[namespace][entity][name]

    def add_type(self, namespace, type_name, t):
        self._add_entity(namespace, 'types', type_name, t)

    def add_func(self, namespace, func_name, func):
        self._add_entity(namespace, 'funcs', func_name, func)
        self._add_entity(namespace, 'decls', func_name, func)

    def add_lambda(self, namespace, shadow_name, lmd):
        self._add_entity(namespace, 'lambdas', shadow_name, lmd)

    def add_var(self, namespace, var_name, var):
        self._add_entity(namespace, 'vars', var_name, var)
        self._add_entity(namespace, 'decls', var_name, var)

    def add_class(self, namespace, class_name, cls):
        self._add_entity(namespace, 'classes', class_name, cls)
        self._add_entity(namespace, 'decls', class_name, cls)

    def remove_type(self, namespace, type_name):
        self._remove_entity(namespace, 'types', type_name)

    def remove_var(self, namespace, var_name):
        self._remove_entity(namespace, 'vars', var_name)
        self._remove_entity(namespace, 'decls', var_name)

    def remove_func(self, namespace, func_name):
        self._remove_entity(namespace, 'funcs', func_name)
        self._remove_entity(namespace, 'decls', func_name)

    def remove_lambda(self, namespace, shadow_name):
        self._remove_entity(namespace, 'lambdas', shadow_name)

    def remove_class(self, namespace, class_name):
        self._remove_entity(namespace, 'classes', class_name)
        self._remove_entity(namespace, 'decls', class_name)

    def _get_declarations_glob(self, namespace, decl_type):
        decls = OrderedDict({})
        namespaces = [(namespace[0],)]
        while namespaces:
            namespace = namespaces.pop()
            decl = self._context.get(namespace, {}).get(decl_type)
            if decl is not None:
                decls.update(decl)
            namespaces.extend(self.find_namespaces(namespace, True))
        return decls

    def _get_declarations(self, namespace, decl_type, only_current, glob, none):
        len_namespace = len(namespace)
        assert len_namespace >= 1
        decls = {}
        if glob:
            decls = self._get_declarations_glob(namespace, decl_type)
        elif len_namespace == 1 or only_current:
            decls = self._context.get(namespace, {}).get(decl_type, {})
        else:
            start = (namespace[0],)
            decls = OrderedDict(self._context.get(start, {}).get(decl_type) or {})
            for ns in namespace[1:]:
                start = start + (ns,)
                decl = self._context.get(start, {}).get(decl_type)
                if decl is not None:
                    decls.update(decl)
        if not none:
            # Do not return artificial nodes
            decls = {k: v for k, v in decls.items() if v is not None}
        return decls

    def find_namespaces(self, namespace, none):
        func_namespaces = [namespace + (fname,)
                           for fname in self.get_funcs(namespace, True, none=none)]
        class_namespaces = [namespace + (cname,)
                            for cname in self.get_classes(namespace, True, none=none)]
        return func_namespaces + class_namespaces

    def get_namespaces_decls(self, namespace, name, decl_type, glob=True):
        """Return a set of tuples of namespace, decl. Note that namespace
        includes the name of the decl.
        """
        namespaces_decls = set()  # Set of tuples of namespace, decl
        if glob:
            namespaces = [(namespace[0],)]
        else:
            namespaces = [namespace]
        while namespaces:
            namespace = namespaces.pop()
            decls = self._context.get(namespace, {}).get(decl_type)
            if decls is not None:
                for decl_name, decl in decls.items():
                    if decl_name == name:
                        ns = namespace + (name,)
                        namespaces_decls.add((ns, decl))
            namespaces.extend(self.find_namespaces(namespace, none=False))
        return namespaces_decls

    def get_decl(self, namespace, name):
        return self._context.get(namespace, {}).get('decls', {}).get(
            name, None)

    def get_lambda(self, namespace, name):
        return self._context.get(namespace, {}).get('lambdas', {}).get(
            name, None)

    def get_types(self, namespace, only_current=False, glob=False, none=False):
        return self._get_declarations(namespace, 'types', only_current, glob, none)

    def get_funcs(self, namespace, only_current=False, glob=False, none=False):
        return self._get_declarations(namespace, 'funcs', only_current, glob, none)

    def get_lambdas(self, namespace, only_current=False, glob=False, none=False):
        return self._get_declarations(namespace, 'lambdas', only_current, glob, none)

    def get_vars(self, namespace, only_current=False, glob=False, none=False):
        return self._get_declarations(namespace, 'vars', only_current, glob, none)

    def get_classes(self, namespace, only_current=False, glob=False, none=False):
        return self._get_declarations(namespace, 'classes', only_current, glob, none)

    def get_declarations(self, namespace, only_current=False, glob=False, none=False):
        return self._get_declarations(namespace, 'decls', only_current, glob, none)

    def remove_namespace(self, namespace):
        if namespace in self._context:
            self._context.pop(namespace)

    def get_declarations_in(self, namespace):
        decls = {}
        for ns, entities in self._context.items():
            if utils.prefix_lst(namespace, ns):
                decls[ns] = entities['decls']
        return decls

    def get_decl_type(self, namespace, name):
        return type(self.get_decl(namespace, name))

    def get_namespace(self, decl):
        return self._namespaces.get(decl, None)

    def get_parent(self, namespace):
        if len(namespace) < 2:
            return None
        parent_namespace = namespace[:-1]
        return self.get_decl(parent_namespace[:-1], parent_namespace[-1])

    def get_parent_class(self, namespace):
        parent = self.get_parent(namespace)
        if parent is None and not (len(namespace) > 2 and
                                   'lambda_' in namespace[-2]):
            return None
        if isinstance(parent, ast.ClassDeclaration):
            return parent
        return self.get_parent_class(namespace[:-1])


def get_decl(context, namespace, decl_name: str, limit=None):
    """
    We search the context for a declaration with the given name (`decl_name`).

    The search begins from the given namespace `namespace` up to the namespace
    given by `limit`.
    """
    def stop_cond(ns):
        # If 'limit' is provided, we search the given declaration 'node'
        # up to a certain namespace.
        return (len(ns)
                if limit is None
                else utils.prefix_lst(limit, ns))

    while stop_cond(namespace):
        decls = context.get_declarations(namespace, True)
        decl = decls.get(decl_name)
        if decl:
            return namespace, decl
        namespace = namespace[:-1]
    return None
