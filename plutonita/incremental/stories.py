"""Manchete, decisão e consequência. Premissas calibradas com o jogador.

O catálogo anterior só permanece para retomar jornais e capítulos de saves antigos.
"""

LEGACY_EVENTS = {
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


STORIES = {
    "walking_v2": {
        "title": "FÁBRICA CRIA PERNAS E FOGE PRO URUGUAI",
        "body": "A fábrica arrancou os próprios alicerces e atravessou a fronteira durante a madrugada. "
                "Já está produzindo no Uruguai. Os funcionários foram junto porque o relógio de ponto estava lá dentro.",
        "options": [
            {"label": "Deixar que abra uma filial", "cost": 0,
             "detail": "América Latina +20 pontos de domínio; renda +10% com a filial em pesos, "
                       "convertida automaticamente. Caos +12. Retorno em 3 anos com despesas de 25% do caixa.",
             "effects": {"market": "latam", "presence": 20, "chaos": 12,
                         "flags": {"walking": True, "peso_income": True}, "schedule": (3, "pregnancy")}},
            {"label": "Mandar capturar a fábrica", "cost": 0,
             "detail": "Caos -8; renda -10% no próximo ano durante o transporte. Não abre a filial.",
             "effects": {"chaos": -8, "flags": {"travel_year": True}}},
        ],
    },
    "pregnancy": {
        "title": "FÁBRICA VOLTA GRÁVIDA DO URUGUAI",
        "body": "A filial voltou com três galpões no ultrassom. A Plutonita já pagou o reforço da fundação "
                "e perdeu a renda em pesos. A fábrica se recusa a dizer qual empresa uruguaia é o pai. "
                "Você ficou com a conta e uma lista de suspeitos.",
        "arrival": {"cash_loss": .25, "flags": {"peso_income": False}},
        "arrival_detail": "Obras e despesas da gravidez: 25% do caixa após a receita anual. "
                          "O bônus em pesos termina; o domínio na América Latina permanece.",
        "options": [
            {"label": "Investigar qual empresa uruguaia é o pai", "cost": 1200,
             "detail": "Em 2 anos, a investigação identifica o pai e abre uma negociação. "
                       "As despesas já pagas não são devolvidas agora.",
             "effects": {"schedule": (2, "paternity")}},
            {"label": "Assumir a família industrial", "cost": 0,
             "detail": "+1 fábrica; caos +12; sem reembolso. As instalações recebem autonomia, "
                       "renda +20% e caos +3/ano. Em 3 anos, elas decidem discutir quem manda.",
             "effects": {"unit": "factory", "chaos": 12, "flags": {"autonomous": True},
                         "schedule": (3, "factory_family")}},
            {"label": "Mandar os advogados atrás do pai", "cost": 0,
             "detail": "Caos -5. Encerra a história sem nova fábrica ou recuperação do prejuízo.",
             "effects": {"chaos": -5}},
        ],
    },
    "paternity": {
        "title": "TESTE DE CONCRETO IDENTIFICA PAI URUGUAIO",
        "body": "A investigação chegou à Goma del Plata. A empresa nega tudo, mas uma das filiais "
                "nasceu com o logotipo dela na fachada. O dono oferece dinheiro para encerrar o assunto. "
                "Também aceita discutir guarda compartilhada.",
        "options": [
            {"label": "Cobrar a parte dele nas despesas", "cost": 0,
             "detail": "Recebe R$ 4.000; caos -5. Encerra a disputa de paternidade.",
             "effects": {"cash_gain": 4000, "chaos": -5}},
            {"label": "Aceitar guarda compartilhada", "cost": 0,
             "detail": "+1 fábrica e +10 pontos na América Latina. Toda a categoria de fábricas "
                       "rende -15%: nos fins de semana as instalações trabalham para o pai.",
             "effects": {"unit": "factory", "market": "latam", "presence": 10,
                         "flags": {"shared_custody": True}}},
        ],
    },
    "factory_family": {
        "title": "FÁBRICAS DECIDEM QUE VOCÊ NÃO É O PAI DELAS",
        "body": "Depois de pagar a gravidez e deixar as instalações crescerem por conta própria, "
                "você recebeu uma reunião de família. As fábricas querem formar uma federação. "
                "Sua presença será permitida, mas suas ordens não.",
        "options": LEGACY_EVENTS["charter"]["options"],
    },
    "counterfeit": {
        "title": "PLUTONITA ORIGINAL COMEÇA A CAÇAR FALSIFICAÇÕES",
        "body": "Seus chicletes desenvolveram dentes e invadiram os depósitos concorrentes. "
                "As embalagens falsificadas estão sendo encontradas vazias. "
                "Os distribuidores querem saber se devem alimentar o estoque.",
        "options": [
            {"label": "Deixar os chicletes caçarem", "cost": 0,
             "detail": "Crescimento de domínio +15%; caos +10. Em 3 anos, os predadores ficam sem falsificações.",
             "effects": {"chaos": 10, "flags": {"predators": True}, "schedule": (3, "hungry_stock")}},
            {"label": "Criar um lote de predadores maiores", "cost": 1800,
             "detail": "Crescimento de domínio +30%; caos +20. A comida acaba em 2 anos, "
                       "e o lote maior será mais caro de recolher.",
             "effects": {"chaos": 20, "flags": {"predators": True, "big_predators": True},
                         "schedule": (2, "hungry_stock")}},
            {"label": "Recolher o lote com dentes", "cost": 0,
             "detail": "Caos -5. Mantém as vendas e a concorrência como estavam.",
             "effects": {"chaos": -5}},
        ],
    },
    "hungry_stock": {
        "title": "ACABARAM AS FALSIFICAÇÕES. O ESTOQUE CONTINUA COM FOME",
        "body": "Os chicletes predadores comeram a concorrência disponível e começaram a abrir "
                "as caixas dos outros sabores da Plutonita. A equipe do depósito está negociando "
                "a retirada de pertences pessoais antes de abandonar o prédio.",
        "options": [
            {"label": "Recolher os predadores", "cost": 0,
             "detail": "Perde 10% do caixa (20% com o lote maior); encerra o bônus de domínio; caos -15.",
             "effects": {"cash_loss": .10, "big_predator_loss": .20, "chaos": -15,
                         "flags": {"predators": False, "big_predators": False}}},
            {"label": "Deixar que escolham quais sabores são legítimos", "cost": 0,
             "detail": "Mantém o bônus de domínio. Caos +15; renda -20% permanentemente "
                       "porque os predadores passam a comer parte da produção.",
             "effects": {"chaos": 15, "flags": {"stock_eaten": True}}},
        ],
    },
    "elimar": {
        "title": "ELIMAR GONZALES TRABALHA EM SETE PAÍSES TODOS OS DIAS",
        "body": "Elimar cumpre expediente presencial em sete países e mantém uma família em cada um. "
                "Nenhuma conhece as outras. Ele nunca atrasou uma entrega e pediu apenas que "
                "a empresa parasse de tentar tirar fotos dele.",
        "options": [
            {"label": "Promover Elimar e publicar uma homenagem", "cost": 0,
             "detail": "Renda +30%. A homenagem sai no próximo jornal; Elimar avisou que "
                       "expor sua identidade pode acabar com a operação nos sete países.",
             "effects": {"flags": {"elimar_promoted": True}, "schedule": (1, "elimar_pensions")}},
            {"label": "Dar uma gratificação sem divulgar", "cost": 800,
             "detail": "Renda +20% permanente. O nome de Elimar fica fora do jornal.",
             "effects": {"flags": {"elimar_discreet": True}}},
            {"label": "Deixar Elimar trabalhar em paz", "cost": 0,
             "detail": "Mantém a renda atual e o segredo. Nenhum bônus ou penalidade.",
             "effects": {}},
        ],
    },
    "elimar_pensions": {
        "title": "SETE FAMÍLIAS RECONHECEM ELIMAR NA HOMENAGEM DA PLUTONITA",
        "body": "As famílias descobriram tudo pela campanha do funcionário do mês. "
                "Elimar faliu pagando pensões e deixou de aparecer nos sete países. "
                "A empresa perdeu o bônus de produtividade e vende 15% menos sem ele.",
        "arrival": {"flags": {"elimar_promoted": False, "elimar_gone": True}},
        "arrival_detail": "A promoção perdeu o bônus de 30%; a renda agora sofre redução de 15% pela ausência de Elimar.",
        "options": [
            {"label": "Bancar um acordo para ele voltar", "cost": 0,
             "detail": "Gasta 30% do caixa; remove a penalidade de 15%. "
                       "Elimar volta sem o bônus da promoção e sem autorizar novas fotos.",
             "effects": {"cash_loss": .30, "flags": {"elimar_gone": False}}},
            {"label": "Contratar substitutos e aceitar o prejuízo", "cost": 0,
             "detail": "Mantém renda -15% pelo restante da campanha. "
                       "Sete funcionários ainda não conseguem cobrir tudo que Elimar fazia.",
             "effects": {}},
        ],
    },
    "court": {
        "title": "STF TENTA PROIBIR A PLUTONITA",
        "body": "Alemandre de Xoraes mandou apreender a Plutonita. "
                "O laboratório propõe enviar uma Plutonita assassina para engolir o ministro "
                "e assumir o lugar dele. O comercial prefere mandar um carregamento de presente.",
        "options": [
            {"label": "Enviar a Plutonita assassina", "cost": 3500,
             "detail": "65%: a substituta derruba a proibição e a renda sobe 15%. "
                       "35%: ela é apreendida, vira fiscal do tribunal e reduz a renda em 25%. "
                       "Caos +15 em qualquer resultado.",
             "effects": {"chaos": 15, "chance": {
                 "probability": .65,
                 "success": {"flags": {"court_ally": True},
                             "result": "PLUTONITA ASSUME O LUGAR DE ALEMANDRE DE XORAES. "
                                       "A proibição caiu. O novo ministro exige que parem de oferecer chiclete nas sessões."},
                 "failure": {"flags": {"court_predator": True}, "schedule": (2, "court_inspection"),
                             "result": "PLUTONITA ASSASSINA É CONTRATADA PELO TRIBUNAL. "
                                       "Sua criação agora apreende sua própria mercadoria. Renda -25%."},
             }}},
            {"label": "Pagar os caras em Plutonita", "cost": 1800,
             "detail": "Evita a proibição; renda +10%; caos +8. "
                       "Em 2 anos chega outro pedido, dessa vez em toneladas.",
             "effects": {"chaos": 8, "flags": {"court_supply": True}, "schedule": (2, "court_tonnes")}},
            {"label": "Recolher o lote que motivou a proibição", "cost": 0,
             "detail": "Paga 10% do caixa pelo recolhimento; caos -8. Mantém a renda futura.",
             "effects": {"cash_loss": .10, "chaos": -8}},
        ],
    },
    "court_tonnes": {
        "title": "TRIBUNAL DEVOLVE CAMINHÃO VAZIO E PEDE MAIS",
        "body": "O carregamento enviado para resolver a proibição acabou. "
                "O novo pedido veio em toneladas e já inclui o endereço de entrega para o ano seguinte. "
                "Você conseguiu transformar um problema político em um cliente que não paga.",
        "options": [
            {"label": "Aceitar o fornecimento permanente", "cost": 0,
             "detail": "Perde o bônus de 10% e passa a ter renda -10% pelo estoque entregue. "
                       "Encerra os pedidos como decisões anuais.",
             "effects": {"flags": {"court_supply": False, "court_tithe": True}}},
            {"label": "Encerrar o acordo e pagar o recolhimento", "cost": 0,
             "detail": "Perde 15% do caixa e o bônus de 10%; mantém a renda normal dali em diante.",
             "effects": {"cash_loss": .15, "flags": {"court_supply": False}}},
        ],
    },
    "court_inspection": {
        "title": "SUA PLUTONITA ASSASSINA VOLTA COM MANDADO DE APREENSÃO",
        "body": "A criatura enviada para substituir o ministro virou fiscal. "
                "Ela conhece todos os seus depósitos porque foi criada dentro de um. "
                "O laboratório diz que ainda consegue atraí-la de volta. O comercial sugere mudar de endereço.",
        "options": [
            {"label": "Financiar a captura da própria criação", "cost": 0,
             "detail": "Perde 20% do caixa; encerra a redução de renda de 25%; caos -10.",
             "effects": {"cash_loss": .20, "chaos": -10, "flags": {"court_predator": False}}},
            {"label": "Conviver com as apreensões", "cost": 0,
             "detail": "Mantém renda -25% pelo restante da campanha. Nenhuma nova cobrança para resolver este caso.",
             "effects": {}},
        ],
    },
}

EVENTS = {**LEGACY_EVENTS, **STORIES}

# Notas curtas só antecipam temas aprovados ou refletem fatos já ocorridos.
# A condição evita publicar gravidez, pensões ou infiltração numa rota que não as teve.
NEWS = (
    {"text": "Falsificadores de Plutonita recomendam não deixar o original perto da imitação."},
    {"text": "Fabricantes de chicletes recusam teste de paternidade envolvendo instalações industriais."},
    {"text": "Transportadora exige saber se a fábrica vai no caminhão ou seguindo o caminhão."},
    {"text": "Filial uruguaia segue recebendo em pesos e remetendo os lucros para a matriz.",
     "flags": ("peso_income",)},
    {"text": "Elimar Gonzales recusa entrevista sobre produtividade. Pela sétima vez no mesmo dia.",
     "flags": ("elimar_discreet",)},
    {"text": "Sete pensões vencem no mesmo dia. Elimar Gonzales cancela qualquer interesse em voltar a ser famoso.",
     "flags": ("elimar_gone",)},
    {"text": "Depósito separa estoque por sabor e por tamanho dos dentes.", "flags": ("predators",)},
    {"text": "Goma del Plata busca as instalações na sexta-feira. A devolução fica para segunda.",
     "flags": ("shared_custody",)},
    {"text": "Alemandre de Xoraes cancela sessão após grudar no próprio paletó.", "flags": ("court_ally",)},
    {"text": "Tribunal exige que o próximo carregamento venha sem nota de agradecimento.",
     "flags": ("court_supply",)},
)
