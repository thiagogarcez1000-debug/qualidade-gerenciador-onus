"""T04 em ambiente SIMULADO (Q07) – versão 1.0 (15/11/2026).

Mede o tempo de um ciclo completo de testar_todos_pings com 580 pontos fictícios e ping simulado.
NÃO mede a rede real: o tempo do processo 'ping' do Windows e a latência real da rede GPON não
entram. Serve para verificar a capacidade da varredura (40 threads) e comparar versões do código.

Cenários (10 ciclos cada):
  normal  – 88% respondem em 2 a 40 ms; 12% sem resposta, esperando o timeout de 1 s do ping
  queda   – OLT inteira fora: 100% esperam o timeout de 1 s (pior caso)
Uso: GERENCIADOR=arquivo.py python tools/desempenho_sim.py
"""
import os
import random
import statistics
import sys
import time
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "testes"))
import apoio  # noqa: E402

M, _ = apoio.carregar()
N, CICLOS, TIMEOUT = 580, 10, 1.0


def ping_simulado(prob_resposta, rnd):
    def ping(ip):
        if rnd.random() < prob_resposta:
            time.sleep(rnd.uniform(0.002, 0.040)); return True
        time.sleep(TIMEOUT); return False
    return ping


def app():
    a = M.GerenciadorONUsApp.__new__(M.GerenciadorONUsApp)
    a.dados_onus = [{"nome": f"P{i}", "ip": f"192.0.2.{i % 254 + 1}#{i}", "olt": "OLT 01", "gpon": 1,
                     "id": i, "serial": "S", "status": "PENDENTE", "cto": "", "lat": None, "lon": None}
                    for i in range(N)]
    a.status_antigo, a.offline_desde, a.ultimo_ok, a.falhas = {}, {}, {}, {}
    a.offline_aprox, a.alertado, a.ultima_varredura, a.rotas = set(), set(), None, {}
    for f in ("registrar_evento", "notificar_queda", "salvar_estado", "montar_alerta",
              "enviar_alerta", "atualizar_resumo", "renderizar_cards"):
        setattr(a, f, mock.Mock())
    a.root = mock.Mock()
    return a


def medir(nome, prob):
    rnd = random.Random(2026)
    a, tempos = app(), []
    with mock.patch.object(M, "ping_ip", ping_simulado(prob, rnd)), mock.patch.object(M, "threading"):
        for _ in range(CICLOS):
            t0 = time.perf_counter(); a.testar_todos_pings(); tempos.append(time.perf_counter() - t0)
    print(f"{nome:<7} ciclos={CICLOS} media={statistics.mean(tempos):.2f}s min={min(tempos):.2f}s "
          f"max={max(tempos):.2f}s  [{', '.join(f'{t:.2f}' for t in tempos)}]")


if __name__ == "__main__":
    print(f"T04 simulado – {N} pontos, 40 threads, timeout {TIMEOUT:.0f} s – arquivo {os.environ.get('GERENCIADOR')}")
    medir("normal", 0.88)
    medir("queda", 0.0)
