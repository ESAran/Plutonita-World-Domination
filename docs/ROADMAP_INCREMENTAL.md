# Roadmap — Plutonita: World Domination incremental

## Direção acordada

Comprar unidades, pesquisar sabores e ver o império crescer. A economia dá ritmo
às descobertas; a bizarrice altera a trajetória da empresa. Sem cliques repetidos,
gestão de preços, manutenção, estoque, distribuição manual ou limite de ações.

- 24 rodadas anuais (1998–2021), avançadas manualmente.
- Painel principal: caixa, renda anual prevista, unidades, pesquisa e caos.
- Mapa em uma tela separada; começo no Brasil, expansão latino-americana e
  abertura mundial no ano 10, mesmo que a etapa regional esteja incompleta.
- Compra e pesquisa alteram a previsão imediatamente. O fechamento paga a renda
  uma única vez e calcula presença nos mercados abertos automaticamente.
- Jornal a cada fechamento, no máximo uma decisão principal por edição. Decidir
  prepara o próximo ano; notícias e consequências antigas continuam consultáveis.
- Caos oferece vantagens e riscos anunciados. Consequências podem voltar anos
  depois; derrotas irreversíveis precisam de sinais e oportunidade de intervenção.
- Final perfeito: todos os mercados dominados antes do último ano, sem ruptura
  em andamento. Outros finais reconhecem resultados econômicos e narrativos.
- O humor ainda será calibrado com exemplos aprovados/rejeitados pelo usuário.

## Etapas e critérios de conclusão

### 1. Campanha jogável de ponta a ponta — em implementação

- [ ] Estado independente e regras de compras, melhorias e pesquisas.
- [ ] Unidades com custo crescente e ganho anual explícito; sabores automáticos.
- [ ] Painel compacto, laboratório, mapa e passagem anual sem ações limitadas.
- [ ] Mercado brasileiro, América Latina e mercados globais a partir do ano 10.
- [ ] Jornal anual com resultado financeiro, notícias e decisão quando aplicável.
- [ ] Primeira cadeia narrativa: fábrica ambulante e filial uruguaia.
- [ ] Pressão do caos com avisos, contenção com custo estratégico e desfecho.
- [ ] Encerramento por prazo, vitória antecipada e finais alternativos iniciais.
- [ ] Save atômico, seed e retomada no jornal sem repetir pagamentos/decisões.
- [ ] Testes de regras, transições, saves, interface e campanhas completas.

Esta etapa entrega uma **base para jogar e avaliar**, não o balanceamento final.
O modo clássico e seus arquivos de campanha/perfil ficam preservados.

### 2. Equilíbrio e ritmo — após jogar a base

- [ ] Ajustar custos, retornos, ritmo de pesquisas e expansão com partidas humanas.
- [ ] Validar que comprar, melhorar e poupar para pesquisar são escolhas distintas.
- [ ] Comparar estratégias cautelosas, expansionistas e experimentais por seeds.
- [ ] Tornar o final perfeito difícil, possível e alcançável por mais de uma rota.
- [ ] Ajustar concorrentes globais sem acrescentar menus administrativos.
- [ ] Verificar clareza dos avisos de caos e ausência de derrotas ocultas inevitáveis.

### 3. Conteúdo e humor — calibração com o usuário

- [ ] Preparar exemplos para seleção de tom antes de ampliar o catálogo.
- [ ] Revisar textos provisórios; preferir consequências persistentes e humor
  corporativo diante do absurdo a trocadilhos infantis ou aleatoriedade gratuita.
- [ ] Adicionar sabores, unidades e cadeias com escolhas e retornos próprios.
- [ ] Dar identidade visual às descobertas no painel, jornal e mapa ASCII.
- [ ] Ampliar finais narrativos sem exigir uma única sequência secreta de respostas.

### 4. Acabamento e lançamento

- [ ] Histórico de campanhas e coleção de finais da nova versão.
- [ ] Tutorial curto, acessibilidade, revisão de terminais estreitos e Windows/Linux.
- [ ] Capturas atualizadas, guia do jogador, documentação e versão de lançamento.
- [ ] Teste humano de duração, compreensão e diversão; rodada final de regressão.

## Decisões iniciais de implementação (ajustáveis)

Dinheiro é o único recurso gasto. Pesquisa é uma compra definitiva; não há linhas
ativas para configurar. Todas as regiões abertas recebem progresso automático;
domínio consolidado não regride. Concorrência reduz a velocidade de expansão
mundial, com efeito visível. Caos elevado por anos consecutivos agrava o risco;
conter uma crise implica abrir mão de vantagens, não pagar uma taxa de limpeza.

Regras novas ficam em `plutonita/incremental/`. A entrada padrão passa a usar a
nova campanha; `--classic` mantém a versão anterior e `--resume` retoma o save
da modalidade escolhida. O arquivo novo é `incremental.json`, separado de
`campaign.json` e `profile.json`. Nenhum save antigo é convertido silenciosamente.

## Fora deste redesenho

Tempo real/produção offline, multiplayer, microgerenciamento, exércitos, novos
serviços externos e implementação de todos os exemplos de humor antes da seleção.
