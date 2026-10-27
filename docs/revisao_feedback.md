# Revisão do plano após o feedback da Proposta (27/10/2026)

## Metas das métricas – fundamentação
| Métrica | Meta | Fundamento |
|---|---|---|
| MQ01 – alertas corretos | ≥ 95% | Meta inicial definida no planejamento: até 1 alarme falso a cada 20 avisos. Será confirmada com a amostra da Sprint 2 (linha de base ainda não medida). |
| MQ03 – complexidade máxima | CC ≤ 20 nas funções críticas | McCabe recomenda 10; ferramentas como o radon classificam 11–20 como "moderada" e acima de 20 como "alta". Partindo de funções com CC 29 a 105, ≤ 20 é um alvo alcançável em uma sprint de refatoração. |
| MQ05 – usabilidade | SUS ≥ 70 | A média de referência do SUS é 68; 70 indica usabilidade acima da média. |
| MQ07 – cobertura | ≥ 70% nas funções críticas | Patamar usual de cobertura mínima; aplicado só às funções críticas, porque a interface Tkinter é difícil de testar automaticamente. Validação pendente na Sprint 2. |

Funções críticas (MQ03, MQ06, MQ07): `carregar_dados_excel`, `testar_internet`, `diagnosticar`, `renderizar_cards` (definição do status exibido), `iniciar_painel` (login e perfis) e `abrir_provisionamento`.

## Critérios completados
- **MQ02 (RQ02):** duas condições. (1) Nenhuma credencial em texto no código (busca de segredos + bandit). (2) Senhas dos usuários do painel guardadas só como hash com salt (teste T03: inspecionar o arquivo de usuários e confirmar que o login funciona com o hash).
- **MQ06 (RQ06):** além de zerar `except: pass` nas funções críticas, injetar falhas (planilha ausente, timeout de rede, ONU inacessível) e verificar que cada uma gera **mensagem ao usuário e linha no log**.

## Riscos (renomeados)
- RS01 (antigo PQ05) – falso "offline" em equipamento que não responde ao ping. É um **relato da equipe ainda não confirmado**; o risco é a consequência (alarme e deslocamento desnecessários).
- RS02 (antigo PQ06) – uma correção quebrar a ferramenta em produção.

## T02 revisado – distinguir "não responde ao ping" de "fora do ar"
| Cenário (simulado com mock) | Confirmação | Resultado esperado |
|---|---|---|
| Falha transitória (1 ping perdido) | nova tentativa | continua online |
| ONU ativa que bloqueia ICMP | consulta somente leitura ao estado da ONU na OLT (autorizada) | "sem confirmação / ativa na OLT", não offline |
| Queda real | sem ping e OLT indicando ONU desconectada | offline confirmado |
| OLT inacessível | sem ping e sem resposta da OLT | "sem confirmação", com aviso |

## Inspeção realizada x planejada
- **Realizado na Sprint 1 (10–11/10):** linha de base estática (T07 – primeira medição) e busca manual de credenciais (T08 – primeira busca).
- **Planejado:** T01 a T06, T09 e as reavaliações de T07 e T08 após as correções.
