1. Lexer - tokenizes the input
2. Parser - builds the AST
3. Scoper - builds the symbol table and checks the scope symbols and `break`/`continue` statements
4. Optimizer - optimizes the AST
5. TypeChecker - type checks the AST
6. (Optional) Tree Printer - prints the AST. May be run at any time.