"""Pesquisa acumulada e receitas experimentais reproduzíveis."""
from random import Random
from .state import GameState

def experiment(state: GameState, rng: Random, traits: tuple[int,int,int,int]) -> dict:
    acid, temperature, fizz, strange=traits
    recipes={
        (1,1,1,2):("terca","Plutonita Sabor Terça-Feira"),
        (0,0,0,0):("nada","Plutonita Sabor de Nada"),
        (3,3,3,3):("definitivo","Plutonita Último Suspiro"),
        (3,3,2,2):("nuclear","Plutonita Nuclear Supreme"),
        (0,2,1,3):("croissant","Plutonita Croissant Radioativo"),
        (1,0,0,3):("imposto","Plutonita Sabor de Imposto"),
        (0,0,3,3):("buraco","Plutonita Buraco Negro")
    }
    key,name=recipes.get(traits,("arrependimento","Plutonita Gosto de Arrependimento"))
    identifier=f"exp_{len(state.experimental)+1}"
    quality=round(.94+.065*state.player.innovation+.035*(acid+fizz)+.05*strange+rng.uniform(-.06,.06),3)
    state.flags[f"recipe_{key}"]=True
    return {"id":identifier,"name":name,"description":f"Produto fictício. Acidez {acid}, temperatura {temperature}, efervescência {fizz}, estranheza {strange}.","category":"experimental" if strange>=2 else "popular","cost":round(.92+.06*sum(traits),2),"attraction":quality,"price_bonus":.03*temperature+.025*strange,"affinity":{"asia":1.2 if strange>=2 else 1,"west":1.18 if temperature>=2 else 1},"special":f"Caos +{strange*4}; qualidade depende do laboratório. Receita: {key}.","unlock":"Criação no laboratório.","events":["terca" if key=="terca" else "patente"],"fictional":True,"color":"cyan","traits":list(traits)}
