"""T03 – Senhas do painel guardadas só como hash com salt (RQ02 / MQ02, condição 2).
Senhas fictícias, criadas só para o teste."""
import json
import os
import unittest

import apoio

M, PASTA = apoio.carregar()
ADMIN, VIEW = "teste-admin-123", "teste-view-456"


class T03Senhas(unittest.TestCase):
    def setUp(self):
        self.arq = os.path.join(PASTA, f"usuarios_{self._testMethodName}.json")
        M.ARQUIVO_USUARIOS = self.arq
        M.PAINEL_SENHA, M.PAINEL_SENHA_VIEW = ADMIN, VIEW

    def test_arquivo_nao_tem_senha_em_texto(self):
        M.carregar_usuarios()
        with open(self.arq, encoding="utf-8") as f:
            texto = f.read()
        self.assertNotIn(ADMIN, texto)
        self.assertNotIn(VIEW, texto)
        u = json.loads(texto)["usuarios"]["admin"]
        self.assertEqual(len(u["hash"]), 64)            # PBKDF2-SHA256 em hexadecimal
        self.assertEqual(len(u["salt"]), 32)

    def test_salt_diferente_por_usuario(self):
        u = M.carregar_usuarios()["usuarios"]
        self.assertNotEqual(u["admin"]["salt"], u["visualizacao"]["salt"])

    def test_login_com_hash(self):
        M.carregar_usuarios()
        self.assertEqual(M.verificar_usuario("admin", ADMIN), "admin")
        self.assertEqual(M.verificar_usuario("visualizacao", VIEW), "view")
        self.assertIsNone(M.verificar_usuario("admin", "errada"))
        self.assertIsNone(M.verificar_usuario("visualizacao", ADMIN))

    def test_sem_senha_configurada_nao_cria_admin_sem_senha(self):
        """Depois de tirar a senha do código (Q06), a falta de configuração não pode abrir o painel."""
        M.PAINEL_SENHA, M.PAINEL_SENHA_VIEW = "", ""
        M.carregar_usuarios()
        self.assertIsNone(M.verificar_usuario("admin", ""), "admin criado com senha vazia")


if __name__ == "__main__":
    unittest.main(verbosity=2)
