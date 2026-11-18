![PLUTONITA: WORLD DOMINATION](assets/header.png)

# Plutonita: World Domination

**Compre unidades. Pesquise sabores. Conquiste o mundo.**

Um incremental de terminal sobre construir um império de chicletes e financiar
decisões empresariais questionáveis. Sua fábrica pode ganhar pernas, atravessar
a fronteira e abrir uma filial no Uruguai. O departamento jurídico acompanha.

**Nova campanha jogável em desenvolvimento.** O ciclo completo já funciona;
equilíbrio, humor e variedade de acontecimentos ainda serão ajustados jogando.

## Jogar

Requer Python 3.11 ou mais recente. No diretório do projeto:

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

No Windows, use `py` ou `python` no lugar de `python3`. O jogo funciona offline
depois da instalação. Para atualizar uma cópia já clonada:

```bash
git pull --ff-only
python3 main.py
```

Escolha **Nova campanha**. Uma seed é opcional; deixe em branco para sortear.

```bash
python3 main.py --seed trabalho
python3 main.py --resume
python3 main.py --no-color
python3 main.py --no-clear
python3 main.py --save-dir saves/outra-campanha
```

## Como funciona

- **24 anos, de 1998 a 2021.** Compre enquanto houver dinheiro; Enter encerra o
  ano, recebe a renda prevista e faz o império avançar. Sem cronômetro ou cliques
  repetidos para produzir.
- **Unidades e melhorias.** Vendedores, máquinas, fábricas e categorias maiores
  rendem automaticamente. A tela mostra preço e ganho anual de cada compra.
- **Sete sabores.** Pesquisas têm benefícios permanentes e automáticos. Alguns
  sabores liberam unidades; outros aumentam renda, alcance ou risco.
- **Mapa separado.** Comece no Brasil, entre na América Latina e abra mercados
  globais no ano 10. Todas as regiões abertas crescem automaticamente.
- **Plutonita Times.** Cada fechamento gera uma edição com resultados, notícias
  e, quando houver, uma decisão que muda os anos seguintes. Edições ficam no arquivo.
- **Caos com consequências.** Quatro fechamentos consecutivos com caos em 75 ou
  mais causam uma derrota. O jornal avisa e oferece uma intervenção antes disso.
- **Oito finais iniciais.** Dominar os seis mercados antes do ano 24, com caos
  abaixo de 75 e a empresa sob seu controle, dá o final perfeito. Outras rotas
  levam a resultados econômicos ou narrativos diferentes.

| Tecla no painel | Função |
|---|---|
| `1` a `5` | Comprar uma unidade das categorias exibidas |
| `P` | Pesquisar sabores |
| `U` | Melhorar uma categoria de unidades |
| `M` | Consultar o mapa e abrir mercados |
| `J` | Consultar edições anteriores do jornal |
| `Enter` | Encerrar o ano |
| `Q` | Salvar e sair para o início |

No jornal, escolha uma opção numerada quando houver uma decisão e pressione
Enter para continuar. Nos submenus, Enter volta ao painel. Não há limite de duas
ações, gestão de preço, estoque ou despesas de manutenção.

## Saves e campanha anterior

O jogo salva após compras, pesquisas, expansão, fechamentos e decisões.
A nova campanha usa `saves/incremental.json`. É possível sair no meio do jornal
e retomá-lo sem receber novamente a renda ou perder a decisão pendente.

Os saves antigos continuam disponíveis no modo clássico:

```bash
python3 main.py --classic
python3 main.py --classic --resume
```

Esse modo mantém `campaign.json` e `profile.json`. Não há conversão automática
entre campanhas. `--balance` continua sendo uma opção exclusiva do modo clássico.
Ao criar outra campanha incremental, o jogo pergunta antes de substituir seu save;
use `--save-dir` para guardar campanhas separadas.

## Estado desta entrega

Há cinco categorias de unidades, três melhorias por categoria, sete sabores,
seis mercados, seis decisões narrativas iniciais e oito finais. A pressão dos
concorrentes mundiais ainda é simplificada. O catálogo de humor é provisório.

Verificações rápidas cobriram inicialização, compra/pesquisa, mapa, jornal,
salvamento e campanha até o encerramento. Uma partida de referência alcançou o
final perfeito no ano 23; isso **não comprova o equilíbrio** das demais estratégias.
O próximo passo é jogar e ajustar ritmo, clareza, escolhas e acontecimentos.

- [Roadmap e próximos passos](docs/ROADMAP_INCREMENTAL.md)
- [Regras da campanha incremental](docs/INCREMENTAL.md)
- [Documentação da campanha clássica](docs/CLASSICO.md)

Regras novas em `plutonita/incremental/`; valores iniciais em `catalog.py`,
histórias em `stories.py`, ciclo anual em `game.py` e telas em `ui.py`.

---

Projeto de fã independente e não oficial, sem vínculo com a Arcor.
