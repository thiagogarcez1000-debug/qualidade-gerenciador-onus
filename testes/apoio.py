"""Ambiente de testes isolado (card Q04).

- Carrega o Gerenciador de ONUs a partir do caminho em GERENCIADOR (variável de ambiente);
  o código não fica neste repositório público.
- Substitui o tkinter por objetos simulados: nenhuma janela é aberta.
- Cada teste roda numa pasta temporária, com dados fictícios (IPs da faixa de documentação
  192.0.2.0/24, RFC 5737). Nenhum teste acessa a rede, a planilha real ou as OLTs.
"""
import importlib.util
import os
import sys
import tempfile
import types
from pathlib import Path
from unittest import mock

PADRAO = Path(__file__).resolve().parents[2] / "gerenciador" / "gerenciador_onus.py"


def _tk_simulado():
    tk = types.ModuleType("tkinter")
    for nome in ("Tk", "Toplevel", "Frame", "Label", "Button", "Entry", "Canvas", "Scrollbar",
                 "StringVar", "IntVar", "BooleanVar", "Text", "Listbox", "Menu", "PhotoImage"):
        setattr(tk, nome, mock.MagicMock(name=nome))
    tk.END, tk.BOTH, tk.X, tk.Y, tk.LEFT, tk.RIGHT, tk.W, tk.E = "end", "both", "x", "y", "left", "right", "w", "e"
    for sub in ("ttk", "messagebox", "simpledialog", "filedialog"):
        m = mock.MagicMock(name=sub)
        setattr(tk, sub, m)
        sys.modules["tkinter." + sub] = m
    sys.modules["tkinter"] = tk


def carregar(caminho=None):
    """Importa o arquivo do Gerenciador como módulo isolado e devolve (modulo, pasta_temporaria)."""
    caminho = Path(caminho or os.environ.get("GERENCIADOR", PADRAO))
    if not caminho.exists():
        raise FileNotFoundError(f"Defina GERENCIADOR com o caminho do arquivo do Gerenciador ({caminho})")
    _tk_simulado()
    pasta = tempfile.mkdtemp(prefix="teste_onus_")
    os.chdir(pasta)                      # arquivos de usuários, estado e histórico vão para a pasta temporária
    spec = importlib.util.spec_from_file_location("gerenciador_onus", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo, pasta
