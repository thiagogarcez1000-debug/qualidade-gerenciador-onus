"""T01 – Leitura da planilha de ONUs (RQ06, RQ07 / MQ06, MQ07). Dados fictícios."""
import os
import unittest
from unittest import mock

import pandas as pd

import apoio

M, PASTA = apoio.carregar()
COLUNAS = ["91()", "IP ONU", "OLT", "GPON", "ID", "SERIAL ONU"]


def app_com(caminho):
    app = M.GerenciadorONUsApp.__new__(M.GerenciadorONUsApp)
    app.excel_file = caminho
    app.carregar_vinculo_mapa = mock.Mock()
    return app


def planilha(nome, linhas, colunas=COLUNAS):
    caminho = os.path.join(PASTA, nome)
    pd.DataFrame(linhas, columns=colunas).to_excel(caminho, index=False)
    return caminho


class T01Planilha(unittest.TestCase):
    def setUp(self):
        self.msg = mock.patch.object(M, "messagebox").start()
        self.addCleanup(mock.patch.stopall)

    def test_planilha_valida(self):
        p = planilha("valida.xlsx", [["UBS Teste", "192.0.2.10", "OLT 01", 1, 5, "fiog0000aaaa"],
                                     ["Escola Teste", "192.0.2.11", "OLT 02", 2, 7, "FIOG0000BBBB"]])
        app = app_com(p); app.carregar_dados_excel()
        self.assertEqual(len(app.dados_onus), 2)
        self.assertEqual(app.dados_onus[0]["serial"], "FIOG0000AAAA")   # serial padronizado em maiúsculas
        self.assertEqual(app.dados_onus[1]["gpon"], 2)
        self.msg.showerror.assert_not_called()

    def test_linha_sem_ip_e_ignorada_sem_perder_validas(self):
        p = planilha("vazias.xlsx", [["UBS A", "192.0.2.20", "OLT 01", 1, 1, "S1"],
                                     ["Sem IP", None, "OLT 01", 1, 2, "S2"],
                                     [None, None, None, None, None, None],
                                     ["UBS B", "192.0.2.21", "OLT 01", 1, 3, "S3"]])
        app = app_com(p); app.carregar_dados_excel()
        self.assertEqual([o["ip"] for o in app.dados_onus], ["192.0.2.20", "192.0.2.21"])

    def test_coluna_ip_ausente_e_informada(self):
        p = planilha("sem_ip.xlsx", [["UBS A", "OLT 01", 1, 1, "S1"]],
                     colunas=["91()", "OLT", "GPON", "ID", "SERIAL ONU"])
        app = app_com(p); app.carregar_dados_excel()
        self.msg.showerror.assert_called_once()
        self.assertEqual(app.dados_onus, [])

    def test_arquivo_ausente_e_informado(self):
        app = app_com(os.path.join(PASTA, "nao_existe.xlsx")); app.carregar_dados_excel()
        self.msg.showerror.assert_called_once()

    def test_serial_duplicado_e_informado(self):
        """Esperado pelo plano: serial duplicado gera aviso ao usuário."""
        p = planilha("duplicado.xlsx", [["UBS A", "192.0.2.30", "OLT 01", 1, 1, "FIOG0000DDDD"],
                                        ["UBS B", "192.0.2.31", "OLT 01", 1, 2, "FIOG0000DDDD"]])
        app = app_com(p); app.carregar_dados_excel()
        avisos = self.msg.showwarning.call_count + self.msg.showerror.call_count
        self.assertGreater(avisos, 0, "DF07: serial duplicado carregado sem nenhum aviso")


if __name__ == "__main__":
    unittest.main(verbosity=2)
