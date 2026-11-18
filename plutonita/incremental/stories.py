"""Primeiras histórias do protótipo; o tom será revisado com o jogador."""

EVENTS = {
    "walking": {
        "title": "FÁBRICA CRUZA A FRONTEIRA SEM DECLARAR A SI MESMA",
        "body": "Uma instalação desenvolveu pernas durante o inventário e chegou ao Uruguai. "
                "Ela continua produzindo. O terreno no Brasil está vazio, mas insiste em receber correspondência.",
        "options": [
            {"label": "Reconhecer a filial uruguaia", "cost": 0,
             "detail": "Abre a América Latina sem custo; domínio local +15 pontos; caos +12. "
                       "A fábrica pode voltar a tomar decisões próprias.",
             "effects": {"market": "latam", "presence": 15, "chaos": 12,
                         "flags": {"walking": True}, "schedule": (3, "family")}},
            {"label": "Comprar o terreno onde ela parou", "cost": 1200,
             "detail": "Abre a América Latina; domínio local +10 pontos. Caos -5. "
                       "A instalação aceita um endereço fixo.",
             "effects": {"market": "latam", "presence": 10, "chaos": -5,
                         "flags": {"settled": True}}},
            {"label": "Repatriar a instalação", "cost": 0,
             "detail": "Caos -8; sem filial. Renda -10% apenas no próximo ano, durante a viagem.",
             "effects": {"chaos": -8, "flags": {"travel_year": True}}},
        ],
    },
    "family": {
        "title": "FÁBRICA RETORNA COM UMA INSTALAÇÃO MENOR",
        "body": "A filial uruguaia voltou acompanhada. Não há nota fiscal, projeto ou licença de construção. "
                "As duas instalações aguardam uma decisão sobre o vínculo societário.",
        "options": [
            {"label": "Incorporar a nova fábrica", "cost": 2400,
             "detail": "+1 fábrica; caos -5. O patrimônio volta a ter proprietário definido.",
             "effects": {"unit": "factory", "chaos": -5}},
            {"label": "Reconhecer a autonomia das instalações", "cost": 0,
             "detail": "+1 fábrica; renda +20%; caos +3 por ano. Abre uma sequência sobre "
                       "quem controla a companhia. Haverá uma última decisão em 3 anos.",
             "effects": {"unit": "factory", "flags": {"autonomous": True},
                         "schedule": (3, "charter")}},
            {"label": "Aceitar apenas a fábrica original", "cost": 0,
             "detail": "Caos -10. A instalação menor abre uma empresa própria e segue viagem.",
             "effects": {"chaos": -10}},
        ],
    },
    "charter": {
        "title": "INSTALAÇÕES APRESENTAM UMA CONSTITUIÇÃO",
        "body": "As fábricas autônomas exigem reconhecimento como uma federação. "
                "O documento inclui as filiais ainda não construídas. Esta decisão define quem será dono do império.",
        "options": [
            {"label": "Ratificar a federação", "cost": 0,
             "detail": "Irreversível: final Federação das Fábricas no encerramento. "
                       "A campanha continua, mas o final perfeito deixa de ser possível. Caos -20.",
             "effects": {"chaos": -20, "flags": {"federation": True, "autonomous": False}}},
            {"label": "Recuperar o controle da empresa", "cost": 0,
             "detail": "Abre mão do bônus de renda de 20%; caos -15. Mantém a rota de dominação mundial.",
             "effects": {"chaos": -15, "flags": {"autonomous": False}}},
        ],
    },
    "critical": {
        "title": "A EMPRESA COMEÇOU A ASSINAR PELOS DIRETORES",
        "body": "Dois fechamentos seguidos com caos crítico. As assinaturas são autênticas, "
                "inclusive as dos diretores que se recusaram a assinar. "
                "Se o caos permanecer em 75 ou mais por quatro anos consecutivos, você perde o controle definitivamente.",
        "options": [
            {"label": "Encerrar permanentemente os projetos instáveis", "cost": 0,
             "detail": "Caos -40; encerra aumentos anuais de caos. Perde o bônus Atomic de 35%, "
                       "metade da renda orbital e novas compras orbitais. Mantém o restante do império.",
             "effects": {"chaos": -40, "flags": {"sealed": True}}},
            {"label": "Manter a produção experimental", "cost": 0,
             "detail": "Preserva os bônus. Mais 2 fechamentos críticos causam uma derrota irreversível; "
                       "a redução anual de Abraço Congelante pode não ser suficiente.",
             "effects": {}},
        ],
    },
    "audit": {
        "title": "AUDITORIA ENCONTRA UM ANDAR SEM LADO DE FORA",
        "body": "O novo andar cabe dentro do galpão e tem um galpão dentro dele. "
                "A equipe de medição pede para interromper a contagem antes de encontrar a si mesma.",
        "options": [
            {"label": "Usar o espaço para produção", "cost": 0,
             "detail": "Fábricas rendem +20% permanentemente; caos +18.",
             "effects": {"chaos": 18, "flags": {"extra_floor": True}}},
            {"label": "Lacrar o acesso", "cost": 0,
             "detail": "Caos -8. A produção atual continua funcionando.",
             "effects": {"chaos": -8}},
        ],
    },
    "forecast": {
        "title": "PESQUISA ENTREVISTA CLIENTES DO PRÓXIMO ANO",
        "body": "Os consumidores descrevem um lançamento que ainda não foi aprovado. "
                "Todos se lembram da mesma coletiva de imprensa, inclusive do acidente.",
        "options": [
            {"label": "Antecipar a distribuição", "cost": 1500,
             "detail": "Presença cresce +20% nos mercados abertos; caos +15.",
             "effects": {"chaos": 15, "flags": {"future_sales": True}}},
            {"label": "Arquivar o estudo", "cost": 0,
             "detail": "Caos -5. Mantém o plano de expansão atual.",
             "effects": {"chaos": -5}},
        ],
    },
}
