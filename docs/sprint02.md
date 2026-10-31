# Registro da Sprint 02 (12/10 a 25/10/2026)

Nenhuma atividade foi executada no período da sprint. A recuperação foi feita em 31/10/2026, no período da Sprint 03.

## Situação dos cards (31/10/2026)
| Card | Atividade | Situação | Evidência |
|---|---|---|---|
| Q04 | Ambiente de testes | Concluído em 31/10 | `testes/apoio.py` |
| Q05 | Testes T01–T03 | Executados em 31/10; em validação | `testes/test_t01..t03` |
| Q06 | Remover senhas do código | Corrigido numa cópia em 31/10; implantação e troca das senhas pendentes | `testes/test_t08_segredos.py`, `tools/busca_segredos.py` |
| Q07 | Desempenho da varredura (T04) | Não iniciado | – |

## Ambiente de testes (Q04)
- O Gerenciador é carregado de um caminho fora do repositório (`GERENCIADOR=...`); o código não é publicado.
- O tkinter é simulado: nenhuma janela abre. Ping, alerta e interface são simulados com `unittest.mock`.
- Dados fictícios: planilhas geradas no teste, IPs 192.0.2.0/24 (faixa de documentação), senhas de teste.
- Ferramentas: `unittest` (biblioteca padrão). O pytest/pytest-cov não pôde ser instalado no ambiente usado;
  a cobertura é medida por `tools/cobertura.py` (sys.settrace, cobertura de linhas).

```bash
GERENCIADOR=/caminho/gerenciador_onus.py python -m unittest discover -s testes -v
GERENCIADOR=/caminho/gerenciador_onus.py python tools/cobertura.py
python tools/busca_segredos.py /caminho/gerenciador_onus.py
python tools/metricas.py /caminho/gerenciador_onus.py
```

## Versões analisadas
| Arquivo | SHA-256 | Observação |
|---|---|---|
| Original (linha de base) | `1e83b5df…1765772` | Métricas idênticas às de 11/10 e 27/10 |
| Cópia com a correção Q06 | `ded3d902…fafa12b67` | 3 senhas retiradas + 2 proteções contra senha vazia |

## Resultados (31/10/2026)
| Teste | Casos | Original | Com Q06 | Defeito |
|---|---|---|---|---|
| T01 – planilha | 5 | 4 aprovados | 4 aprovados | DF07: serial duplicado sem aviso |
| T02 – status/queda | 6 | 2 aprovados | 2 aprovados | DF08: status OFFLINE e QUEDA no histórico já na 1ª falha; DF09: sem consulta à OLT, não distingue bloqueio de ping ou OLT inacessível |
| T03 – hash das senhas | 4 | 3 aprovados | 4 aprovados | sem senha configurada criava admin com senha vazia (corrigido no Q06) |
| T08 – segredos | 1 | reprovado (3 senhas) | aprovado (0) | – |
| **Total** | **16** | **9 / 16** | **11 / 16** | |

- Cobertura de linhas (MQ07), medida: 4,6% das funções críticas (32 de 692 linhas; `carregar_dados_excel` 82,1%).
  O "0%" da Sprint 1 não era medição: era a ausência de qualquer teste.
- Busca de segredos automatizada: **3 senhas** (linhas 25, 70 e 71) e 2 nomes de usuário padrão (24 e 564).
  A linha 564 é o **usuário** da OLT, não uma senha; a senha da OLT é pedida na hora e fica só na memória.
  A contagem de 4 senhas feita à mão em 27/10 estava errada (DF06).
- Regressão (T09) da correção Q06: os 9 casos aprovados no original continuam aprovados.

Verificação feita pelo próprio autor (autoverificação). A validação independente (outro técnico executando a suíte)
e a implantação da correção em produção ficam para a Sprint 03.
