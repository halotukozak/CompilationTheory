from typing import Optional, Any

from lab4 import Predef
from lab4.AST import SymbolRef


class GlobalMarker(object):
    pass


class SymbolTable(object):
    class Scope(object):
        symbols: dict[str, SymbolRef] = {}
        children: dict[str, 'Scope'] = {}

        def __init__(self, parent: 'Scope', key: int | GlobalMarker, in_loop: Optional[bool]):
            self.parent = parent  # :Scope
            self.key = key
            if in_loop is not None:
                self.in_loop = in_loop
            else:
                self.in_loop = parent.in_loop

        def get(self, name: str) -> Optional[SymbolRef]:
            if name in self.symbols.keys():
                return self.symbols[name]
            return self.parent.get(name) if self.parent else None

        def __contains__(self, symbol: SymbolRef) -> bool:
            return symbol.name in self.symbols.keys() or (self.parent is not None and symbol in self.parent)

    global_scope = Scope(None, GlobalMarker(), False)
    global_scope.symbols = Predef.symbols

    actual_scope = global_scope

    def push_scope(self, name: Any):
        self.actual_scope = self.actual_scope.children[id(name)]

    def pop_scope(self):
        self.actual_scope = self.actual_scope.parent

    def get_symbol(self, name: str) -> Optional[SymbolRef]:
        return self.actual_scope.get(name)