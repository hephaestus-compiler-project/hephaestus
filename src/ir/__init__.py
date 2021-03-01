from src.ir.kotlin_types import KotlinBuiltinFactory
from src.ir.groovy_types import GroovyBuiltinFactory
from src.ir.java_types import JavaBuiltinFactory

BUILTIN_FACTORIES = {
    "kotlin": KotlinBuiltinFactory(),
    "groovy": GroovyBuiltinFactory(),
    "java": JavaBuiltinFactory()
}
