"""Sprint 3 – Regra de confirmação da queda (Q13 / DF08 / RQ01). Ping simulado, dados fictícios."""
import unittest
from unittest import mock

import apoio
from test_t02_status import M, eventos, nova_app


def varrer_em(app, respostas, inicio=1000.0, passo=60.0):
    """Uma varredura por resposta, com relógio simulado (1 varredura a cada 60 s)."""
    with mock.patch.object(M, "threading"):
        for k, r in enumerate(respostas):
            with mock.patch.object(M, "ping_ip", return_value=r), \
                 mock.patch.object(M.time, "time", return_value=inicio + k * passo):
                app.testar_todos_pings()


class S3Confirmacao(unittest.TestCase):
    def test_queda_confirmada_registra_inicio_da_primeira_falha(self):
        app = nova_app(); varrer_em(app, [True, False, False])
        q = eventos(app, "QUEDA")
        self.assertEqual(len(q), 1)
        self.assertEqual(q[0].args[2], 1060.0, "início da queda deveria ser o da 1ª falha")
        self.assertEqual(app.dados_onus[0]["status"], "OFFLINE")

    def test_aviso_de_queda_uma_vez_na_confirmacao(self):
        app = nova_app(); varrer_em(app, [True, False, False, False])
        self.assertEqual(app.notificar_queda.call_count, 1)

    def test_volta_registrada_depois_de_queda_confirmada(self):
        app = nova_app(); varrer_em(app, [True, False, False, True])
        self.assertEqual(len(eventos(app, "VOLTA")), 1)
        self.assertEqual(app.dados_onus[0]["status"], "ONLINE")

    def test_ponto_ja_parado_no_inicio(self):
        """Na abertura do programa, 1 falha mostra 'verificando'; a 2ª confirma, marcando horário aproximado."""
        app = nova_app(); varrer_em(app, [False])
        self.assertEqual(app.dados_onus[0]["status"], "PENDENTE")
        varrer_em(app, [False], inicio=1060.0)
        self.assertEqual(app.dados_onus[0]["status"], "OFFLINE")
        self.assertIn("já estava parada", eventos(app, "QUEDA")[0].args[3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
