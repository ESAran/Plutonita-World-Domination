"""Conquistas, recordes e progressão exclusivamente cosmética."""
from pathlib import Path
from .production import valuation
from .persistence import atomic_json
from .state import GameState
ACHIEVEMENTS={
 'first_month':('A Firma Existe','Concluir o primeiro fechamento.'),
 'million':('Primeiro Milhão','Somar R$ 1 milhão em receitas entre campanhas.'),
 'lord':('Senhor dos Chicletes','Chegar a 25% de participação global.'),
 'latam':('Rei da América Latina','Vender 35% da demanda no Brasil e na América Latina.'),
 'witch':('Doutor em Baba de Bruxa','Pesquisar Baba de Bruxa e chegar ao laboratório 3.'),
 'fast_fail':('Falência Recorde','Encerrar por falência até o ano 6.'),
 'zombie':('Amigo dos Zumbis','Financiar o plano odontológico dos zumbis.'),
 'dentists':('Inimigo dos Dentistas','Apoiar o sindicato dos dentes de leite.'),
 'factory':('A Fábrica É Minha Amiga','Acolher a família de fábricas.'),
 'emperor':('Imperador da Goma','Encontrar o final imperial.'),
 'last':('O Último Sabor','Concluir o Sabor Definitivo.'),
 'global':('Passaporte Pegajoso','Operar nos oito mercados.'),
 'classic':('Coleção Radioativa','Desbloquear os sete sabores clássicos.'),
 'scientist':('Doutorado Autoconcedido','Criar três produtos experimentais.'),
 'chaos':('Auditor da Realidade','Chegar a 90 de Caos.'),
 'trusted':('Nome Limpo, Língua Verde','Atingir reputação 95.'),
 'acquisition':('Crianças Fora do Sobretudo','Adquirir ou fundir com um concorrente.'),
 'moon':('Exportador Lunar','Assinar um contrato com a Lua.'),
 'republic':('Cidadão Mastigável','Reconhecer a República da Goma.'),
 'survive':('Vinte e Quatro Fechamentos','Concluir os 24 anos sem falência.')
}

def earned(state: GameState, profile: dict) -> list[str]:
    p=state.player; f=state.flags; last=state.reports[-1]['companies']['player']['regions'] if state.reports else {}
    checks={
        'first_month':bool(state.reports),'million':profile['totals']['revenue']>=1_000_000,
        'lord':p.last_share>=.25,'latam':all(last.get(k,{}).get('share',0)>=.35 for k in ('br','latam')),
        'witch':'baba' in p.products and p.innovation>=3,'fast_fail':state.ending=='bankrupt' and state.month<=6,
        'zombie':f.get('zombie_friend'),'dentists':f.get('dentist_enemy'),'factory':f.get('factory_family'),
        'emperor':state.ending=='emperor','last':state.ending=='definitive','global':len(p.regions)==8,
        'classic':len(set(p.products)&{'lingua','baba','dentada','abraco','abobora','zumbi','atomic'})==7,
        'scientist':len(state.experimental)>=3,'chaos':p.chaos>=90,'trusted':p.reputation>=95,
        'acquisition':any(c.eliminated for c in state.companies[1:]) and p.aggression>=3,
        'moon':f.get('moon_partner'),'republic':state.ending=='republic',
        'survive':state.month==24 and state.phase=='finished' and state.ending!='bankrupt'
    }
    return [key for key,value in checks.items() if value]


def update_profile(profile: dict, state: GameState, path: Path | None = None) -> list[str]:
    if state.phase=='finished' and not any(c['id']==state.campaign_id for c in profile['campaigns']):
        profile['campaigns'].append({'id':state.campaign_id,'seed':state.seed,'ending':state.ending,'months':len(state.reports),'value':valuation(state.player,state),'share':state.player.last_share,'revenue':round(state.stats['revenue'],2),'chaos':state.player.chaos})
        profile['totals']['revenue']+=state.stats['revenue']
        profile['totals']['months']+=len(state.reports)
        if state.ending not in profile['endings']: profile['endings'].append(state.ending)
    new=[key for key in earned(state,profile) if key not in profile['achievements']]
    profile['achievements'].extend(new)
    for key,value in {'value':valuation(state.player,state),'share':state.player.last_share,'revenue':state.stats['revenue']}.items():
        profile['records'][key]=max(profile['records'].get(key,0),value)
    for threshold,unlock in ((3,'tema_roxo'),(7,'tema_azul'),(12,'mascote_rato')):
        if len(profile['achievements'])>=threshold and unlock not in profile['unlocks']: profile['unlocks'].append(unlock)
    if path: atomic_json(path,profile)
    return new
