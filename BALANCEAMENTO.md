# Balanceamento e evidências

Versão anual (1998–2021): **42 testes passaram**, **600 campanhas** com seis estratégias, seeds 1000–1599.

| Estratégia | Campanhas | Lucro anual médio | Participação final | Falência |
|---|---:|---:|---:|---:|
| aleatorio | 100 | R$ 4465.13 | 8.66% | 0% |
| caos | 100 | R$ 10167.48 | 20.59% | 0% |
| conservador | 100 | R$ 17505.74 | 22.77% | 0% |
| expansao | 100 | R$ 25306.44 | 33.96% | 0% |
| pesquisa | 100 | R$ 17924.80 | 29.54% | 0% |
| precos | 100 | R$ 21174.88 | 41.83% | 0% |

## Finais observados

| Final | Campanhas |
|---|---:|
| O GRANDE MAGNATA | 130 |
| O CHICLETE DO POVO | 102 |
| A REPÚBLICA DEMOCRÁTICA DA GOMA | 44 |
| O SABOR DEFINITIVO | 56 |
| FEDERAÇÃO DAS FÁBRICAS AMBULANTES | 10 |
| A FIRMA QUE SE RECUSOU A ACABAR | 197 |
| IMPERADOR DA PLUTONITA | 45 |
| MUTAÇÃO GLOBAL | 15 |
| A SAGRADA ORDEM DA BOLHA | 1 |

Todos os **53 eventos** apareceram na bateria. Os cenários dirigidos completam os 11 finais: falência na seed 1, turno 18 (2015), e antitruste na seed 1000 ao final de 2021.

A sazonalidade de demanda foi agregada em 1,03 por ano; o Halloween oferece +9,2% de atratividade anual para Cabeça de Abóbora. Os limites de produção, caixa finito dos rivais e custos únicos de investimento continuam auditados.

A falência foi 0% entre os agentes, que filtram gastos impossíveis. Um cenário deliberado de excesso industrial demonstra insolvência. Preços baixos lideram participação média; expansão lidera lucro. Sobreviver é mais fácil que dominar: 45 das 600 campanhas chegaram ao final imperial.

## Evidências

- [42 testes](reports/tests.txt), incluindo menus, limpeza de tela, saves, seeds e campanha completa.
- [600 campanhas](reports/simulation_600.json): capacidade, vendas, receita, caixa e participação auditados.
- [Cenários dirigidos](reports/targeted_scenarios.json).

## Limitações

A meta de cerca de 10–15 minutos não foi validada em teste humano cronometrado. As simulações verificam execução e consistência, não diversão. Validação manual em Windows/Linux continua pendente. Os campos JSON com nomes mensais são mantidos por compatibilidade, mas representam turnos anuais nesta versão.
