from lab3.AST import *

Assign(var=SymbolRef(symbol='A'), op='=', expr=Apply(fun=SymbolRef(symbol='zeros'), args=[5]))
Assign(var=SymbolRef(symbol='B'), op='=', expr=Apply(fun=SymbolRef(symbol='ones'), args=[7]))
Assign(var=SymbolRef(symbol='I'), op='=', expr=Apply(fun=SymbolRef(symbol='eye'), args=[10]))
Assign(var=SymbolRef(symbol='E1'), op='=', expr=Matrix(vectors=[Vector(elements=[1, 2, 3]), Vector(elements=[4, 5, 6]), Vector(elements=[7, 8, 9])]))
Assign(var=MatrixRef(matrix=SymbolRef(symbol='A'), row=1, col=3), op='=', expr=0)
