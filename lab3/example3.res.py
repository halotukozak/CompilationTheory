from lab3.AST import *

Assign(var=SymbolRef(symbol='N'), op='=', expr=10)
Assign(var=SymbolRef(symbol='M'), op='=', expr=20)
For(var=SymbolRef(symbol='i'), range=Range(start=1, end=SymbolRef(symbol='N')), body=[
    For(var=SymbolRef(symbol='j'), range=Range(start=SymbolRef(symbol='i'), end=SymbolRef(symbol='M')),
        body=[Apply(fun=SymbolRef(symbol='print'), args=[SymbolRef(symbol='i'), SymbolRef(symbol='j')])])])
While(condition=Apply(fun=SymbolRef(symbol='>'), args=[SymbolRef(symbol='k'), 0]), body=[
    If(condition=Apply(fun=SymbolRef(symbol='<'), args=[SymbolRef(symbol='k'), 5]),
       then=[Assign(var=SymbolRef(symbol='i'), op='=', expr=1)], else_=[
            If(condition=Apply(fun=SymbolRef(symbol='<'), args=[SymbolRef(symbol='k'), 10]),
               then=[Assign(var=SymbolRef(symbol='i'), op='=', expr=2)],
               else_=[Assign(var=SymbolRef(symbol='i'), op='=', expr=3)])]),
    Assign(var=SymbolRef(symbol='k'), op='=', expr=Apply(fun=SymbolRef(symbol='-'), args=[SymbolRef(symbol='k'), 1]))])
