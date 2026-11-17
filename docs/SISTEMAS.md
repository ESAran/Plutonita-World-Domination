# Sistemas e guia de manutenção

Este documento contém **spoilers de receitas e finais**.

## Fluxo

A máquina de estados usa `planning`, `event` e `finished` internamente. Só `planning` aceita ações e configurações. Ao fechar, a produção é resolvida uma vez e as ações chegam a zero. Um evento trienal interrompe o avanço até sua decisão. O próximo ano processa consequências, movimentos dos concorrentes e notícias uma única vez. O carregamento restaura o estado sem repetir a preparação anual.

Decisões inválidas não cobram nem consomem ações. Consultas e alterações comerciais não consomem o gerador aleatório. Custos são validados antes da mutação; riscos anunciados podem acrescentar multas, inclusive deixando o caixa ligeiramente negativo.

## Economia

Demanda regional:

```text
D = demanda-base × (1 + 0,008 × (ano − 1)) × sazonalidade
sazonalidade anual agregada = 1,03 (média do antigo pico de 12% em três meses)
```

O preço realizado, arredondado a centavos, é:

```text
P = preço-base × poder de compra regional × política × (1 + bônus médio dos sabores)
política = 0,78 / 1 / 1,38
```

Para uma marca presente no mercado:

```text
A = (0,28 + reconhecimento/70)
  × (0,5 + reputação/100)
  × adequação do portfólio
  × (1 + marketing/65)
  × (1 + 0,075 × inovação)
  × (P / (preço-base × poder de compra))^(−1,7 × sensibilidade)
  × modificadores de eventos
```

A adequação combina média de atratividade e afinidades dos produtos, preferência regional, diversidade, tendências e sinergias. Baba de Bruxa reforça o marketing; Dentada + Abraço oferecem bônus conjunto; Abóbora agrega o Halloween de cada ano (+9,2% de atração); Zumbi cresce com o tempo; Baba e Atomic oscilam em padrões anuais limitados. As descrições reais dos produtos ficam separadas desses atributos fictícios.

A demanda inicial é `D × A / (soma das atratividades + atratividade de não compra)`. A opção de não compra tem peso-base 0,7. Quantidades são inteiras. Cada empresa atende regiões por prioridade decrescente; empates usam ordem alfabética dos identificadores. Até oito rodadas redistribuem a demanda inicialmente comercial que ficou sem produto, apenas a marcas presentes com capacidade disponível. Restos de arredondamento podem permanecer sem venda; nenhum cliente é contado duas vezes.

```text
capacidade = fábricas × (1100 + (nível − 1) × 550) + capacidade adicional − dano
custo unitário = 1,40 × custo relativo médio × (1 − 0,065 × eficiência)
manutenção = fábricas × (450 + (nível − 1) × 125) + manutenção adquirida
receita = soma(unidades × preço realizado)
lucro = receita − custos variáveis − manutenção − comercial − juros − royalties
```

Os números acima são os padrões; o arquivo de balanceamento é a fonte de verdade. Máximos: seis fábricas próprias, nível cinco, eficiência cinco, laboratório quatro. Capacidades adquiridas ou narrativas aparecem separadamente. Produção adicional narrativa pode ter manutenção explicitada pela opção; seus custos comerciais e variáveis continuam aplicáveis.

Despesas comerciais: R$ 130 por mercado aberto. Empréstimo: R$ 3.000 uma vez, juros de 2,5% ao ano. Financiamentos de ações, retornos de contratos, multas e eventos usam um livro de caixa separado do lucro operacional. O relatório mostra os lançamentos para evitar confundir investimento com prejuízo.

O patrimônio estimado considera caixa menos principal de empréstimos, ativos industriais, presença comercial e 24 vezes o último lucro anual positivo. É uma avaliação simplificada, sujeita às condições comerciais do último ano.

## Rivais e pressão competitiva

Cada rival mantém caixa, capacidade, regiões, preços, campanhas, inovação, eficiência, produtos e reputação. Usa as mesmas fórmulas de demanda, produção e despesas. O plano anual avalia utilização, reserva, oportunidade regional, personalidade e ameaça do jogador; uma perturbação limitada pela seed quebra empates.

Só investimentos que preservem uma reserva mínima são executados. Insolvência abaixo da linha de crédito encerra a empresa. A partir do ano 13, rivais com recursos podem financiar uma segunda campanha se houver ameaça relevante. Não há multiplicador arbitrário de dificuldade, receita gratuita ou capacidade infinita.

Aquisições custam 85% da avaliação do rival, com piso de R$ 3.000; fusões, 48%, com o mesmo piso e royalties de 12% da receita. Transferem operações, não dinheiro líquido do alvo. Essa simplificação contratual é apresentada antes da decisão. Os royalties podem tornar o crescimento por fusões caro.

## Dados de eventos

`events.json` contém 53 eventos, 3 opções por evento e identificadores únicos. Campos principais:

- `conditions`: anos mínimo/máximo, sabor, região, Caos, agressividade, rival ativo, experimentos e flags.
- `weight`: peso de seleção entre candidatos elegíveis.
- `repeat`: controle de repetição; o catálogo atual não repete grandes eventos.
- `options`: texto, custo de entrada, risco anunciado e efeitos.
- `effects`: caixa, reputação, Caos, capacidade, dano, pesquisa, eficiência, manutenção, royalties, agressividade, mercados e flags.
- `schedule`: consequências futuras ou capítulos, com atraso em anos; consequências podem ter requisitos explícitos.
- `chance`: probabilidade e dois ramos de efeitos, sempre sorteados pelo gerador do motor.

Todo evento tem uma opção com **custo de entrada zero** para evitar bloqueios. Essa opção ainda pode anunciar uma despesa compulsória, dano ou queda de demanda. Efeitos comerciais de um evento pós-fechamento começam no fechamento seguinte; uma duração de três anos no evento do ano 3 cobre os anos 4, 5 e 6.

Consequências financeiras agendadas executam uma vez, no início do ano devido. Capítulos ocupam o próximo espaço trienal disponível a partir da data agendada. Capítulos vencidos e elegíveis precedem sorteios comuns; capítulos incompatíveis são descartados. O final lista agendas que ficaram além da campanha.

Arcos:

| História | Capítulos | Continuidade |
|---|---|---|
| André | Estagiário → Sapatos → Sindicato → Assembleia | Depende de manter André como diretor e apoiar a cidadania das gomas |
| Fábricas | Pernas → Fábrica grávida → Creche | Depende de preservar o vínculo e acolher a família industrial |
| Ratos | Conselho → Auditoria → Bolsa | Depende de conservar o conselho e aceitar a controladoria |
| Lua | Descoberta → Alfândega → Contrato | Depende de financiar a missão e obter licença |

As notícias têm um conjunto separado, sem repetição dentro da campanha; dez delas alteram a disputa de demanda de forma pequena e explícita. O jornal também publica números reais do último fechamento.

## Experimentos

Receitas na ordem acidez, temperatura, efervescência, estranheza:

| Receita | Produto |
|---|---|
| 1/1/1/2 | Sabor Terça-Feira |
| 0/0/0/0 | Sabor de Nada |
| 3/3/3/3 | Último Suspiro, base do Sabor Definitivo |
| 3/3/2/2 | Nuclear Supreme |
| 0/2/1/3 | Croissant Radioativo |
| 1/0/0/3 | Sabor de Imposto |
| 0/0/3/3 | Buraco Negro |
| Outras | Gosto de Arrependimento |

Custo: R$ 1.100 + R$ 100 por ponto. Qualidade usa laboratório, características e uma variação de apenas ±0,06. Novas tentativas são ações pagas e limitadas a oito fórmulas. Estranheza custa quatro pontos de Caos por nível. Receitas com acidez igual à temperatura e efervescência pelo menos dois desbloqueiam propaganda absurda.

## Prioridade de finais

Ao fim dos 24 anos, o primeiro final elegível nesta ordem é escolhido:

1. **Falência Total**: caixa abaixo de −R$ 3.500. Também encerra antecipadamente.
2. **O Sabor Definitivo**: anotações do fundador, receita 3/3/3/3, laboratório 3 e conclusão do evento de auditoria após o ano 18.
3. **República Democrática da Goma**: André diretor, cidadania das gomas e reconhecimento da república. A decisão de reconhecimento encerra imediatamente.
4. **Mutação Global**: pacto biológico construído em evento e Caos pelo menos 85.
5. **Monopólio Desmantelado**: agressividade pelo menos 6, participação global pelo menos 30% e ausência de acordo antitruste.
6. **Imperador da Plutonita**: participação global pelo menos 43% e operações em seis mercados.
7. **O Grande Magnata**: patrimônio pelo menos R$ 1.250.000. Venda voluntária também disponível a partir do ano 18.
8. **O Chiclete do Povo**: reputação pelo menos 85, cinco mercados e participação de pelo menos 16%.
9. **Federação das Fábricas Ambulantes**: família industrial e decisão de fundar a federação.
10. **Sagrada Ordem da Bolha**: movimento religioso, Caos pelo menos 60 e quatro mercados.
11. **A Firma que se Recusou a Acabar**: sobrevivência sem outra condição prioritária.

Finalizar cedo por uma decisão explicitamente anunciada prevalece sobre a avaliação de fim de campanha, exceto insolvência. A simples existência de Caos alto não concede um final secreto.

## Persistência

O save usa versão 1 e contém dataclasses convertidas em JSON, estado do `random.Random`, configuração, eventos, histórico e estatísticas. Não há pickle nem execução de conteúdo do arquivo. A gravação temporária usa `fsync` antes de `os.replace`. A validação recusa estados estruturalmente impossíveis e números não finitos.

O perfil registra campanhas por identificador único. Retomar um final já contabilizado não duplica receitas, conquistas ou histórico. Há apenas um escritor esperado por pasta de salvamento: não abra simultaneamente duas instâncias usando o mesmo diretório.

## Interface anual e compatibilidade

O painel principal apresenta três propostas contextuais, duas decisões por ano e consulta direta. Operações avançadas são paginadas. A limpeza usa Rich apenas em terminal interativo compatível; `--no-clear` a desativa. Erros são exibidos na próxima tela e relatórios aguardam Enter.

A campanha cobre 1998–2021. Capacidade, demanda e despesas representam totais anuais em escala econômica abstrata de jogo. Para preservar saves e ferramentas existentes, os nomes internos `month`, `months`, `min_month`, `max_month`, `mean_monthly_profit` e `close_month` continuam como aliases/índices legados de turnos anuais. `Game.close_year()` e `state.year` expõem a escala nova. O calendário sazonal foi agregado, e histórias usam atrasos em anos.
