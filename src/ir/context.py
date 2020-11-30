from collections import OrderedDict


class Context(object):
    def __init__(self):
        self._context = {}

    def _add_entity(self, namespace, entity, name, value):
        if namespace in self._context:
            self._context[namespace][entity][name] = value
        else:
            self._context[namespace] = {
                'funcs': {},
                'vars': {},
                'classes': {},
                'decls': OrderedDict() # Here we keep the declaration order
            }
            self._context[namespace][entity][name] = value

    def add_func(self, namespace, func_name, func):
        self._add_entity(namespace, 'funcs', func_name, func)
        self._add_entity(namespace, 'decls', func_name, func)

    def add_var(self, namespace, var_name, var):
        self._add_entity(namespace, 'vars', var_name, var)
        self._add_entity(namespace, 'decls', var_name, var)

    def add_class(self, namespace, class_name, cls):
        self._add_entity(namespace, 'classes', class_name, cls)
        self._add_entity(namespace, 'decls', class_name, cls)

    def _get_declarations(self, namespace, decl_type, only_current):
        len_namespace = len(namespace)
        assert len_namespace >= 1
        if len_namespace == 1 or only_current:
            return self._context.get(namespace, {}).get(decl_type, {})
        start = (namespace[0],)
        decls = {}
        for n in namespace[1:]:
            decl = self._context.get(start, {}).get(decl_type)
            if decl is not None:
                decls.update(decl)
            start = start + (n,)
        return decls

    def get_funcs(self, namespace, only_current=False):
        return self._get_declarations(namespace, 'funcs', only_current)

    def get_vars(self, namespace, only_current=False):
        return self._get_declarations(namespace, 'vars', only_current)

    def get_classes(self, namespace, only_current=False):
        return self._get_declarations(namespace, 'classes', only_current)

    def get_declarations(self, namespace, only_current=False):
        return self._get_declarations(namespace, 'decls', only_current)

    def remove_namespace(self, namespace):
        if namespace in self._context:
            self._context.pop(namespace)

