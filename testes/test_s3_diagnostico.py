"""Sprint 3 – Diagnóstico do trecho provável da falha (função crítica 'diagnosticar', RQ01/RQ07).
Rotas fictícias: OLT X -> cabo C1 -> caixa CX1 -> cabo C2 -> caixa CX2."""
import unittest

import apoio

M, PASTA = apoio.carregar()


def rota(ate_cx2=True):
    passos = [("cabo", "C1", "", "C1"), ("caixa", "CX1")]
    if ate_cx2:
        passos += [("cabo", "C2", "", "C2"), ("caixa", "CX2")]
    return {"olt": "OLT X", "passos": passos, "marcas": []}


def app_com(status):
    app = M.GerenciadorONUsApp.__new__(M.GerenciadorONUsApp)
    app.dados_onus = [{"nome": f"P{i}", "ip": f"192.0.2.{i}", "status": s} for i, s in enumerate(status)]
    app.rotas = {}
    return app


class S3Diagnostico(unittest.TestCase):
    def test_queda_em_grupo_aponta_o_cabo(self):
        app = app_com(["ONLINE", "OFFLINE", "OFFLINE"])
        app.rotas = {"192.0.2.0": rota(False), "192.0.2.1": rota(), "192.0.2.2": rota()}
        d = app.diagnosticar()
        self.assertEqual(d[0]["tipo"], "cabo")
        self.assertEqual(d[0]["qtd"], 2)
        self.assertIn("C2", d[0]["texto"])

    def test_olt_inteira_fora(self):
        app = app_com(["OFFLINE", "OFFLINE"])
        app.rotas = {"192.0.2.0": rota(), "192.0.2.1": rota()}
        self.assertEqual(app.diagnosticar()[0]["tipo"], "olt")

    def test_queda_isolada(self):
        app = app_com(["ONLINE", "OFFLINE"])
        app.rotas = {"192.0.2.0": rota(False), "192.0.2.1": rota()}
        self.assertEqual(app.diagnosticar()[0]["tipo"], "isolada")

    def test_problema_local_com_rota_boa(self):
        app = app_com(["ONLINE", "OFFLINE"])
        app.rotas = {"192.0.2.0": rota(), "192.0.2.1": rota()}
        self.assertEqual(app.diagnosticar()[0]["tipo"], "local")

    def test_sem_rota_nao_gera_diagnostico(self):
        app = app_com(["OFFLINE"])
        self.assertEqual(app.diagnosticar(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
