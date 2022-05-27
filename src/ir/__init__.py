from src.ir.kotlin_types import KotlinBuiltinFactory
from src.ir.groovy_types import GroovyBuiltinFactory
from src.ir.java_types import JavaBuiltinFactory
from src.ir.typescript_types import TypeScriptBuiltinFactory

BUILTIN_FACTORIES = {
    "kotlin": KotlinBuiltinFactory(),
    "groovy": GroovyBuiltinFactory(),
    "java": JavaBuiltinFactory(),
    "typescript": TypeScriptBuiltinFactory()
}
