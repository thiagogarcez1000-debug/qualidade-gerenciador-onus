"""T08 – Nenhuma senha em texto no código (RQ02 / MQ02, condição 1)."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import apoio            # noqa: E402
import busca_segredos   # noqa: E402


class T08Segredos(unittest.TestCase):
    def test_nenhuma_senha_no_codigo(self):
        caminho = os.environ.get("GERENCIADOR", str(apoio.PADRAO))
        senhas = [a for a in busca_segredos.buscar(caminho) if a[2] == "SENHA"]
        self.assertEqual(senhas, [], f"{len(senhas)} senha(s) em texto: linhas {[a[0] for a in senhas]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
