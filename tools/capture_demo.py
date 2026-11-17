#!/usr/bin/env python3
"""Renderiza telas reais da interface em PNG, sem alterar o save do jogador.

Ferramenta opcional: requer Pillow e uma fonte monoespaçada local.
"""
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.text import Text
from rich.terminal_theme import TerminalTheme
from plutonita.game import Game
from plutonita.ui.dashboard import dashboard
from plutonita.ui.ascii_art import LOGO
from plutonita.ui.menus import Terminal
from plutonita.ui import reports
from plutonita.achievements import update_profile
from plutonita.persistence import empty_profile
from tools.simulate import Agent

OUT = Path('reports/prints')
FONT_PATH = Path('/System/Library/Fonts/Menlo.ttc')
THEME = TerminalTheme(
    (15, 20, 25), (224, 231, 238),
    [(27,32,40),(242,105,105),(110,224,120),(245,211,112),
     (113,164,245),(204,139,237),(104,209,220),(224,231,238)],
    [(118,133,148),(255,133,133),(153,245,129),(255,229,148),
     (144,188,255),(224,169,255),(137,234,244),(255,255,255)],
)
FONT = ImageFont.truetype(str(FONT_PATH), 20)
CELL = FONT.getlength('M')
ROW = 28
PAD = 26


def capture(name, render):
    output = io.StringIO()
    console = Console(file=output, width=80, force_terminal=True,
                      color_system='truecolor', no_color=False, highlight=False, markup=False)
    render(console)
    ansi = output.getvalue()
    text = Text.from_ansi(ansi)
    lines = text.split('\n', allow_blank=True)
    while lines and not lines[-1].plain:
        lines.pop()
    canvas = Image.new('RGB', (round(CELL * 80) + PAD * 2, len(lines) * ROW + PAD * 2), THEME.background_color)
    draw = ImageDraw.Draw(canvas)
    for row, line in enumerate(lines):
        x = PAD
        y = PAD + row * ROW
        for segment in line.render(console):
            style = segment.style
            foreground = THEME.foreground_color
            background = THEME.background_color
            if style and style.color:
                foreground = style.color.get_truecolor(THEME)
            if style and style.bgcolor:
                background = style.bgcolor.get_truecolor(THEME, foreground=False)
            if style and style.reverse:
                foreground, background = background, foreground
            if style and style.dim:
                foreground = tuple(round(a * .58 + b * .42) for a,b in zip(foreground, background))
            width = FONT.getlength(segment.text)
            if background != THEME.background_color:
                draw.rectangle((x,y,x+width,y+ROW),fill=background)
            draw.text((x,y),segment.text,font=FONT,fill=foreground)
            if style and style.underline:
                draw.line((x,y+24,x+width,y+24),fill=foreground)
            x += width
    canvas.save(OUT / f'{name}.png')
    (OUT / f'{name}.txt').write_text(text.plain,encoding='utf-8')
    print(name,canvas.size)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    game=Game('1000')
    agent=Agent('expansao','1000')
    profile=empty_profile()
    achievements=[]
    trace=[]
    capture('01_inicio',lambda c: (c.print(LOGO,style='bright_green'),dashboard(c,game.state)))
    with TemporaryDirectory(prefix='plutonita-prints-') as temporary:
        def action_screen(console):
            terminal=Terminal(console,Path(temporary),game.state.balance,clear=False)
            terminal.game=game
            def go_back(prompt,minimum,maximum,allowed=None):
                console.print(prompt,end='')
                return 0
            terminal.number=go_back
            terminal.action_menu('production')
        capture('02_producao',action_screen)
    while game.state.phase!='finished':
        state=game.state
        if state.phase=='event':
            if state.pending_event=='pernas':
                capture('04_fabrica_fugiu',lambda c: reports.event_screen(c,state))
            elif state.pending_event=='gravida':
                capture('05_consequencia',lambda c: reports.event_screen(c,state))
            choice=agent.event_choice(game)
            trace.append({'ano':state.year,'evento':state.pending_event,'opcao':choice+1})
            game.decide(choice)
            achievements.extend(update_profile(profile,state))
            continue
        if state.month==2:
            capture('03_primeiro_fechamento',lambda c: reports.finances(c,state))
        if state.month==19:
            capture('06_crescimento',lambda c: dashboard(c,state))
        agent.configure(game)
        for _ in range(2):
            choice=agent.choose_action(game)
            if choice:
                trace.append({'ano':state.year,'acao':list(choice)})
                game.act(*choice)
        game.close_month()
        achievements.extend(update_profile(profile,state))
    capture('07_final',lambda c:reports.finale(c,state,achievements))
    (OUT/'partida.json').write_text(json.dumps({'seed':state.seed,'estrategia':'expansao','final':state.ending,'participacao':state.player.last_share,'decisoes':trace},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
