def two_way_subtyping(is_subtype):
    def inner(self, other):
        return is_subtype(self, other) or other.dynamic_subtyping(self)
    return inner
