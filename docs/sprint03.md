# Registro da Sprint 03 (26/10 a 08/11/2026)

Nenhuma atividade foi executada no período da sprint. A execução foi feita em **15/11/2026**, no período da Sprint 04.

## Versões analisadas
| Arquivo | SHA-256 | Observação |
|---|---|---|
| Original (linha de base) | `1e83b5df…1765772` | O mesmo de 11/10, 27/10 e 31/10; métricas idênticas |
| Cópia corrigida da Sprint 3 | `144c25ff…2e3b0d3c6` | Gerada por `tools/aplicar_s3.py` a partir do original |

A cópia corrigida de 31/10 (`ded3d902…`) não foi localizada no computador da TI. A correção Q06 foi
**reaplicada** sobre o original pelo script `tools/aplicar_s3.py`, que deixa cada alteração registrada e
pode ser reexecutado. T03 e T08 foram repetidos nela.

## O que mudou na cópia corrigida
| Card | Defeito / problema | Alteração | Verificação |
|---|---|---|---|
| Q06 | PQ01, DF10 | 3 senhas fora do código (vêm do config.json); sem senha configurada não se cria administrador; senha vazia recusada | T08: 0 senhas; T03 4/4; T05 5/5 |
| Q13 | DF07 | Serial repetido gera aviso e registro em log; nenhuma linha é descartada | T01 5/5; test_s3_falhas |
| Q13 | DF08 | Status e QUEDA só mudam após `CONFIRMAR_QUEDA_VARREDURAS` falhas seguidas (a mesma regra do alerta); o início da queda é o da 1ª falha | T02 4/6; test_s3_confirmacao 4/4 |
| Q13 | DF09 | **Não corrigido.** Recomendação técnica abaixo | T02: 2 casos continuam falhando |
| Q08 | PQ02 | `registrar_erro()` grava em `log_erros.txt`; os 5 `except: pass` das funções críticas e as falhas de planilha, configuração, ping e OLT passam a ser registradas | test_s3_falhas 5/5 |

### DF09 – recomendação (não implementada nesta sprint)
O código já tem uma consulta somente leitura à OLT (`show onu interface gponX onu Y`, usada no teste de internet).
Recomendo usá-la para confirmar a queda: depois de 2 varreduras sem ping, consultar o *Link Status* da ONU na OLT;
`down/inactive` → OFFLINE confirmado; `up/active` → "sem ping, ativa na OLT"; OLT sem resposta → "sem confirmação".
Não implementei porque: (1) o formato real da saída precisa ser conferido numa OLT, fora do ambiente isolado;
(2) a consulta abre uma sessão Telnet por ONU, e com ~580 pontos precisa ser feita em lote e só para os pontos em
suspeita, para não atrasar a varredura; (3) o novo status muda telas, contadores e o painel web; (4) a ocorrência
real (RS01) ainda não foi confirmada em campo. Fica para a Sprint 4, com teste na OLT de bancada.

## Resultados (15/11/2026) – `python -m unittest discover -s testes`
| Conjunto | Casos | Original | Corrigido S3 |
|---|---|---|---|
| T01 planilha | 5 | 4 | 5 |
| T02 status/queda | 6 | 2 | 4 |
| T03 hash das senhas | 4 | 3 | 4 |
| T08 segredos | 1 | 0 | 1 |
| **Subtotal (suíte da Sprint 2)** | **16** | **9** | **14** |
| T05 perfis do painel (novo) | 5 | 5 | 5 |
| S3 injeção de falhas – Q08 (novo) | 5 | 0 | 5 |
| S3 confirmação da queda – DF08 (novo) | 4 | 3 | 4 |
| S3 diagnóstico (novo) | 5 | 5 | 5 |
| **Total** | **35** | **22** | **33** |

Regressão (T09): todos os 22 casos aprovados no original continuam aprovados na cópia corrigida.

### Cobertura das funções críticas (MQ07, `tools/cobertura.py`)
| Função | 31/10 | 15/11 (corrigido) |
|---|---|---|
| carregar_dados_excel | 82,1% | 85,7% |
| testar_internet | 0% | 66,7% |
| diagnosticar | 0% | 96,6% |
| iniciar_painel | 0% | 55,4% |
| renderizar_cards | 0% | 0% |
| abrir_provisionamento | 0% | 0% |
| **Total** | **4,6%** | **30,7%** (217 de 707 linhas) |

Caminhos críticos ainda descobertos: `abrir_provisionamento` (312 linhas, 44% das linhas críticas) e
`renderizar_cards` (88), ambas presas à interface Tkinter e, no provisionamento, à OLT. Para testá-las é preciso
separar a lógica da tela (Q09) e usar a OLT de bancada.

### T04 em ambiente simulado (`tools/desempenho_sim.py`)
580 pontos fictícios, ping simulado (88% respondem em 2–40 ms; o resto espera o timeout de 1 s), 40 threads, 10 ciclos.
| Cenário | Original | Corrigido S3 |
|---|---|---|
| Normal (12% sem resposta) | média 2,42 s (2,25–3,03) | média 2,42 s (2,25–3,03) |
| OLT inteira fora (100% sem resposta) | 15,01 s | 15,01 s |

Os dois cenários cabem no intervalo padrão de 60 s; a varredura roda numa thread separada (`iniciar_varredura_thread`).
**Limite:** não mede a rede real nem o custo do processo `ping` do Windows. O T04 na rede real continua pendente.

### Métricas estáticas (T07, `tools/metricas.py`)
| Métrica | Original | Corrigido S3 |
|---|---|---|
| except: pass (arquivo) | 29 | 22 |
| except: pass (funções críticas) | 5 | 0 |
| Senhas no código | 3 | 0 |
| CC máxima das funções críticas | 105 | 105 (sem refatoração) |

Verificação feita pelo próprio autor (autoverificação). Validação independente, implantação no computador da TI,
troca das senhas em uso, T04 na rede real, DF09 e Q09/Q10 ficam para a Sprint 04.
