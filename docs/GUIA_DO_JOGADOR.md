# Guia do jogador

## Começar

Instale Python 3.11+, execute `python3 -m pip install -r requirements.txt` e depois `python3 main.py`.

Você herda R$ 5.000 em 1998 e tem até 2021 para construir seu império. Cada ano oferece duas ações. O painel mostra três propostas acessíveis, com custo e efeito. Escolher uma custa uma ação; as sugestões se atualizam com a situação da empresa.

## Controles

- **1–3:** executar uma proposta; gastos grandes pedem confirmação.
- **4 — Outras ações:** todas as estratégias avançadas, incluindo experimentos e negociações.
- **5 — Ver empresa:** resumo gratuito. Preços, distribuição e sabores ativos também são gratuitos e valem no próximo fechamento.
- **6:** salvar e sair da campanha.
- **0 ou Enter:** avançar o ano; confirmar somente se ainda houver ações não utilizadas. Nos submenus, voltar.

Depois de duas escolhas, os investimentos somem da tela. Não é preciso consultar relatórios para avançar. A cada três anos há uma decisão narrativa, que não gasta ação estratégica.

A tela limpa a cada menu em terminais compatíveis. Use `--no-clear` para preservar a saída e `--no-color` para desativar cores. Não há animações ou cronômetros.

## Administrar sem planilha

Produzir acima da demanda custa manutenção; capacidade insuficiente perde clientes. Eficiência reduz custo variável. Marketing traz procura temporária. Pesquisa abre produtos e histórias. Expansão aumenta vendas potenciais e despesas. Rivais usam dinheiro e fábricas próprios.

Preço econômico favorece volume; Premium favorece margem. Até três sabores ficam ativos, sem controlar unidades individualmente. Caos e reputação são independentes: uma empresa querida também pode estar envolvida com fenômenos impossíveis.

## Salvamento

O jogo salva automaticamente depois de decisões e fechamentos, incluindo eventos pendentes. Continue com `python3 main.py --resume`. Para outra campanha separada, use `--save-dir saves/outra`. A seed pode ser definida com `--seed 12345`; resultados iguais exigem também mesma versão, configuração e escolhas.

Salvamentos antigos continuam carregáveis, com os turnos restantes interpretados como anos. A versão anual agrega sazonalidade, portanto resultados futuros podem diferir da versão mensal. Arquivos pessoais em `saves/` não vão ao GitHub.

Veja [README](../README.md) para imagens, [sistemas](SISTEMAS.md) para fórmulas e spoilers e [balanceamento](../BALANCEAMENTO.md) para evidências.
