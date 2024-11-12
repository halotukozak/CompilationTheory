from lab3.AST import *

Assign(var=SymbolRef(symbol='D1'), op='=',
       expr=Apply(fun=SymbolRef(symbol='.+'),
                  args=[SymbolRef(symbol='A'), Apply(fun=SymbolRef(symbol="'"), args=[SymbolRef(symbol='B')])]))
Assign(var=SymbolRef(symbol='D2'), op='-=', expr=Apply(fun=SymbolRef(symbol='.-'), args=[SymbolRef(symbol='A'), Apply(
    fun=SymbolRef(symbol="'"), args=[SymbolRef(symbol='B')])]))
Assign(var=SymbolRef(symbol='D3'), op='*=', expr=Apply(fun=SymbolRef(symbol='.*'), args=[SymbolRef(symbol='A'), Apply(
    fun=SymbolRef(symbol="'"), args=[SymbolRef(symbol='B')])]))
Assign(var=SymbolRef(symbol='D4'), op='/=', expr=Apply(fun=SymbolRef(symbol='./'), args=[SymbolRef(symbol='A'), Apply(
    fun=SymbolRef(symbol="'"), args=[SymbolRef(symbol='B')])]))
