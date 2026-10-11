# Plano de testes

| ID | Requisito | Tipo | Objetivo | Resultado esperado |
|---|---|---|---|---|
| T01 | RQ06/RQ07 | Unitário | Validar a leitura da planilha de ONUs (colunas ausentes, linhas vazias, serial duplicado) | Erros tratados e informados; nenhuma linha válida perdida |
| T02 | RQ01 | Unitário (mock) | Confirmar queda só após nova tentativa | ONU só fica "offline" após confirmação |
| T03 | RQ02 | Unitário | Verificar hash com salt das senhas do painel | Senha nunca armazenada em texto puro |
| T04 | RQ04 | Desempenho | Medir o tempo de um ciclo de varredura | Ciclo dentro da meta definida em MQ04 |
| T05 | RQ02/RQ05 | Funcional | Perfis admin/visualização no painel web | Perfil "view" não acessa funções administrativas |
| T06 | RQ05 | Usabilidade | Executar tarefas comuns com usuários da Gerência de TI | Tarefas concluídas sem ajuda; SUS ≥ 70 |
| T07 | RQ03 | Análise estática | Comparar métricas antes/depois da refatoração | CC máx. ≤ 20 nas funções críticas |
| T08 | RQ02 | Segurança | Buscar segredos no código e no histórico | 0 credenciais no código |
| T09 | Todos | Regressão | Reexecutar a suíte após cada mudança | 100% dos testes passando |

Ferramentas: pytest, pytest-cov, unittest.mock, `tools/metricas.py`, bandit, ruff.
