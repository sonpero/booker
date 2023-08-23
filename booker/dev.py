import requests

# Définir le titre et l'auteur du livre
titre_livre = "Le Petit Prince"
auteur_livre = "Antoine de Saint-Exupéry"

titre_livre = 'Une brève histoire du temps, du Big-bang aux trous noirs'
auteur_livre = 'Stephen William Hawking'

# Effectuer la requête à l'API Google Books
url = "https://www.googleapis.com/books/v1/volumes?q=intitle:" + titre_livre + "+inauthor:" + auteur_livre
response = requests.get(url)

# Extraire l'URL de l'image de couverture du livre à partir de la réponse JSON
data = response.json()
if data['totalItems'] > 0:
    livre = data['items'][4]['volumeInfo']
    titre = livre['title']
    auteurs = livre['authors']
    date_parution = livre['publishedDate']
    resume = livre['description']
    image_url = livre['imageLinks']['thumbnail']

    # Télécharger l'image de couverture du livre
    response = requests.get(image_url)
    with open(titre + ".jpg", "wb") as f:
        f.write(response.content)

    # Afficher les informations du livre
    print("Titre: ", titre)
    print("Auteur(s): ", auteurs)
    print("Date de parution: ", date_parution)
    print("Résumé: ", resume)
    print("URL de l'image de couverture: ", image_url)
    print("L'image de couverture a été enregistrée sous le nom", titre + ".jpg")
else:
    print("Aucun livre trouvé avec ce titre et cet auteur.")


class MaClasse:
    def __init__(self):
        self.mes_methodes = {}

    def __getattr__(self, nom):
        if nom in self.mes_methodes:
            return self.mes_methodes[nom]
        else:
            raise AttributeError(f"{self.__class__.__name__} n'a pas l'attribut {nom}")

    def ajouter_methode(self, nom, fonction):
        self.mes_methodes[nom] = fonction
        setattr(self, nom, fonction)

# Exemple d'utilisation
def ma_methode(self):
    print("Ma méthode a été appelée !")

obj = MaClasse()
obj.ajouter_methode("ma_methode", ma_methode)
obj.ma_methode()

# Maintenant, l'IDE devrait être en mesure de reconnaître la méthode "ma_methode" lorsqu'elle est appelée sur l'objet "obj"


def func1():
    print('func1')


def func2():
    print('func2')


mes_methodes = {'function_1' : func1, 'function_2' : func2}

class MaClasse:
    mes_methodes = {'function_1': func1, 'function_2': func2}

    def __getattr__(self, nom):
        if nom in self.mes_methodes:
            return self.mes_methodes[nom]
        else:
            raise AttributeError(f"{self.__class__.__name__} n'a pas l'attribut {nom}")

class MaClasse:
    def __init__(self):
        self.mes_methodes = {}

    def __getattr__(self, nom):
        if nom in self.mes_methodes:
            return self.mes_methodes[nom]
        else:
            raise AttributeError(f"{self.__class__.__name__} n'a pas l'attribut {nom}")

    def ajouter_methode(self, nom, fonction):
        self.mes_methodes[nom] = fonction
        setattr(self, nom, fonction)

# Exemple d'utilisation
def ma_methode(self):
    print("Ma méthode a été appelée !")

obj = MaClasse()
obj.ajouter_methode("ma_methode", ma_methode.__get__(obj, MaClasse))

# Maintenant, l'appel de la méthode 'ma_methode' sur l'objet 'obj' ne devrait plus causer l'erreur "TypeError: ma_methode() missing 1 required positional argument: 'self'"
obj.ma_methode()
obj.ma_


toto = data['items'][0]['imageLinks']['thumbnail']
type(toto)
print(toto)

for element in toto:
    print(element)
len(toto)

type(data)
print(data)

ImageField