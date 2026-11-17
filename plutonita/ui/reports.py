from rich.table import Table
from rich.panel import Panel
from rich import box
from ..markets import MARKETS, PRICE_NAMES, demand
from ..products import catalog
from ..production import capacity, valuation, maintenance
from ..events import EVENTS
from ..endings import ENDINGS
from ..achievements import ACHIEVEMENTS
from .dashboard import money


def table(title,columns):
    t=Table(title=title,box=box.ASCII,expand=True,show_lines=False)
    for name in columns:t.add_column(name,overflow='fold')
    return t


def markets(console,state):
    t=table('Mercados — participação baseada em vendas reais',['Região','Demanda','Marca / preço','Prior.','Vendas %'])
    last=state.reports[-1]['companies']['player']['regions'] if state.reports else {}
    for key,m in MARKETS.items():
        r=state.player.regions.get(key)
        t.add_row(m['name'],str(demand(m,state.month)),f'{r.recognition:.0f} / {PRICE_NAMES[r.price]}' if r else 'Não opera',str(r.priority) if r else '-',f"{last.get(key,{}).get('share',0):.1%}")
    console.print(t)
    traits=table('Perfis de consumo',['Região','Poder de compra','Sensibilidade ao preço','Preferência'])
    labels={'popular':'Popular','viral':'Viral','premium':'Premium','estavel':'Estável','experimental':'Experimental'}
    for m in MARKETS.values():traits.add_row(m['name'],f"{m['income']:.2f}x",f"{m['sensitivity']:.2f}",labels[m['favorite']])
    console.print(traits)
    console.print('Sensibilidade alta favorece preços econômicos. Poder de compra multiplica o preço realizado.')
    console.print('Prioridade 3 recebe produção antes de 2 e 1. Empates usam a ordem fixa dos códigos regionais.\nPreços e prioridades são gratuitos; valem somente no próximo fechamento.')


def finances(console,state):
    if not state.reports:
        console.print('O primeiro relatório aparece após encerrar 1998.');return
    r=state.reports[-1]['companies']['player'];month=state.reports[-1]['month']
    t=table(f'Fechamento de {1997+month}',['Item','Valor'])
    for label,key in [('Receita','revenue'),('Custo variável','variable'),('Manutenção industrial','maintenance'),('Despesas comerciais','commercial'),('Juros','interest'),('Royalties de fusões/acordos','royalty'),('Despesas totais','expenses'),('Lucro operacional','profit')]:
        t.add_row(label,money(r[key]))
    console.print(t)
    console.print(f"Caixa imediatamente antes das vendas: {money(r['cash_before'])}; após operação: {money(r['cash_after'])}.")
    console.print(f"Produção vendida: {r['sold']}/{r['capacity']} ({r['sold']/max(1,r['capacity']):.1%}); demanda inicial não atendida: {r['unmet']}.\nParticipação global: {r['share']:.1%}; mudança {r['share_change']*100:+.2f} pontos percentuais.")
    t=table('Contribuição por região (antes de fábrica, juros e royalties)',['Mercado','Un.','Preço','Contribuição'])
    for key,row in sorted(r['regions'].items(),key=lambda kv:-kv[1]['contribution']):
        t.add_row(MARKETS[key]['name'],str(row['units']),money(row['price']),money(row['contribution']))
    console.print(t)
    if r['unmet']>0: console.print('Diagnóstico: faltou capacidade para a demanda inicial. Revise fábricas e prioridades.',style='yellow')
    elif r['sold']<.65*r['capacity']:console.print('Diagnóstico: capacidade ociosa. Marketing, novos mercados e produtos podem trazer clientes; mais fábricas elevam manutenção.',style='yellow')
    if r['royalty']>0:console.print('Fusões e acordos societários cobram royalties sobre receita, inclusive em anos ruins.')
    if r['share_change']<0:console.print('A participação caiu: compare os movimentos rivais, o fim das campanhas e as linhas ativas no relatório comercial.')
    console.print('Investimentos e consequências de caixa são lançamentos separados do lucro operacional:')
    flows=[x for x in state.history if x['kind']=='caixa' and x['month']==month and x['amount']!=0]
    for x in flows:console.print(f"  {money(x['amount'])}: {x['text']}")
    console.print(f'Caixa atual (inclui ações e eventos posteriores): {money(state.player.cash)}')
    console.print('Últimos resultados: '+' | '.join(f"{1997+x['month']}: {money(x['companies']['player']['profit'])}" for x in state.reports[-6:]))


def competitors(console,state):
    t=table('Concorrentes — informações públicas',['Empresa','Caixa','Capacidade','Mercados','Pesquisa','Fatia'])
    for c in state.companies[1:]:
        t.add_row(c.name+(' [ENCERRADA]' if c.eliminated else ''),money(c.cash),str(capacity(c,state.balance)),str(len(c.regions)),str(c.innovation),f'{c.last_share:.1%}')
    console.print(t)
    for line in state.rival_history[-12:]:console.print(line)


def products(console,state):
    p=state.player
    console.print('Sabores: descrições de produtos reais; todos os atributos estratégicos são fictícios.',style='yellow')
    for key,product in catalog(state).items():
        status='ATIVO' if key in p.active else 'DISPONÍVEL' if key in p.products else 'PESQUISA'
        console.print(f"{product['name']} [{status}]",style=product['color'])
        console.print(f"  {product['description']}\n  Custo relativo {product['cost']:.2f}; atratividade {product['attraction']:.2f}. {product['special']}\n  Desbloqueio: {product['unlock']}")
        if product['affinity']:console.print('  Afinidades: '+', '.join(MARKETS[k]['name']+f' +{(v-1)*100:.0f}%' for k,v in product['affinity'].items()))


def effect_summary(effects):
    pieces=[]
    names={'cash':'caixa','chaos':'Caos','reputation':'reputação','capacity':'capacidade','damage':'dano','innovation':'pesquisa','efficiency':'eficiência','aggression':'agressividade','maintenance':'manutenção/ano'}
    for key,label in names.items():
        if key in effects:pieces.append(f"{label} {effects[key]:+g}")
    if 'royalty' in effects:pieces.append(f"royalties {effects['royalty']:+.0%} da receita")
    for e in effects.get('effects',[]):
        target=MARKETS[e['market']]['name'] if e.get('market') not in (None,'all') else 'todos os mercados'
        company=e.get('company','player')
        pieces.append(f"demanda {(e['value']-1):+.0%}, {e['duration']} ano(s), {target}"+(' (rival)' if company not in ('player','all') else ''))
    if 'unlock_market' in effects:pieces.append('abre '+MARKETS[effects['unlock_market']]['name'])
    if effects.get('schedule'):pieces.append('desdobramento futuro em '+', '.join(str(e['delay']) for e in effects['schedule'])+' ano(s)')
    if effects.get('ending'):pieces.append('ENCERRA A CAMPANHA com um final especial')
    return '; '.join(pieces) or 'Consequência narrativa registrada.'


def event_screen(console,state):
    event=EVENTS[state.pending_event]
    console.print(Panel(event['description'],title=event['title'],border_style='magenta',box=box.ASCII))
    console.print(f"DECISÃO DE {state.year} — não usa ação. Caixa: {money(state.player.cash)}")
    for i,option in enumerate(event['options'],1):
        console.print(f"\n[{i}] {option['label']} — {money(option['cost'])}",style='bright_green')
        console.print('    '+effect_summary(option['effects']))
        if option['risk']!='Sem risco adicional.':console.print('    Risco: '+option['risk'],style='yellow')
    console.print('\n[0] Salvar e sair; resolver depois')


def company_summary(console,state):
    """Uma consulta já aberta, sem escolher entre vários relatórios."""
    p=state.player
    console.print(Panel('CONSULTA — ler esta tela não muda a empresa e não gasta ações.',
                        title='SUA EMPRESA',box=box.ASCII,border_style='cyan'))
    if state.reports:
        r=state.reports[-1]['companies']['player']
        console.print(f"Receita {money(r['revenue'])} - despesas {money(r['expenses'])} = {money(r['profit'])}")
        console.print(f"Produção vendida: {r['sold']}/{r['capacity']} ({r['sold']/max(1,r['capacity']):.0%}).")
        if r['unmet']>0:console.print('Atenção: faltou produção para atender clientes.',style='yellow')
        elif r['sold']<.65*r['capacity']:console.print('Há capacidade ociosa. Busque clientes antes de construir.',style='yellow')
        best=max(r['regions'],key=lambda k:r['regions'][k]['contribution'])
        console.print(f"Maior contribuição: {MARKETS[best]['name']} ({money(r['regions'][best]['contribution'])}).")
    else:
        console.print('O primeiro resultado aparece ao avançar o ano.')
    console.print(f"Fábricas: {p.factories} | nível {p.level} | capacidade {capacity(p,state.balance)} | laboratório {p.innovation}")
    console.print('Mercados: '+', '.join(MARKETS[k]['name'] for k in p.regions))
    products=catalog(state)
    console.print('Sabores ativos: '+', '.join(products[k]['name'] for k in p.active))
    rivals=[c for c in state.companies[1:] if not c.eliminated]
    if rivals:
        console.print('Rivais: '+'; '.join(f'{c.name} {c.last_share:.0%}' for c in rivals))
    if state.scheduled:
        console.print('Uma decisão passada pode voltar a partir de '+str(1997+min(x['due'] for x in state.scheduled))+'.')
    if p.loan or p.royalty:
        console.print(f'Juros: {money(p.loan*.025)}/ano; royalties: {p.royalty:.0%} da receita.')


def achievements(console,profile):
    t=table(f"Conquistas: {len(profile['achievements'])}/{len(ACHIEVEMENTS)}",['Estado','Conquista','Como obter'])
    for key,(name,description) in ACHIEVEMENTS.items():t.add_row('OK' if key in profile['achievements'] else '--',name,description)
    console.print(t)
    names={'tema_roxo':'Roxo efervescente','tema_azul':'Azul congelante','mascote_rato':'Rato contador'}
    console.print('Cosméticos: '+(', '.join(names[k] for k in profile['unlocks'] if k in names) or '3 conquistas liberam o tema roxo; 7, azul; 12, o rato contador.'))


def campaign_history(console,profile):
    t=table('Histórico de campanhas',['Seed','Final','Anos','Patrimônio','Fatia'])
    for c in profile['campaigns'][-30:]:t.add_row(c['seed'],ENDINGS[c['ending']]['title'],str(c['months']),money(c['value']),f"{c['share']:.1%}")
    console.print(t)
    console.print(f"Receita total em campanhas encerradas: {money(profile['totals']['revenue'])}; finais descobertos: {len(profile['endings'])}/{len(ENDINGS)}.")


def finale(console,state,new_achievements):
    ending=ENDINGS[state.ending];p=state.player
    console.print(Panel(ending['title']+'\n\n'+ending['text'],title='PLUTONITA TIMES — EDIÇÃO FINAL',border_style=state.theme,box=box.ASCII))
    t=table('Balanço do império',['Indicador','Resultado'])
    for label,value in [('Seed',state.seed),('Anos concluídos',str(len(state.reports))),('Receita acumulada',money(state.stats['revenue'])),('Patrimônio estimado',money(valuation(p,state))),('Caixa final',money(p.cash)),('Participação global',f'{p.last_share:.1%}'),('Mercados abertos',f'{len(p.regions)}/8'),('Sabores lançados',str(len(p.products))),('Eventos enfrentados',str(state.stats['events'])),('Concorrentes encerrados',str(state.stats['defeated'])),('Caos final',f'{p.chaos:.0f}/100')]:t.add_row(label,value)
    console.print(t)
    console.print('Decisões memoráveis:',style='yellow')
    for line in state.decisions:console.print('  '+line)
    pending=[EVENTS[x['event']]['title'] for x in state.scheduled if 'event' in x]
    if pending:console.print('Depois da campanha, o conselho ainda terá de lidar com: '+', '.join(pending)+'.')
    console.print('Novas conquistas: '+(', '.join(ACHIEVEMENTS[k][0] for k in new_achievements) or 'nenhuma nesta sessão.'))
    console.print('Seu histórico foi preservado. Outras decisões e seeds abrem caminhos diferentes.')
