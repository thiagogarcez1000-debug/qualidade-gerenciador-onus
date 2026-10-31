"""Cobertura de linhas por função (MQ07) – versão 1.0 (31/10/2026). Só biblioteca padrão.

Uso: GERENCIADOR=caminho/gerenciador_onus.py python tools/cobertura.py
Roda toda a suíte de testes/ com sys.settrace e mede, para cada função listada, quantas das
linhas executáveis foram executadas pelos testes.
Regra: linha executável = linha inicial de cada comando (ast.stmt) dentro do corpo da função,
sem contar a docstring. É uma medição real de cobertura de linhas, equivalente ao "line
coverage" do pytest-cov, que não pôde ser instalado neste ambiente.
"""
import ast
import os
import sys
import unittest
from pathlib import Path

CRITICAS = ["carregar_dados_excel", "testar_internet", "diagnosticar", "renderizar_cards",
            "iniciar_painel", "abrir_provisionamento"]
OUTRAS = ["testar_todos_pings", "carregar_usuarios", "verificar_usuario", "_hash_senha"]


def linhas_executaveis(caminho, nomes):
    with open(caminho, encoding="utf-8") as f:
        arvore = ast.parse(f.read())
    res = {}
    for no in ast.walk(arvore):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)) and no.name in nomes and no.name not in res:
            corpo = no.body[1:] if ast.get_docstring(no) else no.body
            res[no.name] = {s.lineno for c in corpo for s in ast.walk(c) if isinstance(s, ast.stmt)}
    return res


def main():
    raiz = Path(__file__).resolve().parents[1]
    alvo = os.path.realpath(os.environ["GERENCIADOR"])
    executadas = set()

    def rastrear(frame, evento, arg):
        if os.path.realpath(frame.f_code.co_filename) != alvo:
            return None
        if evento == "line":
            executadas.add(frame.f_lineno)
        return rastrear

    sys.path.insert(0, str(raiz / "testes"))
    suite = unittest.defaultTestLoader.discover(str(raiz / "testes"))
    import threading
    threading.settrace(rastrear); sys.settrace(rastrear)
    resultado = unittest.TextTestRunner(stream=open(os.devnull, "w")).run(suite)
    sys.settrace(None); threading.settrace(None)
    print(f"Suíte: {resultado.testsRun} testes, {len(resultado.failures)} falhas, {len(resultado.errors)} erros")
    tot_e = tot_x = 0
    funcs = linhas_executaveis(alvo, CRITICAS + OUTRAS)
    for grupo, nomes in (("Funções críticas (MQ07)", CRITICAS), ("Outras funções testadas", OUTRAS)):
        print(f"\n{grupo}")
        ge = gx = 0
        for n in nomes:
            linhas = funcs.get(n, set())
            x = len(linhas & executadas)
            ge += len(linhas); gx += x
            print(f"  {n:<24} {x:>4}/{len(linhas):<4} {100 * x / max(len(linhas), 1):5.1f}%")
        print(f"  {'TOTAL':<24} {gx:>4}/{ge:<4} {100 * gx / max(ge, 1):5.1f}%")
        if grupo.startswith("Funções críticas"):
            tot_e, tot_x = ge, gx
    return tot_x, tot_e


if __name__ == "__main__":
    main()
