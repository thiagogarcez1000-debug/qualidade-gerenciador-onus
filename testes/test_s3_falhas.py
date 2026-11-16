"""Sprint 3 – Injeção de falhas (Q08 / RQ06 / MQ06, condição 2). Dados fictícios, rede simulada.
Cada falha injetada deve gerar (a) mensagem ao usuário e (b) registro em log com data e contexto."""
import os
import socket
import unittest
from unittest import mock

import pandas as pd

import apoio

M, PASTA = apoio.carregar()
LOG = os.path.join(PASTA, "log_erros.txt")
ITEM = {"nome": "UBS Teste", "ip": "192.0.2.60", "olt": "OLT 01", "gpon": 3, "id": 9}
CFG = {"OLTS": {"OLT 01": "192.0.2.1"}, "OLT_USUARIO": "teste", "OLT_PORTA": 23}


class ThreadSincrona:
    """Substitui threading.Thread: executa o alvo na hora, para o teste ver o resultado."""
    def __init__(self, target=None, args=(), daemon=None):
        self.alvo, self.args = target, args

    def start(self):
        self.alvo(*self.args)


def log():
    return open(LOG, encoding="utf-8").read() if os.path.exists(LOG) else ""


def app_teste():
    app = M.GerenciadorONUsApp.__new__(M.GerenciadorONUsApp)
    app.root = mock.Mock()
    app.root.after.side_effect = lambda _t, f: f()
    app.senha_olt = "senha-ficticia"
    app.carregar_vinculo_mapa = mock.Mock()
    return app


class S3Falhas(unittest.TestCase):
    def setUp(self):
        if os.path.exists(LOG):
            os.remove(LOG)
        M.ARQUIVO_LOG_ERROS = LOG
        self.msg = mock.patch.object(M, "messagebox").start()
        mock.patch.object(M.threading, "Thread", ThreadSincrona).start()
        self.addCleanup(mock.patch.stopall)

    def test_planilha_ausente_mensagem_e_log(self):
        app = app_teste(); app.excel_file = os.path.join(PASTA, "nao_existe.xlsx")
        app.carregar_dados_excel()
        self.msg.showerror.assert_called_once()
        self.assertIn("planilha", log(), "falha da planilha sem registro em log")

    def test_serial_duplicado_aviso_e_log(self):
        p = os.path.join(PASTA, "dup_s3.xlsx")
        pd.DataFrame([["UBS A", "192.0.2.30", "OLT 01", 1, 1, "FIOG0000DDDD"],
                      ["UBS B", "192.0.2.31", "OLT 01", 1, 2, "FIOG0000DDDD"],
                      ["UBS C", "192.0.2.32", "OLT 01", 1, 3, "FIOG0000EEEE"]],
                     columns=["91()", "IP ONU", "OLT", "GPON", "ID", "SERIAL ONU"]).to_excel(p, index=False)
        app = app_teste(); app.excel_file = p; app.carregar_dados_excel()
        self.assertEqual(len(app.dados_onus), 3, "linhas descartadas")
        self.msg.showwarning.assert_called_once()
        self.assertIn("FIOG0000DDDD", self.msg.showwarning.call_args.args[1])
        self.assertIn("serial duplicado", log())

    def test_timeout_de_rede_no_ping(self):
        """Ping que levanta exceção (ex.: timeout do processo) não pode sumir em silêncio."""
        with mock.patch.object(M, "ping_ip", side_effect=TimeoutError("ping excedeu 5 s")), \
             mock.patch.object(M, "carregar_provisionamento", return_value=CFG), \
             mock.patch.object(M, "SessaoOLT", side_effect=socket.timeout("timed out")):
            app_teste().testar_internet(dict(ITEM))
        texto = self.msg.showinfo.call_args.args[1]
        self.assertIn("SEM RESPOSTA", texto)
        self.assertIn("erro do sistema", texto, "usuário não é avisado de que o ping falhou por erro")
        self.assertIn("TimeoutError", log())

    def test_onu_ou_olt_inacessivel(self):
        with mock.patch.object(M, "ping_ip", return_value=False), \
             mock.patch.object(M, "carregar_provisionamento", return_value=CFG), \
             mock.patch.object(M, "SessaoOLT", side_effect=ConnectionRefusedError("recusado")):
            app_teste().testar_internet(dict(ITEM))
        texto = self.msg.showinfo.call_args.args[1]
        self.assertIn("OLT: não consultei", texto)
        self.assertIn("ConnectionRefusedError", log(), "falha de acesso à OLT sem registro em log")

    def test_configuracao_invalida_registrada(self):
        with mock.patch.object(M, "ping_ip", return_value=True), \
             mock.patch.object(M, "carregar_provisionamento", side_effect=ValueError("JSON inválido")):
            app_teste().testar_internet(dict(ITEM))
        self.msg.showinfo.assert_called_once()
        self.assertIn("provisionamento.json", log(), "erro de configuração descartado em silêncio")


if __name__ == "__main__":
    unittest.main(verbosity=2)
