import gamecode
import kivy
from kivy.lang import Builder
from kivy.app import App
import random as rd
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
import time
import sqlite3




# Autodidacte


# rempli NAV_J à voir, mais ça devrait le faire ez normalement.




# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('BDD_BatailleNavale.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table
create_M_query = '''
    CREATE TABLE IF NOT EXISTS M
   (
    N_M NUMBER(4)  NOT NULL,
    VAINQUEUR VARCHAR2(2)  NULL,
    DUREE DATE  NULL,
    NB_COUPS NUMBER(4)  NOT NULL,
    NIVEAU VARCHAR2(4)  NULL,
    JOUEUR VARCHAR2(10)  NULL,
    CONSTRAINT PK_M PRIMARY KEY (N_M)
   ) ;
'''
create_NAV_J_query = '''
CREATE TABLE IF NOT EXISTS NAV_J
   (
    N1 NUMBER(8) NOT NULL,
    N_J NUMBER(4)  NOT NULL,
    NOM VARCHAR2(10)  NULL,
    N_B NUMBER(2)  NOT NULL,
    B_X NUMBER(1),
    B_Y NUMBER(1),
    CONSTRAINT PK_NAV_J PRIMARY KEY (N1)
   ) ;
'''
create_ATQ_J_query = '''
CREATE TABLE IF NOT EXISTS ATQ_J
   (
    N2 NUMBER(8) NOT NULL,
    N_J NUMBER(4)  NOT NULL,
    NOM VARCHAR2(10)  NULL,
    N_A NUMBER(4)  NOT NULL,
    A_X NUMBER(1),
    A_Y NUMBER(1),
    ETAT VARCHAR2(1),
    CONSTRAINT PK_ATQ_J PRIMARY KEY (N2)
   ) ;
'''
cursor.execute(create_M_query)
cursor.execute(create_NAV_J_query)
cursor.execute(create_ATQ_J_query)


position = []
niveau = None
pseudo = None
liste_bat_pos = []
compteur = 0
kivy.require('2.0.0')
alph = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
ALPH = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]


def rempli_M(N_M, VAINQUEUR, DUREE, NB_COUPS, NIVEAU, JOUEUR):
    insert_query = '''
        INSERT INTO M (N_M, VAINQUEUR, DUREE, NB_COUPS, NIVEAU, JOUEUR)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(insert_query, (N_M, VAINQUEUR, DUREE, NB_COUPS, NIVEAU, JOUEUR))

def rempli_NAV_J(N1, N_J, NOM, N_B, B_X, B_Y):
    insert_query = '''
        INSERT INTO NAV_J (N1, N_J, NOM, N_B, B_X, B_Y)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(insert_query, (N1, N_J, NOM, N_B, B_X, B_Y))

def rempli_ATQ_J(N2, N_J, NOM, N_A, A_X, A_Y, ETAT):
    insert_query = '''
        INSERT INTO ATQ_J (N2, N_J, NOM, N_A, A_X, A_Y, ETAT)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(insert_query, (N2, N_J, NOM, N_A, A_X, A_Y, ETAT))


class WindowManager(ScreenManager):
    pass

class MenuScreen(Screen):
    pass

class ChoixScreen(Screen):
    def __init__(self, **kwargs):
        super(ChoixScreen, self).__init__(**kwargs)
        self.diffic = None

    def on_enter(self):
        self.diffic = None

class NameRequest(Popup):
    def __init__(self, **kwargs):
        super(NameRequest, self).__init__(**kwargs)

    def set_pseudo(self):
        global pseudo
        pseudo = self.ids.txtinput.text

class Winending(Popup):
    def on_open(self):
        select_query = '''
            SELECT N_M, VAINQUEUR, DUREE, NB_COUPS, NIVEAU, JOUEUR FROM M
        '''

        cursor.execute(select_query)
        val = cursor.fetchall()[-1]

        temps_minutes = val[2] // 60
        reste_secondes = val[2] % 60

        # Générer le compte rendu
        compte_rendu = f"Vainqueur : {val[1]}\n"
        compte_rendu += f"Temps : {temps_minutes} min {reste_secondes} sec\n"
        compte_rendu += f"Nombre de coups : {val[3]}\n"
        compte_rendu += f"Difficulté : {val[4]}\n"
        compte_rendu += f"Joueur/joueuse : {val[5]}\n"

        # Nom du fichier
        Nom = f"CR de la partie {val[0]}"

        # Créer un fichier texte et écrire le compte rendu
        nom_fichier = f"{Nom}.txt"
        with open(nom_fichier, 'w') as fichier:
            fichier.write(compte_rendu)

        print("Le compte rendu a été enregistré dans le fichier :", nom_fichier)

        # Commit the changes and close the connection
        conn.commit()

class Loseending(Popup):
    def on_open(self):
        select_query = '''
            SELECT N_M, VAINQUEUR, DUREE, NB_COUPS, NIVEAU, JOUEUR FROM M
        '''

        cursor.execute(select_query)
        val = cursor.fetchall()[-1]

        temps_minutes = val[2] // 60
        reste_secondes = val[2] % 60

        # Générer le compte rendu
        compte_rendu = f"Vainqueur : {val[1]}\n"
        compte_rendu += f"Temps : {temps_minutes} min {reste_secondes} sec\n"
        compte_rendu += f"Nombre de coups : {val[3]}\n"
        compte_rendu += f"Difficulté : {val[4]}\n"
        compte_rendu += f"Joueur/joueuse : {val[5]}\n"

        # Nom du fichier
        Nom = f"CR de la partie {val[0]}"

        # Créer un fichier texte et écrire le compte rendu
        nom_fichier = f"{Nom}.txt"
        with open(nom_fichier, 'w') as fichier:
            fichier.write(compte_rendu)

        print("Le compte rendu a été enregistré dans le fichier :", nom_fichier)

        # Commit the changes and close the connection
        conn.commit()

class Abandon(Popup):
    pass

class Devmt(Popup):
    pass

class Rules(Popup):
    pass

class Credits(Popup):
    pass

class FacileScreen(Screen):
    def __init__(self, **kwargs):
        super(FacileScreen, self).__init__(**kwargs)
        self.bateau = [[1, 5, "porte-avions"], [2, 4, "croiseur"], [3, 3, "contre-torpilleur"], [4, 3, "contre-torpilleur"], [5, 2, "torpilleur"]]
        self.bateau_a_placer = [(5, 2), (4, 3), (3, 3), (2, 4), (1, 5)]
        self.bato = (5, 2)
        self.position_rec = []
        self.position = []  # [numero bateau, [(coordonees)]]
        self.placage = [[0 for i in range(10)] for i in range(10)]
        self.current = self.find_empty()
        self.dir = 'v'

    def create_grille_def(self):
        bat = self.bateau
        grille_og = [[0 for i in range(10)] for i in range(10)]  # grille vierge que l'on va remplir
        test = 5*[True]
        while True in test:
            b = test.index(True)  # on cherche un bateau qui n'est pas encore placé (True si non placé et False si déjà posé sur le plateau).
            i, j = rd.randrange(0, 10), rd.randrange(0, 10)  # coordonées du premier point du bateau
            orientation = rd.randrange(0, 4)  #0 si en haut, 1 si à droite, 2 si en bas, 3 si à gauche
            if orientation == 0:
                if -1 < i - bat[b][1] + 1 < 10:  # pour éviter de sortir du plateau
                    x = [grille_og[k][j] for k in range(i - bat[b][1] + 1, i+1)]
                    if x.count(0) == bat[b][1]:  # pour éviter le chevauchement
                        for l in range(bat[b][1]):
                            grille_og[i - l][j] = bat[b][0]
                        test[b] = False
            elif orientation == 2:
                if -1 < i + bat[b][1] - 1 < 10:
                    x = [grille_og[k][j] for k in range(i, i + bat[b][1])]
                    if x.count(0) == bat[b][1]:
                        for l in range(bat[b][1]):
                            grille_og[i + l][j] = bat[b][0]
                        test[b] = False
            elif orientation == 1:
                if -1 < j + bat[b][1] - 1 < 10:
                    x = [grille_og[i][k] for k in range(j, j + bat[b][1])]
                    if x.count(0) == bat[b][1]:
                        for l in range(bat[b][1]):
                            if grille_og[i][j + l] == 0:
                                grille_og[i][j + l] = bat[b][0]
                            else:
                                break
                        test[b] = False
            else:
                if -1 < j - bat[b][1] + 1 < 10:
                    x = [grille_og[i][k] for k in range(j - bat[b][1], j + 1)]
                    if x.count(0) == bat[b][1]:
                        for l in range(bat[b][1]):
                            if grille_og[i][j - l] == 0:
                                grille_og[i][j - l] = bat[b][0]
                            else:
                                break
                        test[b] = False
        return grille_og

    def placer_aleatoire(self):
        self.position = []
        self.position_rec = []
        g = self.create_grille_def()

        def verif_bonne_grille(grille):  # permet de vérifier que les bateaux sont tous présents
            count_bateau = [0, 0, 0, 0, 0]
            for i in range(10):
                for j in range(10):
                    x = grille[i][j]
                    if x > 0:
                        count_bateau[x-1] += 1
            return (count_bateau == [5, 4, 3, 3, 2])

        aux = verif_bonne_grille(g)
        while not aux:
            g = self.create_grille_def()
            aux = verif_bonne_grille(g)

        for a in range(10):
            for b in range(10):
                id_btn = alph[a] + str(b+1)
                if g[a][b] == 0:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))
                else:
                    ind = [0, 5, 4, 32, 31, 2][g[a][b]]
                    self.position += [(ind, [a, b])]
                    self.position_rec += [(ind, [a, b])]
                    if ind == 32:
                        ind = 3
                    elif ind == 31:
                        ind = 4
                    liste_bat_pos.append([[5, 4, 32, 31, 2][ind-1], a, b])
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
        global position
        position = self.position
        setattr(self.ids['etape_btn'], 'text', " Jouer ")

    def on_enter(self):
        self.bateau = [[1, 5, "porte-avions"], [2, 4, "croiseur"], [3, 3, "contre-torpilleur"], [4, 3, "contre-torpilleur"], [5, 2, "torpilleur"]]
        self.bateau_a_placer = [(5, 2), (4, 3), (3, 3), (2, 4), (1, 5)]
        self.bato = (5, 2)
        self.position = []  # [numero bateau, [(coordonees)]]
        self.position_rec = []
        self.placage = [[0 for i in range(10)] for i in range(10)]
        self.current = self.find_empty()
        self.dir = 'v'
        self.ids.haut.disabled = True
        self.ids.gauche.disabled = True
        self.ids.rota.disabled = True
        self.ids.droite.disabled = True
        self.ids.bas.disabled = True

        setattr(self.ids['etape_btn'], 'text', "Commencer")
        for i in range(10):
            for j in range(10):
                id_btn = alph[i] + str(j + 1)
                setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

    def find_empty(self):
        for i in range(10):
            for j in range(10):
                if self.placage[i][j] == 0:
                    return(i,j)

    def place(self, bat):
        og_x, og_y = self.current
        testos = False
        for x in range(bat[1]):
            id_btn = alph[og_x + x] + str(og_y + 1)
            if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                setattr(self.ids['etape_btn'], 'disabled', True)
                testos = True
            else:
                setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
        if not testos:
            setattr(self.ids['etape_btn'], 'disabled', False)

    def fleche_bas(self):
        old_x, old_y = self.current
        y = old_y
        testos = False
        if old_x < 10 - self.bato[1] and self.dir == 'v':
            x = old_x + 1
            self.current = x, y
            bat = self.bato
            for k in range(bat[1]):
                id_btn = alph[old_x + k] + str(old_y + 1)
                if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                else:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

            for k in range(bat[1]):
                id_btn = alph[x + k] + str(y + 1)
                if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                    setattr(self.ids['etape_btn'], 'disabled', True)
                    testos = True
                else:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

        elif old_x < 9 and self.dir == 'h':
            x = old_x + 1
            self.current = x, y
            bat = self.bato
            for k in range(bat[1]):
                id_btn = alph[old_x] + str(old_y + k + 1)
                if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                else:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

            for k in range(bat[1]):
                id_btn = alph[x] + str(y + k + 1)
                if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                    setattr(self.ids['etape_btn'], 'disabled', True)
                    testos = True
                else:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

        if not testos:
            setattr(self.ids['etape_btn'], 'disabled', False)

    def fleche_haut(self):
        old_x, old_y = self.current
        y = old_y
        testos = False
        if old_x > 0:
            x = old_x - 1
            self.current = x, y
            bat = self.bato
            if self.dir == "v":
                for k in range(bat[1]):
                    id_btn = alph[old_x + k] + str(old_y + 1)
                    if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                    else:
                        setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

                for k in range(bat[1]):
                    id_btn = alph[x + k] + str(y + 1)
                    if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                        setattr(self.ids['etape_btn'], 'disabled', True)
                        testos = True
                    else:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

            else:
                for k in range(bat[1]):
                    id_btn = alph[old_x] + str(old_y + k + 1)
                    if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                    else:
                        setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

                for k in range(bat[1]):
                    id_btn = alph[x] + str(y + k + 1)
                    if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                        setattr(self.ids['etape_btn'], 'disabled', True)
                        testos = True
                    else:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
        if not testos:
            setattr(self.ids['etape_btn'], 'disabled', False)

    def fleche_droite(self):
        old_x, old_y = self.current
        x = old_x
        testos = False
        if old_y < 9 and self.dir == 'v':
            y = old_y + 1
            self.current = x, y
            bat = self.bato
            for k in range(bat[1]):
                id_btn = alph[old_x + k] + str(old_y + 1)
                if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                else:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

            for k in range(bat[1]):
                id_btn = alph[x + k] + str(y + 1)
                if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                    setattr(self.ids['etape_btn'], 'disabled', True)
                    testos = True
                else:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

        elif old_y < 10 - self.bato[1] and self.dir == 'h':
            y = old_y + 1
            self.current = x, y
            bat = self.bato
            for k in range(bat[1]):
                id_btn = alph[old_x] + str(old_y + k + 1)
                if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                else:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

            for k in range(bat[1]):
                id_btn = alph[x] + str(y + k + 1)
                if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                    setattr(self.ids['etape_btn'], 'disabled', True)
                    testos = True
                else:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

        if not testos:
            setattr(self.ids['etape_btn'], 'disabled', False)

    def fleche_gauche(self):
        old_x, old_y = self.current
        x = old_x
        testos = False
        if old_y > 0:
            y = old_y - 1
            self.current = x, y
            bat = self.bato
            testos = False
            if self.dir == "v":
                for k in range(bat[1]):
                    id_btn = alph[old_x + k] + str(old_y + 1)
                    if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                    else:
                        setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

                for k in range(bat[1]):
                    id_btn = alph[x + k] + str(y + 1)
                    if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                        setattr(self.ids['etape_btn'], 'disabled', True)
                        testos = True
                    else:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

            else:
                for k in range(bat[1]):
                    id_btn = alph[old_x] + str(old_y + k + 1)
                    if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                    else:
                        setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

                for k in range(bat[1]):
                    id_btn = alph[x] + str(y + k + 1)
                    if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                        setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                        setattr(self.ids['etape_btn'], 'disabled', True)
                        testos = True
                    else:
                        setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

        if not testos:
            setattr(self.ids['etape_btn'], 'disabled', False)

    def fleche_rota(self):
        old_x, old_y = self.current
        n = self.bato[1]
        testos = False
        if self.dir == 'v' and old_y + n < 11:
            self.dir = "h"
            for k in range(1, n):
                id_btn = alph[old_x + k] + str(old_y + 1)
                if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                else:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

                id_btn = alph[old_x] + str(old_y + k + 1)
                if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                    setattr(self.ids['etape_btn'], 'disabled', True)
                    testos = True
                else:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

        elif self.dir == 'h' and old_x + n < 11:
            self.dir = 'v'
            for k in range(1, n):
                id_btn = alph[old_x] + str(old_y + k + 1)
                if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                else:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

                id_btn = alph[old_x + k] + str(old_y + 1)
                if self.ids[id_btn].background_color == [0.14, 0.82, 0.27, 1]:
                    setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
                    setattr(self.ids['etape_btn'], 'disabled', True)
                    testos = True
                else:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))

        if not testos:
            setattr(self.ids['etape_btn'], 'disabled', False)

    def next_bateau(self):
        if self.ids.etape_btn.text == "Commencer":
            self.ids.etape_btn.text = "Suivant"
            self.ids.haut.disabled = False
            self.ids.gauche.disabled = False
            self.ids.rota.disabled = False
            self.ids.droite.disabled = False
            self.ids.bas.disabled = False
        else:
            self.effet_valide()
        self.dir = "v"
        self.current = self.find_empty()
        if len(self.bateau_a_placer) > 1:
            self.bato = self.bateau_a_placer.pop()
            self.place(self.bato)
        elif len(self.bateau_a_placer) == 1:
            self.bato = self.bateau_a_placer.pop()
            self.place(self.bato)
            self.ids.etape_btn.text = "Jouer"
        else:
            self.manager.current = 'jeu'



    def effet_valide(self):
        x, y = self.current
        select_query1 = '''
            SELECT MAX(N_M) FROM M
        '''
        cursor.execute(select_query1)
        maxi = cursor.fetchall()[0][0]
        if maxi == None:
            maxi = 0
        select_query2 = '''
                        SELECT MAX(N1) FROM NAV_J
                    '''
        cursor.execute(select_query2)
        maxi2 = cursor.fetchall()[0][0]
        if maxi2 == None:
            maxi2 = 0
        for i in range(len(self.position_rec)):
            rempli_NAV_J(maxi2 + i + 1, maxi + 1, pseudo, self.position_rec[i][0], self.position_rec[i][1][0], self.position_rec[i][1][1])

        self.position_rec = []
        ind, n = self.bato
        nums = [2, 31, 32, 4, 5]
        if self.dir == "v":
            for k in range(n):
                self.position += [(ind, [x + k, y])]
                self.position_rec += [(ind, [x + k, y])]
                id_btn = alph[x + k] + str(y + 1)
                setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                liste_bat_pos.append([nums[ind-1], x + k, y])
        else:
            for k in range(n):
                self.position += [(ind, [x, y + k])]
                self.position_rec += [(ind, [x, y + k])]
                id_btn = alph[x] + str(y + k + 1)
                setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                liste_bat_pos.append([nums[ind-1], x, y + k])
        global position
        position = self.position

class Exo2Screen(Screen):
    def __init__(self, **kwargs):
        super(Exo2Screen, self).__init__(**kwargs)
        self.coo = 0, 0
        self.t0 = time.time()
        self.idbtn = None
        self.compteur = 0
        self.opposant = None
        self.dif = None
        self.ia = None
        self.cpt = 0
        self.liste_attaque = []
        self.grille_defe = self.update()
        self.grille_touche = [[0 for k in range(10)] for k in range(10)]

    def on_enter(self):
        self.coo = 0, 0
        self.t0 = time.time()
        self.idbtn = None
        self.compteur = 0
        self.cpt = 0
        self.dif = self.manager.get_screen('choix').diffic
        if self.dif == 'facile':
            self.opposant = gamecode.FACILE()
        elif self.dif == 'moyen':
            self.opposant = gamecode.MOYEN()
        elif self.dif == 'difficile':
            self.opposant = gamecode.DIFFICILE()
        elif self.dif == 'autodidacte':
            self.opposant = gamecode.AUTODIDACTE()
        self.ia = gamecode.JOUEUR()
        self.liste_attaque = []
        self.grille_defe = self.update()
        self.grille_touche = [[0 for k in range(10)] for k in range(10)]
        self.grille_defe = self.update()
        setattr(self.ids['valid'], 'disabled', True)
        self.ia.grille_def = self.grille_defe
        for i in range(10):
            for j in range(10):
                id_b = alph[i] + str(j + 1)
                setattr(self.ids[id_b], 'background_color', (0, 0, 0, .5))
                setattr(self.ids[id_b], 'disabled', False)
                id_btn = "z" + id_b
                if self.grille_defe[i][j] != 0:
                    setattr(self.ids[id_btn], 'background_color', (.14, .82, .27, 1))
                else:
                    setattr(self.ids[id_btn], 'background_color', (0, 0, 0, .5))

    def appui_bouton(self, btn):
        if btn.background_color == [0, 0, 0, 0.5]:
            setattr(self.ids['valid'], 'disabled', False)
            txt = btn.text
            ligne = ALPH.index(txt[0])
            if int(txt[-2:]) == 10:
                col = 9
            else:
                col = int(txt[-1]) - 1
            self.idbtn = btn
            self.coo = ligne, col
            setattr(btn, 'background_color', '#DAA0A0')
            for i in range(10):
                for j in range(10):
                    id_btn = alph[i] + str(j + 1)
                    setattr(self.ids[id_btn], 'disabled', True)
                    x = self.ids[id_btn].background_normal
                    setattr(self.ids[id_btn], 'background_disabled_normal', x)
            id_btn = alph[ligne] + str(col + 1)
            setattr(self.ids[id_btn], 'disabled', False)
        else:
            setattr(self.ids['valid'], 'disabled', True)
            self.enlever_lattaque()

    def update(self):
        liss = [[0 for k in range(10)] for k in range(10)]
        pos = [position[i][1] for i in range(len(position))]
        for coo in pos:
            liss[coo[0]][coo[1]] = 1
        return liss

    def faire_lattaque(self):
        x, y = self.coo
        id_btn = alph[x] + str(y + 1)
        setattr(self.ids[id_btn], 'disabled', True)
        setattr(self.ids['valid'], 'disabled', True)
        if self.opposant.grille_def[x][y] == 0:
            setattr(self.idbtn, 'background_color', '#7070FA')
            setattr(self.ids['lbl'], 'text', 'Loupé !')
            self.liste_attaque.append([x, y, 'L'])

            select_query1 = '''
                SELECT MAX(N_M) FROM M
            '''
            cursor.execute(select_query1)
            maxi = cursor.fetchall()[0][0]
            if maxi == None:
                maxi = 0
            select_query2 = '''
                            SELECT MAX(N2) FROM ATQ_J
                        '''
            cursor.execute(select_query2)
            maxi2 = cursor.fetchall()[0][0]
            if maxi2 == None:
                maxi2 = 0

            rempli_ATQ_J(maxi2+1, maxi+1, pseudo, self.cpt, self.coo[0], self.coo[1], 'P')

            # Confirmer les modifications
            conn.commit()

        else:   # touché
            setattr(self.idbtn, 'background_color', '#70FA70')
            setattr(self.ids['lbl'], 'text', 'Touché ! Bravo !!!')
            self.liste_attaque.append([x, y, 'T'])
            self.grille_touche[x][y] = 1
            select_query1 = '''
                SELECT MAX(N_M) FROM M
            '''
            cursor.execute(select_query1)
            maxi = cursor.fetchall()[0][0]
            if maxi == None:
                maxi = 0
            select_query2 = '''
                            SELECT MAX(N2) FROM ATQ_J
                        '''
            cursor.execute(select_query2)
            maxi2 = cursor.fetchall()[0][0]
            if maxi2 == None:
                maxi2 = 0
            rempli_ATQ_J(maxi2+1, maxi+1, pseudo, self.cpt, self.coo[0], self.coo[1], 'T')

            # Confirmer les modifications
            conn.commit()

        i, j = x, y
        ind = self.opposant.grille_def[i-1][j-1]
        if ind > 0:
            self.ia.grille_attaque[i-1][j-1] = ind
        else:
            self.ia.grille_attaque[i-1][j-1] = -1


        self.opposant.defend(self.ia, x, y)

        n = 0
        for k in range(10):
            for l in range(10):
                n += self.grille_touche[k][l]
        if n == 17:
            setattr(self.ids['lbl'], 'text', 'Vous avez gagné !!!!!')
            t_tot = time.time() - self.t0
            compteur = self.compteur

            select_query1 = '''
                SELECT MAX(N_M) FROM M
            '''
            cursor.execute(select_query1)
            maxi = cursor.fetchall()[0][0]
            if maxi == None:
                maxi = 0

            if self.dif == 'facile':
                rempli_M(maxi+1, pseudo, t_tot, self.cpt, 'Facile', pseudo)
            elif self.dif == 'moyen':
                rempli_M(maxi+1, pseudo, t_tot, self.cpt, 'Moyen', pseudo)
            elif self.dif == 'difficile':
                rempli_M(maxi+1, pseudo, t_tot, self.cpt, 'Difficile', pseudo)
            elif self.dif == 'autodidacte':
                rempli_M(maxi+1, pseudo, t_tot, self.cpt, 'Autodidacte', pseudo)


            # Confirmer les modifications
            conn.commit()

            Winending().open()


        i, j = self.opposant.attaque(self.ia)
        self.ia.defend(self.opposant, i, j)


        self.compteur += 1

        time.sleep(0.2)

        id_btn = "z" + alph[i] + str(j + 1)
        if self.grille_defe[i][j] != -9:
            setattr(self.ids[id_btn], 'background_color', (.76, .17, .13, 1))
        else:
            setattr(self.ids[id_btn], 'background_color', "#7070FA")

        n = 0
        for k in range(10):
            for l in range(10):
                n += self.grille_defe[k][l]
        if n == 0:
            compteur = self.compteur
        self.cpt += 1

        liste_aux = []
        for coo in self.liste_attaque:
            liste_aux.append([coo[0],coo[1]])
        for a in range(10):
            for b in range(10):
                if [a, b] not in liste_aux:
                    id_btn = alph[a] + str(b+1)
                    setattr(self.ids[id_btn], 'disabled', False)

        n = 0
        for a in range(10):
            for b in range(10):
                id_btn = "z" + alph[a] + str(b + 1)
                if self.ids[id_btn].background_color == [.76, .17, .13, 1]:
                    n += 1
        if n == 17:
            setattr(self.ids['lbl'], 'text', 'Vous avez perdu !!!')
            t_tot = time.time() - self.t0
            compteur = self.compteur

            select_query1 = '''
                SELECT MAX(N_M) FROM M
            '''
            cursor.execute(select_query1)
            maxi = cursor.fetchall()[0][0]
            if maxi == None:
                maxi = 0

            if self.dif == 'facile':
                rempli_M(maxi + 1, 'F', t_tot, self.cpt, 'Facile', pseudo)
            elif self.dif == 'moyen':
                rempli_M(maxi + 1, 'M', t_tot, self.cpt, 'Moyen', pseudo)
            elif self.dif == 'difficile':
                rempli_M(maxi + 1, 'D', t_tot, self.cpt, 'Difficile', pseudo)
            elif self.dif == 'autodidacte':
                rempli_M(maxi + 1, 'A', t_tot, self.cpt, 'Autodidacte', pseudo)

            # Confirmer les modifications
            conn.commit()

            Loseending().open()

    def enlever_lattaque(self):
        liste_aux = []
        for coo in self.liste_attaque:
            liste_aux.append([coo[0],coo[1]])
        for i in range(10):
            for j in range(10):
                if [i, j] not in liste_aux:
                    id_btn = alph[i] + str(j + 1)
                    setattr(self.ids[id_btn], 'disabled', False)
        setattr(self.idbtn, 'background_color', (0, 0, 0, .5))

class AlphApp(App):
    def build(self):
        return Builder.load_file('main.kv')



AlphApp().run()



# Fermer la connexion
conn.close()
