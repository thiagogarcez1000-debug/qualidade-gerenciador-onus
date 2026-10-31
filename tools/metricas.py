"""Metricas estaticas simples para um arquivo Python – versão 1.1 (31/10/2026).

Uso: python tools/metricas.py caminho/arquivo.py
Só usa a biblioteca padrão (ast). Mesmas regras da versão 1.0 (11/10/2026); a 1.1 só passa a
imprimir o SHA-256 do arquivo analisado e a sobreposição entre except genérico e except: pass.

Regras de contagem
- Complexidade ciclomática (McCabe, aproximada): 1 + número de nós de decisão dentro da função:
  if/elif, for, while, expressão condicional (x if c else y), except, with, assert e cada "for"
  de compreensão; cada operador and/or soma (n.º de operandos - 1). Funções aninhadas são
  contadas dentro da função que as contém (a função externa inclui a complexidade da interna).
- Tamanho da função: linhas da definição até a última linha (inclui comentários e linhas em branco).
- except genérico: "except:" sem tipo ou "except Exception".
- except: pass: bloco except cujo corpo é só "pass" (de qualquer tipo). Os dois conjuntos
  se sobrepõem: um "except Exception: pass" entra nas duas contagens.
"""
import ast
import hashlib
import sys

VERSAO = "1.1"
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
    bruto = open(caminho, "rb").read()
    codigo = bruto.decode("utf-8")
    arvore = ast.parse(codigo)
    funcoes = [n for n in ast.walk(arvore)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    excepts = [n for n in ast.walk(arvore) if isinstance(n, ast.ExceptHandler)]
    genericos = [e for e in excepts if e.type is None or
                 (isinstance(e.type, ast.Name) and e.type.id == "Exception")]
    vazios = [e for e in excepts if len(e.body) == 1 and isinstance(e.body[0], ast.Pass)]
    ambos = [e for e in vazios if e in genericos]
    dados = sorted(((complexidade(f), f.end_lineno - f.lineno + 1, f.name) for f in funcoes),
                   reverse=True)
    ccs = [d[0] for d in dados]
    print(f"metricas.py v{VERSAO}  arquivo: {caminho}")
    print(f"SHA-256: {hashlib.sha256(bruto).hexdigest()}")
    print(f"Linhas: {len(codigo.splitlines())}")
    print(f"Funcoes: {len(funcoes)}  CC media: {sum(ccs) / max(len(ccs), 1):.1f}")
    print(f"CC>10: {sum(c > 10 for c in ccs)}  CC>20: {sum(c > 20 for c in ccs)}")
    print(f"except: {len(excepts)}  genericos: {len(genericos)}  except-pass: {len(vazios)}"
          f"  (generico E pass: {len(ambos)})")
    print(f"Docstrings: {sum(ast.get_docstring(f) is not None for f in funcoes)}")
    print("\nTop 10 por complexidade:")
    for cc, linhas, nome in dados[:10]:
        print(f"  {nome:<30} CC={cc:<4} linhas={linhas}")


if __name__ == "__main__":
    analisar(sys.argv[1])
