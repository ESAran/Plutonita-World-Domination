"""Orquestração transacional dos turnos, sem lógica de terminal."""
from random import Random
from uuid import uuid4
from .state import new_state
from .persistence import save_game, load_game
from .actions import execute, RuleError
from .competitors import take_turns
from .economy import simulate_month
from .events import choose_event, resolve_event, monthly_news, process_due
from .endings import select_ending, eligible_endings
from .markets import PRICES

class Game:
    def __init__(self, seed: str = "1998", balance: dict | None = None):
        self.state=new_state(str(seed),balance)
        self.state.campaign_id=str(uuid4())
        self.rng=Random(str(seed))
        self.prepare_month()

    def save(self,path): save_game(path,self.state,self.rng)

    @classmethod
    def load(cls,path):
        game=cls.__new__(cls)
        game.state,game.rng=load_game(path)
        return game

    def prepare_month(self):
        s=self.state
        s.news=[]
        s.effects=[e for e in s.effects if e['until']>=s.month]
        process_due(s,self.rng)
        if s.player.cash < -s.balance['bankruptcy_credit']:
            s.ending='bankrupt'; s.phase='finished'; return
        take_turns(s,self.rng)
        monthly_news(s,self.rng)
        if s.reports:
            p=s.reports[-1]['companies']['player']
            s.news.append(f"Plutonita vendeu {p['sold']} unidades; resultado R$ {p['profit']:+.2f}; participação {p['share']:.1%}.")
        s.flags['month_opening_cash']=s.player.cash

    def act(self,kind,target='',traits=None) -> str:
        message=execute(self.state,self.rng,kind,target,traits)
        if self.state.phase=='finished' and self.state.ending=='magnate':
            if 'magnate' not in eligible_endings(self.state): raise RuleError('A venda ainda não é elegível.')
        return message

    def configure(self,market: str,price: str,priority: int) -> None:
        if self.state.phase!='planning': raise RuleError('A configuração vale apenas antes do fechamento anual.')
        if market not in self.state.player.regions or price not in PRICES or type(priority) is not int or priority not in (1,2,3):
            raise RuleError('Mercado, preço ou prioridade inválido.')
        region=self.state.player.regions[market]
        region.price,region.priority=price,priority

    def set_active(self,identifiers: list[str]) -> None:
        if self.state.phase!='planning': raise RuleError('Altere as linhas durante o planejamento.')
        if not 1<=len(identifiers)<=self.state.balance['line_limit'] or len(set(identifiers))!=len(identifiers) or any(p not in self.state.player.products for p in identifiers):
            raise RuleError('Escolha de uma a três linhas distintas já desbloqueadas.')
        self.state.player.active=list(identifiers)

    def close_month(self) -> None:
        """Alias legado para ferramentas e saves da primeira versão."""
        self.close_year()

    def close_year(self) -> None:
        s=self.state
        if s.phase!='planning': raise RuleError('Resolva o evento pendente antes de continuar.')
        simulate_month(s)
        s.actions=0
        if s.player.cash < -s.balance['bankruptcy_credit']:
            s.ending='bankrupt'; s.phase='finished'; return
        if s.month%3==0:
            s.pending_event=choose_event(s,self.rng)
            if s.pending_event:
                s.phase='event'; return
        self.advance()

    def decide(self,choice: int) -> str:
        start=len(self.state.history)
        result=resolve_event(self.state,self.rng,choice)
        outcomes=[x['text'] for x in self.state.history[start:] if x['kind']=='risco']
        if outcomes:result+='\n'+'\n'.join(outcomes)
        s=self.state
        requested=s.flags.pop('requested_ending',None)
        if s.player.cash < -s.balance['bankruptcy_credit']:
            s.ending='bankrupt'; s.phase='finished'
        elif requested and requested in eligible_endings(s):
            s.ending=requested; s.phase='finished'
        else: self.advance()
        return result

    def advance(self):
        s=self.state
        if s.month>=s.balance['months']:
            s.ending=select_ending(s); s.phase='finished'
        else:
            s.month+=1; s.actions=s.balance['actions']; s.phase='planning'
            self.prepare_month()
