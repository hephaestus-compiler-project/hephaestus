from src.ir.kotlin_types import KotlinBuiltinFactory
from src.ir.groovy_types import GroovyBuiltinFactory

BUILTIN_FACTORIES = {
    "kotlin": KotlinBuiltinFactory(),
    "groovy": GroovyBuiltinFactory()
}
