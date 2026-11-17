# Progresso — PLUTONITA: WORLD DOMINATION

Implementação concluída em 16/11/2026. Pasta inicialmente vazia, sem repositório Git; não havia alterações anteriores. O Git local foi inicializado posteriormente para preparar a publicação autorizada.

## Etapas

- [x] **1 — Fundação:** pacote Python, dataclasses, seed, ciclo de 24 meses, interface inicial e JSON atômico. Validação de avanço e round-trip do save realizada antes de ampliar o motor.
- [x] **2 — Economia:** oito mercados, produção limitada, demanda por atratividade, redistribuição, precificação, prioridades, marketing, expansão e relatórios. Testes de capacidade, caixa, investimento único e ações inválidas passaram.
- [x] **3 — Concorrentes e sabores:** três agentes com recursos próprios, sete clássicos, pesquisa acumulada, laboratório, oito nomes experimentais, três linhas ativas e combinações especiais.
- [x] **4 — Narrativa:** 53 eventos grandes, 60 notícias, quatro histórias em capítulos, consequências agendadas, condições, flags, Caos e conteúdo de fim de campanha.
- [x] **5 — Finais e progressão:** 11 finais com prioridade determinística, 20 conquistas, cosméticos, histórico, estatísticas e perfil idempotente.
- [x] **6 — Refinamento:** interface Rich completa em português, confirmações, entradas inválidas, relatório de riscos, validação de saves, documentação, 35 testes, 600 campanhas finais e dois cenários dirigidos.

Os arquivos foram gravados continuamente por etapa. Houve rodadas piloto de balanceamento antes da bateria final registrada.

## Critérios de aceitação

- [x] Inicia por `python main.py`; suporta `--seed`, `--no-color`, `--resume`, `--save-dir` e `--balance`.
- [x] Campanha completa de 24 meses, duas ações por mês, consultas e configurações gratuitas.
- [x] Oito mercados e economia consistente; participação ponderada por demanda real.
- [x] Três concorrentes com decisões, caixa finito, investimentos e reações.
- [x] Sete sabores clássicos e pesquisa de experimentos.
- [x] Eventos alteram economia, atributos, relações e histórias persistentes.
- [x] Caos independente de reputação, com oportunidades e riscos.
- [x] 53 eventos grandes e 60 notícias curtas; todos os grandes eventos alcançados em simulação.
- [x] 11 finais; todos alcançados por decisões legais na soma da bateria principal e dos cenários dirigidos.
- [x] Conquistas, histórico e recordes persistentes; cosméticos desbloqueáveis.
- [x] Salvamento/carregamento, agenda, flags e RNG preservados; arquivos versionados e escrita atômica.
- [x] Seeds reproduzíveis e agentes de teste separados do motor.
- [x] Modo de simulação independente da interface, com seis estratégias.
- [x] 35 testes principais passaram; partida completa também percorreu os menus de `main.py`.
- [x] README, guia de sistemas, dependências, evidências e ferramenta de balanceamento entregues.
- [x] Interface em português, ASCII/Rich, menus numéricos e suporte sem cores.
- [x] Fluxo otimizado para a meta de 15–20 minutos, sem cronômetro, animações ou relatórios detalhados obrigatórios.

## Evidências

- `reports/tests.txt`: saída da suíte de 35 testes.
- `reports/simulation_600.json`: 600 campanhas, seeds 1000–1599, 100 por estratégia, invariantes econômicos auditados.
- `reports/targeted_scenarios.json`: falência por capacidade ociosa e intervenção por concentração/práticas agressivas.
- `reports/terminal_preview.txt`: exemplo de painel, fechamento e evento em 80 colunas.
- `BALANCEAMENTO.md`: interpretação dos resultados e ajustes realizados.

## Limitações e próximos estudos

A meta temporal foi tratada pelo desenho da interface, mas **não foi validada em teste humano cronometrado**. Diversão, ritmo de leitura e novas estratégias humanas precisam de observação. A bateria principal teve 0% de falência, enquanto o cenário dirigido de escolhas ruins faliu no mês 17; isso é uma decisão de tolerância inicial, não uma alegação de balanceamento definitivo.

Execução verificada em Python 3.12/macOS; sintaxe compatível com 3.11 e layout testado em 48/80 colunas. Falta validação manual em Windows/Linux. Um save por pasta; não executar dois escritores simultâneos no mesmo diretório. Não há serviços externos ou arquivos de arte proprietários.

Não há etapa de implementação pendente para a versão entregue. Estudos humanos e ajustes posteriores podem partir desta versão funcional.

## Preparação para GitHub — 16/11/2026, 18h30

Os 35 testes passaram novamente. Git local inicializado em `main`; caches, ambientes, arquivos de credenciais e saves excluídos do conjunto de publicação. Destino solicitado: repositório privado `ESAran/plutonita-world-domination`. A criação remota e o envio continuam bloqueados por falta de autenticação Git disponível e indisponibilidade do controle do Chrome. O conector GitHub não oferece criação de repositórios e a consulta ao destino retornou 404. Nenhum arquivo foi enviado.

## Revisão de usabilidade e publicação — 17/11/2026

- [x] Limpeza Rich a cada tela; opção `--no-clear` e comportamento compatível com redirecionamento.
- [x] Três propostas diretas; duas ações por ano; investimentos ocultos após gastar ações.
- [x] Consulta direta da empresa e operações avançadas opcionais paginadas.
- [x] Campanha 1998–2021, relatórios e efeitos anuais, Halloween agregado.
- [x] README com header original, controles novos e sete imagens atualizadas.
- [x] 42 testes passaram; 600 campanhas anuais e dois cenários dirigidos concluídos.
- [x] Código antigo recuperado e validado por hashes após indisponibilidade de cópias do iCloud.
- [x] Publicado no repositório público fornecido pelo usuário: ESAran/Plutonita-World-Domination. A árvore remota coincide com o commit local (36e26f47afbdcfbf5bee523ed31d567c4dd1068e).

O usuário pediu envio imediato sem novos testes. Resultados acima já estavam concluídos antes desse pedido. A revisão substitui a escala mensal e o fluxo anterior; as seções anteriores registram o histórico.
