# Diagnóstico inicial da qualidade (linha de base – Sprint 01)

Medição estática feita em 10/10/2026 com `tools/metricas.py` sobre o arquivo principal `gerenciador_onus.py`.

| Indicador | Valor medido |
|---|---|
| Linhas do arquivo | 3.780 |
| Funções / classes | 172 / 4 |
| Complexidade ciclomática média | 8,6 |
| Funções com CC > 10 | 40 |
| Funções com CC > 20 | 20 |
| Maior função | `abrir_provisionamento` – 410 linhas, CC ≈ 105 |
| Funções com mais de 50 / 100 linhas | 25 / 9 |
| Blocos `except` | 92 (67 genéricos, 29 `except: pass`) |
| Funções com docstring | 30 de 172 |
| Atribuições globais | 48 |
| Linhas com mais de 120 caracteres | 86 |
| Testes automatizados | nenhum |
| Credenciais padrão no código | 3 ocorrências (valores omitidos) |

## Funções de maior complexidade
| Função | CC |
|---|---|
| abrir_provisionamento | 105 |
| iniciar_painel | 56 |
| gerar_relatorio_metragem | 41 |
| testar_internet | 40 |
| renderizar_cards | 34 |
| diagnosticar | 34 |
| procurar | 31 |
| abrir_usuarios | 30 |
| abrir_alterar_velocidade | 30 |
| carregar_dados_excel | 29 |

## Principais achados
- **PQ01** – senhas padrão escritas no código-fonte.
- **PQ02** – 29 blocos `except: pass` escondem falhas de rede e de leitura de planilha.
- **PQ03** – funções muito grandes e complexas dificultam manutenção.
- **PQ04** – ausência de testes automatizados.
- **PQ05** – risco de falso "offline" quando a ONU não responde ao ICMP.
- **PQ06** – risco de alterações quebrarem a ferramenta em produção.
