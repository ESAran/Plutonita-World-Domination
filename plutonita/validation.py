"""Validação estrutural de arquivos locais antes de restaurar uma campanha."""
import math
from .state import GameState
from .markets import MARKETS, PRICES
from .products import CLASSICS
from .balance import load_balance


def validate_state(state: GameState) -> None:
    # JSON não deve introduzir NaN, infinitos ou estruturas incompletas no motor.
    def finite(value):
        if isinstance(value,float) and not math.isfinite(value):raise ValueError('Número não finito no salvamento.')
        if isinstance(value,dict):
            for item in value.values():finite(item)
        elif isinstance(value,(list,tuple)):
            for item in value:finite(item)
    finite(state.to_dict())
    if not isinstance(state.seed,str) or not state.campaign_id:raise ValueError('Identificação de campanha ausente.')
    if set(state.balance)!=set(load_balance()):raise ValueError('Configuração incompleta no salvamento.')
    if any(type(value) not in (int,float) or value<(0 if key in ('reputation','chaos') else 1e-9) for key,value in state.balance.items()):raise ValueError('Configuração inválida no salvamento.')
    if state.balance['months']!=24 or state.balance['actions']!=2:raise ValueError('Duração ou ações inválidas.')
    if state.phase not in ('planning','event','finished'):raise ValueError('Fase desconhecida.')
    if type(state.month) is not int or not 1<=state.month<=24 or type(state.actions) is not int or not 0<=state.actions<=2:raise ValueError('Ano ou ações inválidas.')
    if [c.id for c in state.companies]!=['player','goma','sweet','bubble']:raise ValueError('Lista de empresas inválida.')
    products={**CLASSICS,**state.experimental}
    for key,product in state.experimental.items():
        if not key.startswith('exp_') or product.get('id')!=key:raise ValueError('Identificador experimental inválido.')
        for field in ('name','description','category','cost','attraction','price_bonus','affinity','special','unlock','events','color'):
            if field not in product:raise ValueError('Fórmula experimental incompleta.')
        if product['cost']<=0 or product['attraction']<=0:raise ValueError('Atributos comerciais inválidos.')
    for c in state.companies:
        if not isinstance(c.cash,(int,float)):raise ValueError('Caixa inválido.')
        if not 0<=c.reputation<=100 or not 0<=c.chaos<=100:raise ValueError('Indicador fora do intervalo 0–100.')
        if type(c.factories) is not int or not 1<=c.factories<=state.balance['max_factories']:raise ValueError('Número de fábricas inválido.')
        if type(c.level) is not int or not 1<=c.level<=state.balance['max_level']:raise ValueError('Nível de fábrica inválido.')
        if not 0<=c.efficiency<=5 or not 0<=c.innovation<=4:raise ValueError('Nível tecnológico inválido.')
        if min(c.extra_capacity,c.extra_maintenance,c.damage,c.loan,c.royalty,c.aggression)<0:raise ValueError('Ativo ou dívida com sinal inválido.')
        if not c.regions or any(k not in MARKETS for k in c.regions):raise ValueError('Mercado desconhecido.')
        for region in c.regions.values():
            if region.price not in PRICES or region.priority not in (1,2,3) or not 0<=region.recognition<=100 or not 0<=region.marketing<=180:raise ValueError('Configuração comercial inválida.')
        if len(c.products)!=len(set(c.products)) or any(k not in products for k in c.products):raise ValueError('Catálogo de produtos inválido.')
        if not 1<=len(c.active)<=state.balance['line_limit'] or len(set(c.active))!=len(c.active) or any(k not in c.products for k in c.active):raise ValueError('Linhas de produção inválidas.')
    from .events import EVENTS
    from .endings import ENDINGS
    if any(key not in EVENTS for key in state.seen) or len(set(state.seen))!=len(state.seen):raise ValueError('Histórico de eventos inválido.')
    if state.stats['events']!=len(state.seen):raise ValueError('Contagem narrativa inconsistente.')
    if state.phase=='event' and state.pending_event not in EVENTS:raise ValueError('Evento pendente ausente.')
    if state.phase!='event' and state.pending_event is not None:raise ValueError('Evento fora da fase de decisão.')
    if state.phase=='finished' and state.ending not in ENDINGS:raise ValueError('Final desconhecido.')
    for item in state.scheduled:
        if type(item.get('due')) is not int or item['due']<1:raise ValueError('Agenda inválida.')
        if 'event' in item and item['event'] not in EVENTS:raise ValueError('Capítulo agendado desconhecido.')
        if 'event' not in item and 'effects' not in item:raise ValueError('Consequência agendada ausente.')
    for effect in state.effects:
        if effect.get('kind')!='demand' or effect.get('value',0)<=0 or type(effect.get('until')) is not int:raise ValueError('Efeito comercial inválido.')
    if state.theme not in ('green','magenta','cyan'):raise ValueError('Tema visual inválido.')
