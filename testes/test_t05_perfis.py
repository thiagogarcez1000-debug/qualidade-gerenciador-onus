"""T05 – Perfis do painel web (RQ02 / MQ02): o perfil de visualização não acessa funções de administrador.
O servidor do painel sobe numa porta livre e é acessado por 127.0.0.1, com usuários e senhas fictícios."""
import http.client
import json
import os
import socket
import unittest
from unittest import mock

import apoio

M, PASTA = apoio.carregar()
ADMIN, VIEW = "teste-admin-789", "teste-view-012"


def porta_livre():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


class T05Perfis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        M.ARQUIVO_USUARIOS = os.path.join(PASTA, "usuarios_t05.json")
        M.PAINEL_SENHA, M.PAINEL_SENHA_VIEW, M.WEB_SENHA = ADMIN, VIEW, ""
        M.PAINEL_PORTA = cls.porta = porta_livre()
        app = mock.Mock()
        app.dados_onus = [{"nome": "UBS Teste", "ip": "192.0.2.70"}]
        app.reboot_em_andamento, app.senha_web = set(), None
        app.dados_painel.return_value = {"onus": [], "resumo": {"total": 0}}
        cls.srv = M.iniciar_painel(app)

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def pedir(self, metodo, caminho, corpo=None, cookie=None):
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5)
        cab = {"Content-Type": "application/json"}
        if cookie:
            cab["Cookie"] = cookie
        c.request(metodo, caminho, json.dumps(corpo) if corpo is not None else None, cab)
        r = c.getresponse(); dados = r.read(); c.close()
        return r.status, r.getheader("Set-Cookie", ""), dados

    def entrar(self, usuario, senha):
        st, ck, _ = self.pedir("POST", "/login", {"usuario": usuario, "senha": senha})
        return st, ck.split(";")[0]

    def test_sem_login_api_bloqueada(self):
        for rota in ("/api/onus", "/api/eu", "/api/historico"):
            self.assertEqual(self.pedir("GET", rota)[0], 401, rota)
        self.assertEqual(self.pedir("POST", "/api/reboot", {"ip": "192.0.2.70"})[0], 401)

    def test_admin_e_visualizacao_entram_com_o_perfil_certo(self):
        for usuario, senha, perfil in (("admin", ADMIN, "admin"), ("visualizacao", VIEW, "view")):
            st, ck = self.entrar(usuario, senha)
            self.assertEqual(st, 200)
            self.assertEqual(json.loads(self.pedir("GET", "/api/eu", cookie=ck)[2])["perfil"], perfil)

    def test_visualizacao_nao_reinicia_onu(self):
        _, ck = self.entrar("visualizacao", VIEW)
        self.assertEqual(self.pedir("POST", "/api/reboot", {"ip": "192.0.2.70"}, ck)[0], 403)

    def test_admin_chega_ao_reinicio(self):
        _, ck = self.entrar("admin", ADMIN)
        st, _, corpo = self.pedir("POST", "/api/reboot", {"ip": "192.0.2.70"}, ck)
        self.assertEqual(st, 200)               # sem senha da ONU configurada, o reinício é recusado com aviso
        self.assertIn("WEB_SENHA", json.loads(corpo)["erro"])

    def test_senha_errada_e_senha_vazia_recusadas(self):
        self.assertEqual(self.entrar("admin", "errada")[0], 401)
        self.assertEqual(self.entrar("", "")[0], 401, "login antigo aceitou senha vazia")


if __name__ == "__main__":
    unittest.main(verbosity=2)
