"""T02 – Status exibido x confirmação da queda (RQ01 / MQ01), com ping simulado.
Cenários do T02 revisado (docs/revisao_feedback.md)."""
import unittest
from unittest import mock

import apoio

M, PASTA = apoio.carregar()
IP = "192.0.2.50"


def nova_app():
    app = M.GerenciadorONUsApp.__new__(M.GerenciadorONUsApp)
    app.dados_onus = [{"nome": "UBS Teste", "ip": IP, "olt": "OLT 01", "gpon": 1, "id": 1,
                       "serial": "S", "status": "PENDENTE", "cto": "", "lat": None, "lon": None}]
    app.status_antigo, app.offline_desde, app.ultimo_ok, app.falhas = {}, {}, {}, {}
    app.offline_aprox, app.alertado = set(), set()
    app.ultima_varredura = None
    for f in ("registrar_evento", "notificar_queda", "diagnosticar", "salvar_estado",
              "montar_alerta", "enviar_alerta", "atualizar_resumo", "renderizar_cards"):
        setattr(app, f, mock.Mock())
    app.root = mock.Mock()
    return app


def varrer(app, respostas):
    """Executa uma varredura por item de 'respostas' (True = respondeu ao ping)."""
    with mock.patch.object(M, "threading") as th:      # só a thread do alerta é simulada
        for r in respostas:
            with mock.patch.object(M, "ping_ip", return_value=r):
                app.testar_todos_pings()
    return th.Thread


def eventos(app, tipo):
    return [c for c in app.registrar_evento.call_args_list if c.args[0] == tipo]


class T02Status(unittest.TestCase):
    def test_falha_transitoria_nao_gera_alerta(self):
        app = nova_app(); thread = varrer(app, [True, False, True])
        thread.assert_not_called()                      # WhatsApp só após 2 varreduras sem resposta

    def test_falha_transitoria_mantem_status_online(self):
        """Esperado: 1 ping perdido não muda o status exibido nem registra queda no histórico."""
        app = nova_app(); varrer(app, [True, False])
        self.assertEqual(app.dados_onus[0]["status"], "ONLINE", "DF08: status vira OFFLINE na 1ª falha")

    def test_falha_transitoria_nao_registra_queda(self):
        app = nova_app(); varrer(app, [True, False, True])
        self.assertEqual(eventos(app, "QUEDA"), [], "DF08: QUEDA gravada no histórico após 1 falha")

    def test_queda_real_alerta_uma_vez(self):
        app = nova_app(); thread = varrer(app, [True, False, False, False])
        self.assertEqual(thread.call_count, 1)          # um alerta, na 2ª varredura sem resposta
        self.assertEqual(app.dados_onus[0]["status"], "OFFLINE")

    def test_onu_ativa_que_bloqueia_icmp(self):
        """Esperado: 'sem confirmação / ativa na OLT', não OFFLINE (exige consulta à OLT)."""
        app = nova_app(); varrer(app, [False, False])
        self.assertNotEqual(app.dados_onus[0]["status"], "OFFLINE",
                            "DF09: sem confirmação pela OLT, ONU que bloqueia ping aparece OFFLINE")

    def test_olt_inacessivel(self):
        """Esperado: sem ping e sem resposta da OLT = 'sem confirmação', com aviso, não OFFLINE."""
        app = nova_app(); varrer(app, [False, False])
        self.assertNotEqual(app.dados_onus[0]["status"], "OFFLINE",
                            "DF09: o software não consulta a OLT, então não distingue OLT inacessível")


if __name__ == "__main__":
    unittest.main(verbosity=2)
