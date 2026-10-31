"""Busca automatizada de credenciais no código (teste T08) – versão 1.0 (31/10/2026).

Uso: python tools/busca_segredos.py caminho/arquivo.py
Regra: percorre a árvore sintática (ast) e aponta toda string literal NÃO vazia atribuída a
- uma variável (NOME = "...") ou
- uma chave de dicionário ({"NOME": "..."})
cujo nome contenha senha/password/pass/secret/token/apikey (classe SENHA) ou usuario/user/login (classe USUARIO).
Nomes iniciados por ARQUIVO_, PASTA_ ou CAMPOS_ são ignorados (são caminhos de arquivo, não credenciais).
Os valores nunca são impressos: aparecem mascarados com o número de caracteres.
Código de saída: quantidade de ocorrências da classe SENHA (0 = critério MQ02(1) atendido).
"""
import ast
import re
import sys

SENHA = re.compile(r"senha|password|passwd|pass\b|_pass|secret|token|api_?key", re.I)
USUARIO = re.compile(r"usuario|user|login", re.I)
IGNORAR = re.compile(r"^(ARQUIVO|PASTA|CAMPOS)_", re.I)   # nomes de arquivo/pasta, não credenciais


def classificar(nome):
    if IGNORAR.search(nome):
        return None
    if SENHA.search(nome):
        return "SENHA"
    if USUARIO.search(nome):
        return "USUARIO"
    return None


def buscar(caminho):
    with open(caminho, encoding="utf-8") as f:
        arvore = ast.parse(f.read())
    achados = []
    for no in ast.walk(arvore):
        pares = []
        if isinstance(no, ast.Assign):
            pares = [(t.id, no.value) for t in no.targets if isinstance(t, ast.Name)]
        elif isinstance(no, ast.Dict):
            pares = [(k.value, v) for k, v in zip(no.keys, no.values)
                     if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        for nome, valor in pares:
            classe = classificar(nome)
            if classe and isinstance(valor, ast.Constant) and isinstance(valor.value, str) and valor.value:
                achados.append((valor.lineno, nome, classe, len(valor.value)))
    return sorted(set(achados))


if __name__ == "__main__":
    achados = buscar(sys.argv[1])
    for linha, nome, classe, n in achados:
        print(f"linha {linha:<5} {classe:<8} {nome:<22} = \"{'*' * 8}\" ({n} caracteres)")
    senhas = [a for a in achados if a[2] == "SENHA"]
    usuarios = [a for a in achados if a[2] == "USUARIO"]
    print(f"\nSENHA: {len(senhas)}   USUARIO padrão: {len(usuarios)}")
    sys.exit(len(senhas))
