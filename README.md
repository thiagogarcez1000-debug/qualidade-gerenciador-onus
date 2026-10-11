# Qualidade – Gerenciador de ONUs Furukawa

Projeto de extensão da disciplina **Qualidade de Software Aplicada** (UniEVANGÉLICA – EAD, 2026/2).

**Autor:** Thiago José da Silva Garcez (D2510495)
**Instituição parceira:** Prefeitura Municipal de Anápolis – Gerência de TI
**Orientadora:** Profª. Dra. Natasha Sophie Pereira

## Objetivo
Avaliar e melhorar a qualidade do *Gerenciador de ONUs Furukawa*, ferramenta desktop (Python/Tkinter + painel web)
usada pela Gerência de TI para acompanhar e provisionar as ONUs da rede GPON municipal. O foco está em
confiabilidade do status das ONUs, segurança de credenciais, manutenibilidade, tratamento de erros e testabilidade
(ISO/IEC 25010).

## Estrutura
| Pasta | Conteúdo |
|---|---|
| `docs/` | Diagnóstico inicial, plano de testes e registros das sprints |
| `tools/` | Script de métricas estáticas (complexidade ciclomática, tamanho de funções, `except: pass`) |
| `tests/` | Testes automatizados (a partir da Sprint 02) |

> O código-fonte do software avaliado **não** é versionado neste repositório público enquanto houver
> credenciais embutidas (problema PQ01). Planilhas, KMZ e arquivos de configuração também ficam fora (`.gitignore`).

## Sprints
| Sprint | Período | Foco |
|---|---|---|
| 01 | 28/09 – 11/10/2026 | Diagnóstico, métricas de base e plano de testes |
| 02 | 12/10 – 25/10/2026 | Testes automatizados das funções críticas e remoção de senhas do código |
| 03 | 26/10 – 08/11/2026 | Refatoração das funções de maior complexidade e tratamento de erros |
| 04 | 09/11 – 22/11/2026 | Regressão, desempenho, usabilidade e relatório final |

Quadro Kanban: https://trello.com/b/o67053ka
