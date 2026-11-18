# Ajustes do playtest — 18/11/2026

## Instrução atual — registrar e aguardar

O usuário aprovou os pontos 2 a 8 da checagem conjunta, com alterações nas rotas
de Elimar e da Receita Federal. Este documento registra o trabalho a fazer.
**Não iniciar a implementação dos novos ajustes até o próximo comando do usuário.**
A publicação desta rodada é somente deste documento de tarefas.

Interface, predadores, notícias contextuais e apresentação de Elimar com retorno
em sete anos já foram desenvolvidos localmente em rodadas anteriores. As caixas
marcadas abaixo se referem a esse trabalho local; não significam que os novos
ajustes aprovados nesta checagem já estejam implementados ou publicados.

Os pontos aprovados devem ser implementados e testados na próxima etapa autorizada.
A filial ficou sem resposta à dúvida de interpretação do ponto 1; preservar a
instrução literal registrada na seção 6, sem tratar a interpretação como aprovada.
Consequências futuras e probabilidades neste documento são informações de
produção e não devem aparecer como spoilers nas alternativas do jogo.

## 1. Interface e ritmo — interface aprovada e implementada

- [x] Preservar a fachada PLUTONITA: WORLD DOMINATION e recuperar o logo ASCII
  existente em `plutonita/ui/ascii_art.py`.
- [x] Manter a limpeza da tela entre telas e o suporte a `--no-clear`.
- [x] Separar visualmente caixa/renda, progresso, compras e navegação.
- [x] Dar ao Plutonita Times uma tela própria com identidade de jornal:
  cabeçalho, edição, manchete, notas curtas, balanço e decisão em áreas distintas.
- [x] Mostrar níveis como `NÍVEL 2 · ◆◆◇◇`, com alternativa ASCII e distinção
  legível sem cores. Evitar o sufixo solto `N2`.
- [x] Acrescentar renda total anual de cada categoria, considerando quantidade
  e modificadores ativos; manter renda adicional da próxima unidade.
- [x] Adaptar a apresentação à largura do terminal sem cortar valores.
- [ ] Avaliar o ritmo parado entre compras: distribuir notícias preparatórias,
  decisões e retornos ao longo da campanha sem exigir micromanagement.

Proposta de painel: logo no topo; ano e fase abaixo; caixa, renda e domínio em
resumo compacto; tabela central; comandos fixos no rodapé. Compra atualiza a
tela e destaca o ganho obtido. Verde e magenta preservam a identidade existente.

Exemplo de tabela (valores ilustrativos do relato, não cálculo real do save):

| Comprar unidades | Nível | Quantidade | Custo | +Renda/ano | Total/ano |
|---|---|---:|---:|---:|---:|
| [1] Vendedores | 2 · ◆◆◇◇ | 10 | R$ 628 | R$ 202 | R$ 2.020 |
| [2] Máquinas de venda | 1 · ◆◇◇◇ | 3 | R$ 822 | R$ 384 | R$ 1.152 |
| [3] Fábricas | 1 · ◆◇◇◇ | 2 | R$ 3.899 | R$ 1.680 | R$ 3.360 |

## 2. Mapa — aprovado, a implementar

- [ ] Ampliar o mapa e detalhar contornos e pontos, incluindo Groenlândia,
  região ártica e Antártida.
- [ ] Diferenciar mercados fechados, presença e domínio completo por cores e símbolos.
- [ ] Manter tela própria, legenda e informações por região.
- [ ] Incluir os polos como geografia visual, sem criar mercados novos nesta revisão.
- [ ] Integrar a Groenlândia à América do Norte; preservar os seis mercados atuais.
- [ ] Preparar versões para terminais largos e estreitos e verificar a leitura.

## 3. Jornal sem repetição e com preparação narrativa

- [x] Relacionar notícias a compras, pesquisas, expansão e decisões efetivamente
  ocorridas. Priorizar reações recentes e impedir contradições com a rota atual.
- [x] Avaliar o lote de 40 notícias contextuais
  aprovado na checagem: 40 elegíveis, incluindo a nota de CEO.
- [x] Impedir repetição de notícias na mesma campanha, inclusive após salvar e retomar.
  A seleção consulta IDs e textos das edições anteriores.
- [x] Se acabarem as notas elegíveis, publicar somente balanço e acontecimentos
  novos; não reciclar manchetes para preencher espaço.
- [x] Ampliar o catálogo com textos submetidos à avaliação do usuário.
- [x] Publicar o aviso de não juntar original e falsificação dois anos antes
  da caça; vincular o evento à publicação efetiva, não a um sorteio independente.
- [x] Publicar a recusa dos testes de paternidade antes da gravidez da fábrica,
  condicionada à rota uruguaia.
- [x] Garantir ordem dos capítulos mesmo quando uma crise adiar uma decisão.
- [x] Distinguir notícias únicas de indicadores recorrentes de estado, como caos.

## 4. Elimar Gonzales

Apresentação, promoção para CEO e retorno em sete anos já aprovados e desenvolvidos localmente.

- [x] Apresentá-lo como funcionário do mês em sete países ou mais, simultaneamente.
- [x] Retirar qualquer menção às famílias da apresentação e das alternativas.
- [x] Alterar a promoção para CEO.
- [x] Guardar a revelação das famílias para o desfecho da cadeia.
- [x] Rever a homenagem e seu momento: não usar a premiação de funcionário do mês
  como divulgação que já deveria ter revelado o segredo antes da promoção.
- [ ] Implementar a presidência com acúmulo do cargo de CEO, a opção de pedido
  de desculpas após a falência por pensões e o final Elimar descritos na seção 9.
- [x] Checar texto, momento da revelação e efeitos econômicos antes de implementar.

## 5. Predadores — aprovado e implementado

Pedido: prejuízo já ocorrido ao chegar a notícia; uma solução de custo médio;
alternativa gratuita com punição leve e risco posterior; terceira solução cara
com sacrifício imediato maior e encerramento definitivo deste problema.

Proposta inicial de chegada: perder 5% do caixa após a receita anual (8% com
lote maior). Mostrar o valor efetivamente descontado no balanço. As escolhas
tratam do estoque restante; não cobram novamente esse prejuízo.

| Opção proposta | Custo imediato | Efeito conhecido para o jogador |
|---|---:|---|
| 1. Isolar os predadores e proteger o depósito | R$ 1.200 | Evita novas perdas deste caso por dois anos; suspende o bônus de domínio durante a contenção; caos -8. |
| 2. Deixar que escolham quais sabores são legítimos | R$ 0 | Mantém o bônus de domínio; renda -5%; caos +5. |
| 3. Desativar o lote e reconstruir o estoque | R$ 2.400 | Renda -10% por um ano; encerra o bônus de domínio; caos -15; elimina definitivamente perdas deste caso. |

Documentação interna aprovada: a opção 2 tem 60% de chance de agravamento após
três anos. A perda de renda passa de 5% para 20%, e uma nova decisão permite
conter o depósito, conviver com a perda de 20% ou desativar o lote. O sorteio
acontece uma vez; quando não há agravamento, permanece a perda de 5%. A opção 1 compra tempo e
devolve uma escolha ao fim da contenção; a opção 3 encerra a cadeia. Não revelar
a cena futura ou a probabilidade no texto da opção 2. Uma contenção contratada
por prazo definido pode informar sua duração, pois é uma condição conhecida.

Exemplo: se R$ 5.444 for o caixa antes do ataque, a perda inicial de 5% fica em
cerca de R$ 272. Depois dela, cada escolha desconta apenas seu próprio custo.
O lote maior perde 8% na chegada; os custos das escolhas são os mesmos.
O equilíbrio em partidas humanas continua em avaliação.

## 6. Fábrica no Uruguai — instrução registrada; interpretação pendente

Instrução do usuário: **“2000 + a fabrica na legalização”**.
Sugestão do usuário: **“gravidez é talvez só 50%”**.
O ponto 1 não foi respondido na última aprovação conjunta. Não considerar
confirmada a compra de uma unidade extra nem transformar “talvez” em aprovação
numérica definitiva.

- [ ] Esclarecer, na retomada do desenvolvimento, se significa R$ 2.000 mais o
  preço atual de uma fábrica, acrescentando uma unidade, ou R$ 2.000 para
  legalizar a fábrica existente que fugiu, sem comprar outra.
- [ ] Registrar 50% de chance de gravidez como proposta do usuário a confirmar.
- [ ] Se essa probabilidade for adotada, sortear uma única vez e persistir o
  resultado; carregar o save não pode mudar a ocorrência da gravidez.
- [ ] Na proposta apresentada: gravidez após três anos, precedida pela notícia
  de paternidade; sem gravidez, a filial continua funcionando normalmente.
- [ ] A proposta de benefícios permanece +20 pontos na América Latina, renda
  +10% e caos +12. Se o mercado já estiver aberto, respeitar o teto de domínio.
  Confirmar junto da interpretação do custo.
- [ ] Não antecipar gravidez, probabilidade, data ou prejuízo na alternativa.
- [ ] Comparar o custo da rota com uma expansão normal equivalente, considerando
  eventual fábrica adicional, e preservar a vantagem solicitada pelo usuário.

## 7. Dívida — aprovado, a implementar

- [ ] Permitir financiar apenas o valor faltante de uma decisão, por opção explícita.
- [ ] Limitar o crédito total a uma renda anual prevista.
- [ ] Cobrar juros de 10% ao ano e fixar vencimento em três anos.
- [ ] Destinar automaticamente 30% da renda recebida à dívida, permitindo
  pagamentos extras voluntários e sem descontar além do saldo devido.
- [ ] Mostrar principal, juros, amortização e prazo antes de contratar.
- [ ] Emitir avisos claros antes do vencimento; saldo não quitado no prazo causa
  falência e um encerramento próprio.
- [ ] Impedir que novos empréstimos renovem o prazo de dívidas anteriores.
- [ ] Limitar o vencimento ao último ano da campanha para empréstimos tardios.
- [ ] Definir e testar a ordem de renda, juros, amortização e avaliação da falência.
- [ ] Persistir contratos e saldos; validar compatibilidade com saves anteriores.

## 8. Tribunal — aprovado, a implementar

Probabilidades são internas. Mostrar custos e efeitos conhecidos ao jogador,
sem narrar os capítulos futuros antes de acontecerem.

### Proibição da Plutonita

- [ ] Assassina: R$ 3.500; 70% de sucesso com renda +20%; 30% de falha com renda
  -25%; caos +15 em ambos os resultados.
- [ ] Na falha, revelar que a criatura foi chantageada com fotos em festas
  clandestinas no Madame Satã e passou a trabalhar como fiscal.
- [ ] Carregamento de presente: R$ 1.800; renda +10%; caos +8. Não anunciar o
  pedido posterior em toneladas.
- [ ] Recolhimento: 10% do caixa, com o valor exato visível antes da escolha;
  caos -8; preserva a renda futura.

### Retorno da criatura como fiscal

- [ ] Capturar: custo equivalente a uma renda anual prevista; elimina a
  penalidade de renda; caos -10.
- [ ] Reorganizar entregas e conviver: sem custo de caixa; substitui a perda de
  25% por uma perda permanente de 8%.
- [ ] Testar que as duas rotas oferecem alternativas econômicas reais.

### Pedido do tribunal em toneladas

- [ ] Fornecer continuamente: remove o bônus anterior de 10% e passa a aplicar
  perda de 5% da renda.
- [ ] Encerrar o acordo: cobra 20% de uma renda anual, remove o bônus e encerra
  o fornecimento, sem manter a penalidade dessa rota.

## 9. Plutopia Brasileira e final Elimar — aprovados, a implementar

Manchete-base aprovada: **BRASIL CAMINHA PARA A FALÊNCIA ENQUANTO A PLUTONITA
BATE RECORDE DE VENDAS**.

- [ ] Introduzir a crise depois de consolidar o Brasil, a partir do ano 12,
  relacionando-a à compra intensiva de Plutonita.
- [ ] Permitir comprar os dois principais partidos rivais e formar a Plutopia
  Brasileira, com as alternativas aprovadas abaixo.

| Alternativa | Custo | Efeito aprovado |
|---|---|---|
| Instalar presidente ciborgue controlado pela organização | Uma renda anual | Renda +25%; caos +20. |
| Colocar Elimar presidente enquanto contratado | 80% de uma renda anual | Renda +20%; caos +10; pode acumular CEO e presidente. |
| Manter a empresa fora do governo | Sem desembolso imediato | Renda -10% durante dois anos pela crise. |

### Alterações expressas do usuário na última checagem

- [ ] Se Elimar falir por pensões, oferecer **pedir desculpas colocando-o como
  presidente**. Essa possibilidade deve continuar acessível mesmo que a falência
  o tenha afastado da empresa; não exigir contratação ativa nessa exceção.
- [ ] Permitir acumular CEO e presidente, mantendo o retorno da história em sete
  anos após a promoção original para CEO, sem reiniciar esse relógio.
- [ ] Tratar a interação entre ausência, retorno, bônus de CEO e bônus presidencial
  para não duplicar bônus nem manter penalidade de ausência incoerente.
- [ ] Com caos muito alto, Elimar pode tomar o poder da Plutonita e destronar o
  jogador, levando ao **final Elimar**.
- [ ] Na etapa de desenvolvimento, definir o limiar de “caos muito alto”, a
  condição/probabilidade da tomada de poder e sua prioridade frente a outros
  finais. Esses números não foram fixados pelo usuário nesta checagem.
- [ ] Sinalizar a escalada e oferecer oportunidade de reação antes da perda
  irreversível de controle, sem revelar antecipadamente a cena final.
- [ ] Especificar o custo e os efeitos da exceção de pedido de desculpas na
  retomada; não presumir que a falência pessoal seja automaticamente quitada.

## 10. Receita Federal e Fernando Taxad — aprovado, a implementar

Manchete-base aprovada: **FERNANDO TAXAD COBRA IMPOSTO SOBRE CHICLETES QUE A
PLUTONITA AINDA NÃO VENDEU**.

A cobrança recai sobre os lucros projetados pelo comercial. Custos percentuais
usam como base a renda anual do momento da decisão, registrada para os pagamentos
futuros; mudanças posteriores de renda não recalculam o valor contratado.

- [ ] Regularizar: pagar 25% de uma renda anual e encerrar o caso.
- [ ] Contestar: pagar 10% de uma renda anual aos advogados.
- [ ] Vitória na contestação, com 60% de chance: cancelar a cobrança **e conceder
  isenção que aumenta a renda anual em 5%**, conforme alteração expressa do usuário.
- [ ] Derrota, com 40% de chance: cobrar adicional de 35% da renda anual de
  referência após dois anos.
- [ ] Parcelar: total de 40% de uma renda anual, dividido em três pagamentos.
- [ ] Persistir sorteio, referência financeira e parcelas; não sortear novamente
  ao retomar nem conceder a isenção mais de uma vez para o mesmo caso.
- [ ] Definir a duração da isenção na implementação: o bônus de 5% foi aprovado,
  mas não foi estabelecido prazo específico nesta checagem.
- [ ] Não mostrar as probabilidades ou revelar o capítulo futuro nas alternativas.

## 11. Reta final — aprovado, a implementar

- [ ] Fazer a campanha continuar até o ano 24, salvo derrota anterior.
- [ ] Registrar quando o domínio completo foi atingido pela primeira vez.
- [ ] Exigir domínio alcançado antes do ano 24 e manutenção de controle/estabilidade
  até o encerramento para obter o final perfeito.
- [ ] Introduzir até dois grandes acontecimentos entre os anos 20 e 23,
  escolhidos conforme as rotas da campanha:
  - aliança de concorrentes para conter a expansão;
  - presidente ciborgue passando a dar ordens à própria organização;
  - fábricas autônomas retomando a disputa pelo controle do império.
- [ ] Dar a cada acontecimento uma reação possível e tempo útil para responder.
- [ ] Integrar as crises de dívida, Elimar e demais cadeias sem esconder regras de
  derrota nem exigir respostas a capítulos publicados depois do encerramento.
- [ ] Evitar sobreposição que torne obrigatória uma sequência de derrotas sem saída.

## 12. Encerramento e regras gerais — aprovado, a implementar

- [ ] Criar edição especial final do Plutonita Times.
- [ ] Mostrar o mapa final e desfechos dos personagens/projetos envolvidos na campanha.
- [ ] Dar identidade ao final Elimar e ao final por dívida, além dos finais existentes.
- [ ] Revisar todas as alternativas para remover spoilers de acontecimentos futuros,
  incluindo textos ainda acessíveis em saves anteriores.
- [ ] Exibir custo real calculado: nenhuma opção com cobrança percentual pode
  aparecer como “sem custo”.
- [ ] Manter explícitas regras como vencimento da dívida e perda definitiva de
  controle; suspense narrativo não deve ocultar essas condições.
- [ ] Preservar decisões já tomadas e resultados persistidos ao migrar saves.

## Verificação e entrega após aprovação dos blocos

- [x] Testar ausência de notícias repetidas e ordem dos prenúncios/capítulos.
- [ ] Testar efeitos imediatos e futuros, custos reais, opções acessíveis e sorteios
  persistidos sem novo sorteio ao carregar.
- [ ] Comparar rotas de compras, contenção, risco e expansão em campanhas completas.
- [ ] Conferir interface larga/estreita, sem cores e com/sem limpeza de tela.
- [ ] Atualizar documentação de regras, direção de humor e capturas.
- [x] Registrar separadamente o que foi aprovado, desenvolvido localmente e o que falta fazer.
- [ ] Após novo comando e desenvolvimento, publicar a implementação validada no GitHub.
- [x] Preparar a publicação atual somente do documento de tarefas, conforme pedido.

## Entrega local desta rodada

- Implementados logo, níveis, total por categoria, layout adaptável, jornal e
  preservação do clear. Abaixo de 80 colunas, as compras viram blocos de texto.
- Implementadas três escolhas, perda inicial, contenção por dois fechamentos,
  risco de 60% após três anos e desativação definitiva com um ano de reconstrução.
- Saves v1 são aceitos. Jornais antigos dos predadores conservam suas alternativas
  originais, sem cobrança retroativa. Novos saves usam versão 2.
- Verificação: 68 testes passaram. Dois testes do modo clássico passaram a usar
  explicitamente `--classic`; 26 testes novos cobrem interface, predadores, jornal e Elimar.
- Implementados catálogo contextual, histórico sem repetição, prenúncios em ordem
  e reações às escolhas, incluindo a nota de CEO.
- Elimar: funcionário do mês em sete países, sem dica sobre fotos; promoção para
  CEO e retorno sete anos depois. Famílias aparecem apenas no desfecho.
- Prévias em `reports/revisao_playtest/`: painel largo/estreito e jornal.
- A implementar após o próximo comando: mapa, dívida, tribunal, Plutopia Brasileira,
  presidência/final de Elimar, Receita, reta final e novos encerramentos.
- Filial e gravidez: preservar a instrução do usuário e esclarecer os detalhes
  pendentes da seção 6 na retomada.
- Esta publicação documental não inclui os arquivos de código alterados nas rodadas
  anteriores; eles continuam no workspace para a próxima etapa.
