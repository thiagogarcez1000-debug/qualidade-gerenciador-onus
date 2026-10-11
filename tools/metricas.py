"""Metricas estaticas simples para um arquivo Python.

Uso: python tools/metricas.py caminho/arquivo.py
Calcula complexidade ciclomatica aproximada (McCabe), tamanho das funcoes,
blocos except genericos/vazios e docstrings, usando apenas a biblioteca padrao.
"""
import ast
import sys

DECISOES = (ast.If, ast.For, ast.While, ast.IfExp, ast.ExceptHandler,
            ast.With, ast.Assert, ast.comprehension)


def complexidade(func):
    cc = 1
    for no in ast.walk(func):
        if isinstance(no, DECISOES):
            cc += 1
        elif isinstance(no, ast.BoolOp):
            cc += len(no.values) - 1
    return cc


def analisar(caminho):
    codigo = open(caminho, encoding="utf-8").read()
    arvore = ast.parse(codigo)
    funcoes = [n for n in ast.walk(arvore)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    excepts = [n for n in ast.walk(arvore) if isinstance(n, ast.ExceptHandler)]
    genericos = [e for e in excepts if e.type is None or
                 (isinstance(e.type, ast.Name) and e.type.id == "Exception")]
    vazios = [e for e in excepts if len(e.body) == 1 and isinstance(e.body[0], ast.Pass)]
    dados = sorted(((complexidade(f), f.end_lineno - f.lineno + 1, f.name) for f in funcoes),
                   reverse=True)
    ccs = [d[0] for d in dados]
    print(f"Linhas: {len(codigo.splitlines())}")
    print(f"Funcoes: {len(funcoes)}  CC media: {sum(ccs) / max(len(ccs), 1):.1f}")
    print(f"CC>10: {sum(c > 10 for c in ccs)}  CC>20: {sum(c > 20 for c in ccs)}")
    print(f"except: {len(excepts)}  genericos: {len(genericos)}  except-pass: {len(vazios)}")
    print(f"Docstrings: {sum(ast.get_docstring(f) is not None for f in funcoes)}")
    print("\nTop 10 por complexidade:")
    for cc, linhas, nome in dados[:10]:
        print(f"  {nome:<30} CC={cc:<4} linhas={linhas}")


if __name__ == "__main__":
    analisar(sys.argv[1])
