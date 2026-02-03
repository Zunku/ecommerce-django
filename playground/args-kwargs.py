def suma(multiplo, *args):
    print(sum(args))

def demo(apellido, *args, **kwargs):
    print(args)
    print(kwargs)
    print(apellido)
    
# The normal argument have to be first
# 2 and 3 are *args
# nombre and lenguaje are **kwargs
# 
demo('Marcelo', 2,3, nombre='Daniel', lenguaje='Python')