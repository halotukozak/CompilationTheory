1. MatrixScanner - tokenizes the input
2. MatrixParser - builds the AST, establish types
3. MatrixScoper - builds the symbol table and checks the scope symbols and `break`/`continue` statements
4. TypeChecker - type checks the AST
5. (Optional) Tree Printer - prints the AST. May be run at any time.
6. 