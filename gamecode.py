import random as rd
import numpy as np
import matplotlib.pyplot as plt
import time
import sqlite3

def intersection(l1, l2):
    for x in l1:
        if x in l2:
            return True
    return False

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('BDD_BatailleNavale.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

class IA():
    """
    Définit les méthodes de base qui seront utilisées par toutes les IA

    Auteur :
        Romain Jaugey
    """

    def __init__(self):
        self.grille_attaque = [[0 for i in range(10)] for i in range(10)]  # 0 si pas tiré sur la case, -1 si tiré dans le vide et 1, 2, 3, 4, 5 si un bateau est touché et 8 si coulé
        self.bateau = [[1, 5, "porte-avions"], [2, 4, "croiseur"], [3, 3, "contre-torpilleur"], [4, 3, "contre-torpilleur"], [5, 2, "torpilleur"]]
        self.grille_def = self.place_bateau(self.bateau)
        self.en_coulage = []
        self.liste_bateaux_en_jeu = [True, True, True, True, True]
        self.mem = []
        self.grille_probas = [[0 for i in range(10)] for j in range(10)]

    def place_bateau(self, bat):
        """
        Cette méthode sert uniquement à vérifier que la méthode create_grille_def
        a fonctionné correctement

        Inputs :
            bat : liste contenant les informations sur les bateaux à placer
        Outputs :
            g : grille contenant tous les bateaux bien placés sans chevauchement
            ni dépassement du plateau de jeu
        """
        g = self.create_grille_def(bat)

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
            g = self.create_grille_def(bat)
            aux = verif_bonne_grille(g)
        return g

    def create_grille_def(self, bat):
        """
        On place de manière aléatoire sur le plateau les bateaux contenus
        dans 'bat' sans chevauchement et sans dépassement du plateau.

        Inputs :
            bat : liste contenant les informations sur les bateaux à placer
        Outputs :
            grille_og : grille contenant tous les bateaux placés
        """

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

    def clean(self, ind):
        aux = []
        for l in self.mem:
            a, b = l[0], l[1]
            if self.grille_attaque[a][b] == ind:
                aux.append(l)
        self.mem = [item for item in self.mem if item not in aux]

    def verif_fini(self):
        return (True not in self.liste_bateaux_en_jeu)

    def defend(self, ennemi, i, j):  # -9 si l'adversaire a tiré dans le vide et -x si l'adversaire a touché un bateau numero x
        x = self.grille_def[i][j]
        if x == 0:
            self.grille_def[i][j] = -9
        else:
            self.grille_def[i][j] = -x
            c = 0
            for k in range(10):
                for l in range(10):
                    if x == self.grille_def[k][l]:
                        c += 1
                        break
            if c == 0:
                ennemi.liste_bateaux_en_jeu[x-1] = False

    def va_couler(self, ind):
        c = 0
        for i in range(10):
            for j in range(10):
                if ind == self.grille_def[i][j]:
                    c += 1
        return (c == 1)

    def est_mort(self, i, j, dir, ennemi):
        ind = self.grille_attaque[i][j]
        if dir == "v":
            ligne = [self.grille_attaque[k][j] for k in range(10)]
            coo = []
            for a in range(10):
                if ligne[a] == ind:
                    coo += [a]
            return ( ((min(coo) == 0) or ((min(coo) > 0) and (ligne[min(coo) - 1] not in [ind, 0]))) and ((max(coo) == 9) or ((max(coo) < 9) and (ligne[max(coo) + 1] not in [ind, 0]))) )

        elif dir == "h":
            col = [self.grille_attaque[i][k] for k in range(10)]
            coo = []
            for a in range(10):
                if col[a] == ind:
                    coo += [a]
            return ( ((min(coo) == 0) or ((min(coo) > 0) and (col[min(coo) - 1] not in [ind, 0]))) and ((max(coo) == 9) or ((max(coo) < 9) and (col[max(coo) + 1] not in [ind, 0]))) )

    def show_attaque(self):
        return np.matrix(self.grille_attaque)

    def show_def(self):
        return np.matrix(self.grille_def)

    def show_probas(self):
        return(np.matrix(self.grille_probas))


class TEMOIN(IA):
    """
    Définit une IA témoin = inactive qui permet de tester l'efficacité des autres IA

    Auteur :
        Arne Jacobs
    """

    def attaque(self, ennemi):
        i, j = 0, 0
        x = ennemi.grille_def[i][j]
        if x == 0:
            self.grille_attaque[i][j] = 0
        else:
            self.grille_attaque[i][j] = x
        return(i, j)


class FACILE(IA):
    """
    Définit une IA facile qui joue aléatoirement sur la grille (sans se répéter)

    Auteur :
        Arne Jacobs
    """


    def attaque(self, ennemi):
        """
        On attaque aaléatoirement dans une zone non déjà visée
        On modifie la grille_attaque selon le résultat et on retourne les coordonées de l'attaque.

        Inputs :
            ennemi : joueur ennemi (permet de savoir si l'on a touché ou non l'adversaire)
        Outputs :
            (i, j) : coordonées du point d'attaque
        """



        i, j = rd.randrange(0, 10), rd.randrange(0, 10)
        while self.grille_attaque[i][j] != 0:
            i, j = rd.randrange(0, 10), rd.randrange(0, 10)
        x = ennemi.grille_def[i][j]
        if x == 0:
            self.grille_attaque[i][j] = -1
        else:
            self.grille_attaque[i][j] = x
        return(i, j)


class MOYEN(IA):
    """
    Définit une IA de niveau moyen qui se rapproche du jeu d'un humain
    qui ne réfléchit pas trop.

    Auteur :
        Arne Jacobs
    """

    def __init__(self):
        super().__init__()
        self.touche = False
        self.coule = False
        self.direction = None
        self.bateau_en_cours = 0
        """
        L'attaque se décompose en 2 parties
        - On attaque aaléatoirement dans une zone non déjà visée jusqu'à toucher un bateau.
        - Une fois qu'un bateau est touché on se concentre dessus jusqu'à le couler.

        Inputs :
            ennemi : joueur ennemi (permet de savoir si l'on a touché ou non l'adversaire)
        Outputs :
            (i, j) : coordonées du point d'attaque
        """

    def attaque(self, ennemi):
        i, j = 0, 0
        if self.mem == []:  # on cherche à toucher un premier bateau
            self.direction = None
            i, j = rd.randrange(0, 10), rd.randrange(0, 10)

            def full_damier():
                n = 0
                for a in range(10):
                    for b in range(10):
                        if (a+b) % 2 == 0 and self.grille_attaque[a][b] == 0:
                            return False
                return True

            if full_damier():
                while self.grille_attaque[i][j] != 0:
                    i, j = rd.randrange(0, 10), rd.randrange(0, 10)
            else:
                while (i + j) % 2 != 0 or self.grille_attaque[i][j] != 0:
                    i, j = rd.randrange(0, 10), rd.randrange(0, 10)



            x = ennemi.grille_def[i][j]
            if x == 0:
                self.grille_attaque[i][j] = -1
                self.bateau_en_cours = 0
            elif x != 0:
                self.grille_attaque[i][j] = x
                self.touche = True
                self.coule = False
                self.en_coulage.append([i, j])
                self.mem.append([i, j])
                self.bateau_en_cours = x

        elif self.direction == None:  # si on a touché avec un random et qu'on n'a aucune info
            l_t = self.mem[0]
            x, y = l_t[0], l_t[1]
            self.direction = None
            # Define the list of possible directions to check
            directions = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            valid_directions = []

            for i, j in directions:
                if 0 <= i < 10 and 0 <= j < 10 and self.grille_attaque[i][j] == 0:
                    if ennemi.grille_def[i][j] > 0:
                        valid_directions.append((i, j))

            if valid_directions:
                i, j = rd.choice(valid_directions)  # Select a random valid direction
                self.direction = "v" if i != x else "h"
            else:
                i, j = rd.randrange(0, 10), rd.randrange(0, 10)
                while self.grille_attaque[i][j] != 0:
                    i, j = rd.randrange(0, 10), rd.randrange(0, 10)

            ind = ennemi.grille_def[i][j]
            if ind == 0:
                self.grille_attaque[i][j] = -1
                bo = self.est_mort(x, y, self.direction, ennemi)
                ind = abs(self.bateau_en_cours)
                if bo:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]
            elif ind != 0:
                self.grille_attaque[i][j] = ind
                bo = not self.est_mort(i, j, self.direction, ennemi)
                if bo:
                    self.touche = True
                    self.coule = False
                    self.mem.append([i, j])
                    if abs(ind) == abs(self.bateau_en_cours):
                        self.en_coulage.append([i, j])
                else:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]

        elif self.direction == "v":  # on vérifie les extremites verticales
            l_t = self.en_coulage[0]
            x, y = l_t[0], l_t[1]
            line = [self.grille_attaque[a][y] for a in range(10)]
            ind = line[x]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            if 0 <= x - 1 and line[x - 1] == 0:
                i, j = x - 1, y
            elif 10 > x + 1 and line[x + 1] == 0:
                i, j = x + 1, y
            elif 0 <= x - 2 and line[x - 2] == 0 and not intersection(range_list, line[x - 2:x + 1]):
                i, j = x - 2, y
            elif 10 > x + 2 and line[x + 2] == 0 and not intersection(range_list, line[x:x + 3]):
                i, j = x + 2, y
            elif 0 <= x - 3 and line[x - 3] == 0 and not intersection(range_list, line[x - 3:x + 1]):
                i, j = x - 3, y
            elif 10 > x + 3 and line[x + 3] == 0 and not intersection(range_list, line[x:x + 4]):
                i, j = x + 3, y
            elif 0 <= x - 4 and line[x - 4] == 0 and not intersection(range_list, line[x - 4:x + 1]):
                i, j = x - 4, y
            elif 10 > x + 4 and line[x + 4] == 0 and not intersection(range_list, line[x:x + 5]):
                i, j = x + 4, y
            elif 0 <= x - 5 and line[x - 5] == 0 and not intersection(range_list, line[x - 5:x + 1]):
                i, j = x - 5, y
            elif 10 > x + 5 and line[x + 5] == 0 and not intersection(range_list, line[x:x + 6]):
                i, j = x + 5, y
            elif 0 <= x - 6 and line[x - 6] == 0 and not intersection(range_list, line[x - 6:x + 1]):
                i, j = x - 6, y
            elif 10 > x + 6 and line[x + 6] == 0 and not intersection(range_list, line[x:x + 7]):
                i, j = x + 6, y
            elif 0 <= x - 7 and line[x - 7] == 0 and not intersection(range_list, line[x - 7:x + 1]):
                i, j = x - 7, y
            elif 10 > x + 7 and line[x + 7] == 0 and not intersection(range_list, line[x:x + 8]):
                i, j = x + 7, y
            elif 0 <= x - 8 and line[x - 8] == 0 and not intersection(range_list, line[x - 8:x + 1]):
                i, j = x - 8, y
            elif 10 > x + 8 and line[x + 8] == 0 and not intersection(range_list, line[x:x + 9]):
                i, j = x + 8, y
            elif 0 <= x - 9 and line[x - 9] == 0 and not intersection(range_list, line[x - 9:x + 1]):
                i, j = x - 9, y
            elif 10 > x + 9 and line[x + 9] == 0 and not intersection(range_list, line[x:x + 10]):
                i, j = x + 9, y
            else:

                # Define the list of possible directions to check
                directions = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
                valid_directions = []

                for i, j in directions:
                    if 0 <= i < 10 and 0 <= j < 10 and self.grille_attaque[i][j] == 0:
                        if ennemi.grille_def[i][j] > 0:
                            valid_directions.append((i, j))

                if valid_directions:
                    i, j = rd.choice(valid_directions)  # Select a random valid direction
                    if i != x:
                        self.direction = "v"
                    else:
                        self.direction = "h"
                else:
                    self.direction = None
                    i, j = rd.randrange(0, 10), rd.randrange(0, 10)
                    while self.grille_attaque[i][j] != 0:
                        i, j = rd.randrange(0, 10), rd.randrange(0, 10)


            ind = ennemi.grille_def[i][j]
            if ind == 0:
                self.grille_attaque[i][j] = -1
                bo = self.est_mort(x, y, self.direction, ennemi)
                ind = abs(self.bateau_en_cours)
                if bo:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]
            elif ind > 0:
                self.grille_attaque[i][j] = ind
                bo = not self.est_mort(i, j, self.direction, ennemi)
                if bo:
                    self.touche = True
                    self.coule = False
                    self.mem.append([i, j])
                    if abs(ind) == abs(self.bateau_en_cours):
                        self.en_coulage.append([i, j])
                else:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]

        else:  # on vérifie les extremites horizontales
            l_t = self.en_coulage[0]
            x, y = l_t[0], l_t[1]
            line = [self.grille_attaque[x][a] for a in range(10)]
            ind = line[y]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            if 0 <= y - 1 and line[y - 1] == 0:
                i, j = x, y - 1
            elif 10 > y + 1 and line[y + 1] == 0:
                i, j = x, y + 1
            elif 0 <= y - 2 and line[y - 2] == 0 and not intersection(range_list, line[y - 2:y + 1]):
                i, j = x, y - 2
            elif 10 > y + 2 and line[y + 2] == 0 and not intersection(range_list, line[y:y + 3]):
                i, j = x, y + 2
            elif 0 <= y - 3 and line[y - 3] == 0 and not intersection(range_list, line[y - 3:y + 1]):
                i, j = x, y - 3
            elif 10 > y + 3 and line[y + 3] == 0 and not intersection(range_list, line[y:y + 4]):
                i, j = x, y + 3
            elif 0 <= y - 4 and line[y - 4] == 0 and not intersection(range_list, line[y - 4:y + 1]):
                i, j = x, y - 4
            elif 10 > y + 4 and line[y + 4] == 0 and not intersection(range_list, line[y:y + 5]):
                i, j = x, y + 4
            elif 0 <= y - 5 and line[y - 5] == 0 and not intersection(range_list, line[y - 5:y + 1]):
                i, j = x, y - 5
            elif 10 > y + 5 and line[y + 5] == 0 and not intersection(range_list, line[y:y + 6]):
                i, j = x, y + 5
            elif 0 <= y - 6 and line[y - 6] == 0 and not intersection(range_list, line[y - 6:y + 1]):
                i, j = x, y - 6
            elif 10 > y + 6 and line[y + 6] == 0 and not intersection(range_list, line[y:y + 7]):
                i, j = x, y + 6
            elif 0 <= y - 7 and line[y - 7] == 0 and not intersection(range_list, line[y - 7:y + 1]):
                i, j = x, y - 7
            elif 10 > y + 7 and line[y + 7] == 0 and not intersection(range_list, line[y:y + 8]):
                i, j = x, y + 7
            elif 0 <= y - 8 and line[y - 8] == 0 and not intersection(range_list, line[y - 8:y + 1]):
                i, j = x, y - 8
            elif 10 > y + 8 and line[y + 8] == 0 and not intersection(range_list, line[y:y + 9]):
                i, j = x, y + 8
            elif 0 <= y - 9 and line[y - 9] == 0 and not intersection(range_list, line[y - 9:y + 1]):
                i, j = x, y - 9
            elif 10 > y + 9 and line[y + 9] == 0 and not intersection(range_list, line[y:y + 10]):
                i, j = x, y + 9
            else:
                l_t = self.mem[0]
                x, y = l_t[0], l_t[1]

                # Define the list of possible directions to check
                directions = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
                valid_directions = []

                for i, j in directions:
                    if 0 <= i < 10 and 0 <= j < 10 and self.grille_attaque[i][j] == 0:
                        if ennemi.grille_def[i][j] > 0:
                            valid_directions.append((i, j))

                if valid_directions:
                    i, j = rd.choice(valid_directions)  # Select a random valid direction
                    self.direction = "v" if i != x else "h"
                else:
                    self.direction = None
                    i, j = rd.randrange(0, 10), rd.randrange(0, 10)
                    while self.grille_attaque[i][j] != 0:
                        i, j = rd.randrange(0, 10), rd.randrange(0, 10)


            ind = ennemi.grille_def[i][j]
            if ind == 0:
                self.grille_attaque[i][j] = -1
                bo = self.est_mort(x, y, self.direction, ennemi)
                ind = abs(self.bateau_en_cours)
                if bo:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]
            elif ind > 0:
                self.grille_attaque[i][j] = ind
                bo = not self.est_mort(i, j, self.direction, ennemi)
                if bo:
                    self.touche = True
                    self.coule = False
                    self.mem.append([i, j])
                    if abs(ind) == abs(self.bateau_en_cours):
                        self.en_coulage.append([i, j])
                else:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]

        return(i, j)


class DIFFICILE(IA):
    """
    Définit une IA de niveau difficile qui se repose sur les probabilités
    et qui est équivalente, voire supérieure à un humain

    Auteur :
        Romain Jaugey
    """


    def __init__(self):
        super().__init__()
        self.touche = False
        self.coule = False
        self.side = ["haut", "droite", "bas", "gauche"]
        self.direction = None
        self.bateau_en_cours = 0

    def compte_possibilites_recherche(self, i, j):
        """
        Calcul des probabilités lors de la phase de recherche d'un bateau

        Inputs :
            i, j : coordonées du point où l'on veut calculer la probabilité
        Outputs :
            c : nombre de bateaux que l'on peut placer qui passent par cette case
        """

        c = 0
        for k in range(5):
            n = self.bateau[k][1]
            if self.liste_bateaux_en_jeu[k]:
                horiz = [self.grille_attaque[i][y] for y in range(10)]
                vert = [self.grille_attaque[x][j] for x in range(10)]
                for l in range(n):
                    if (0 <= i-l) and (i+n-l-1 < 10) and (vert[i-l:i+n-l].count(0) == n):
                        c += 1
                    if (0 <= j-l) and (j+n-l-1 < 10) and (horiz[j-l:j+n-l].count(0) == n):
                        c += 1
        return c

    def compte_possibilites_touche(self, i, j, direction, ennemi):
        """
        Calcul des probabilités lorsque l'on se concentre sur un bateau déjà touché (non coulé évidemment)

        Inputs :
            i, j : coordonées du point que l'on a touché précédemment
            direction : direction du bateau en cours de coulage "v" si vertical, "h" si horizontal et None si on ne sait pas encore
            ennemi : joueur ennemi (permet de savoir si l'on a touché ou non l'adversaire)
        Outputs :
            x, y : coordonées du point d'attaque
        """



        c_list = [0, 0, 0, 0]  #h, g, b, d
        c_ind = [[i-1, j], [i, j-1], [i+1, j], [i, j+1]]
        ind = self.grille_attaque[i][j]
        if direction == None:  # si l'on a déjà touché 2 fois un autre bateau que celui que l'on doit couler alors on peut déjà avoir sa direction
            if 0 <= i-1 and self.grille_attaque[i-1][j] == ind:
                self.direction = "v"
            elif i+1 < 10 and self.grille_attaque[i+1][j] == ind:
                self.direction = "v"
            elif 0 <= j-1 and self.grille_attaque[i][j-1] == ind:
                self.direction = "h"
            elif j+1 < 10 and self.grille_attaque[i][j+1] == ind:
                self.direction = "h"

        if direction == None:  # = si l'on a touché précedemment et que l'on n'a pas plus d'informations
            horiz = [self.grille_attaque[i][y] for y in range(10)]
            vert = [self.grille_attaque[x][j] for x in range(10)]
            for k in range(5):
                if self.liste_bateaux_en_jeu[k]:
                    n = self.bateau[k][1]
                    if 0 <= i - n + 1 and vert[i - n + 1:i + 1].count(0) == n-1:
                        c_list[0] += 1
                    if i + n - 1 < 10 and vert[i:i + n].count(0) == n-1:
                        c_list[2] += 1
                    for a in range(1, n-1):
                        if 0 <= i + a - n + 1 and i + a < 10 and vert[i + a - n + 1:i + a + 1].count(0) == n-1:
                            c_list[0] += 1
                            c_list[2] += 1
                    if 0 <= j - n + 1 and horiz[j - n + 1:j + 1].count(0) == n-1:
                        c_list[1] += 1
                    if j + n - 1 < 10 and horiz[j:j + n].count(0) == n-1:
                        c_list[3] += 1
                    for a in range(1, n-1):
                        if 0 <= j + a - n + 1 and j + a < 10 and horiz[j + a - n + 1:j + a + 1].count(0) == n-1:
                            c_list[1] += 1
                            c_list[3] += 1
            x, y = 0, 0
            maxi = 0
            for a in range(4):
                c = c_list[a]
                if c > maxi:
                    maxi = c
                    x, y = c_ind[a]
                    if ennemi.grille_def[x][y] == ind:
                        if a % 2 == 0:
                            self.direction = "v"
                        else:
                            self.direction = "h"
                    else:
                        self.direction = None

        elif direction == "v":  # si le bateau que l'on doit couler est à la verticale sur le plateau
            l_t = self.en_coulage[0]
            u, v = l_t[0], l_t[1]
            line = [self.grille_attaque[a][v] for a in range(10)]
            ind = line[u]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            if 0 <= u - 1 and line[u - 1] == 0:
                x, y = u - 1, v
            elif 10 > u + 1 and line[u + 1] == 0:
                x, y = u + 1, v
            elif 0 <= u - 2 and line[u - 2] == 0 and not intersection(range_list, line[u - 2:u + 1]):
                x, y = u - 2, v
            elif 10 > u + 2 and line[u + 2] == 0 and not intersection(range_list, line[u:u + 3]):
                x, y = u + 2, v
            elif 0 <= u - 3 and line[u - 3] == 0 and not intersection(range_list, line[u - 3:u + 1]):
                x, y = u - 3, v
            elif 10 > u + 3 and line[u + 3] == 0 and not intersection(range_list, line[u:u + 4]):
                x, y = u + 3, v
            elif 0 <= u - 4 and line[u - 4] == 0 and not intersection(range_list, line[u - 4:u + 1]):
                x, y = u - 4, v
            elif 10 > u + 4 and line[u + 4] == 0 and not intersection(range_list, line[u:u + 5]):
                x, y = u + 4, v

        else:  # si le bateau que l'on doit couler est à l'horizontale sur le plateau
            l_t = self.en_coulage[0]
            u, v = l_t[0], l_t[1]
            line = [self.grille_attaque[u][a] for a in range(10)]
            ind = line[v]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            if 0 <= v - 1 and line[v - 1] == 0:
                x, y = u, v - 1
            elif 10 > v + 1 and line[v + 1] == 0:
                x, y = u, v + 1
            elif 0 <= v - 2 and line[v - 2] == 0 and not intersection(range_list, line[v - 2:v + 1]):
                x, y = u, v - 2
            elif 10 > v + 2 and line[v + 2] == 0 and not intersection(range_list, line[v:v + 3]):
                x, y = u, v + 2
            elif 0 <= v - 3 and line[v - 3] == 0 and not intersection(range_list, line[v - 3:v + 1]):
                x, y = u, v - 3
            elif 10 > v + 3 and line[v + 3] == 0 and not intersection(range_list, line[v:v + 4]):
                x, y = u, v + 3
            elif 0 <= v - 4 and line[v - 4] == 0 and not intersection(range_list, line[v - 4:v + 1]):
                x, y = u, v - 4
            elif 10 > v + 4 and line[v + 4] == 0 and not intersection(range_list, line[v:v + 5]):
                x, y = u, v + 4

        return(x, y)

    def attaque(self, ennemi):
        """
        Définit en 2 étapes :
        - On recherche à l'aide des probabilités quelle case est la plus susceptible
        d'être occupée par un bateau adverse
        - On se concentre sur le bateau déjà touché et on calcule les probabilités que ce
        bateau puisse être positionné dans chaque direction pour déterminer la plus probable

        Inputs :
            ennemi : joueur ennemi (permet de savoir si l'on a touché ou non l'adversaire)
        Outputs :
            (i, j) : coordonées du point d'attaque
        """

        i, j = 0, 0
        if self.mem == []:  # on cherche a toucher une premiere fois un bateau
            maxi = 0
            for k in range(10):
                for l in range(10):
                    x = self.compte_possibilites_recherche(k, l)
                    self.grille_probas[k][l] = x
                    if x > maxi:
                        i, j = k, l
                        maxi = x

            x = ennemi.grille_def[i][j]
            if x == 0:
                self.grille_attaque[i][j] = -1
                self.bateau_en_cours = 0
            elif x > 0:
                # print("TOUCHE")
                self.grille_attaque[i][j] = x
                if not ennemi.va_couler(x):
                    self.touche = True
                    self.coule = False
                    self.en_coulage.append([i, j])
                    self.mem.append([i, j])
                    self.bateau_en_cours = x
                else:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(x)
                    self.bateau_en_cours = 0
                    self.en_coulage = self.mem

        else:  # dans le cas où l'on a déjà touché un bateau et que l'on cherche maintenant à le couler
            h, g = self.en_coulage[0]
            self.bateau_en_cours = self.grille_attaque[h][g]
            i, j = self.compte_possibilites_touche(h, g, self.direction, ennemi)

            ind = ennemi.grille_def[i][j]
            if ind == 0:
                self.grille_attaque[i][j] = -1
                bo = self.est_mort(h, g, self.direction, ennemi)
                ind = abs(self.bateau_en_cours)
                if bo:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]
            elif ind != 0:
                self.grille_attaque[i][j] = ind
                bo = not self.est_mort(i, j, self.direction, ennemi)
                if bo:
                    self.touche = True
                    self.coule = False
                    self.mem.append([i, j])
                    if abs(ind) == abs(self.bateau_en_cours):
                        self.en_coulage.append([i, j])
                else:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]

        return(i, j)














class AUTODIDACTE(IA):
    """
    Définit une IA de niveau difficile qui se repose sur les probabilités
    et qui s'adapte au fil des parties aux coups joués : nombre * 1.05 si joué précédemment

    Auteur :
        Romain Jaugey
    """

    def __init__(self):
        super().__init__()
        self.touche = False
        self.coule = False
        self.side = ["haut", "droite", "bas", "gauche"]
        self.direction = None
        self.bateau_en_cours = 0

    def compte_possibilites_recherche(self, i, j):
        """
        Calcul des probabilités lors de la phase de recherche d'un bateau

        Inputs :
            i, j : coordonées du point où l'on veut calculer la probabilité
        Outputs :
            c : nombre de bateaux que l'on peut placer qui passent par cette case
        """

        c = 0
        for k in range(5):
            n = self.bateau[k][1]
            if self.liste_bateaux_en_jeu[k]:
                horiz = [self.grille_attaque[i][y] for y in range(10)]
                vert = [self.grille_attaque[x][j] for x in range(10)]
                for l in range(n):
                    if (0 <= i-l) and (i+n-l-1 < 10) and (vert[i-l:i+n-l].count(0) == n):
                        c += 1
                    if (0 <= j-l) and (j+n-l-1 < 10) and (horiz[j-l:j+n-l].count(0) == n):
                        c += 1
        return c

    def compte_possibilites_touche(self, i, j, direction, ennemi):
        """
        Calcul des probabilités lorsque l'on se concentre sur un bateau déjà touché (non coulé évidemment)

        Inputs :
            i, j : coordonées du point que l'on a touché précédemment
            direction : direction du bateau en cours de coulage "v" si vertical, "h" si horizontal et None si on ne sait pas encore
            ennemi : joueur ennemi (permet de savoir si l'on a touché ou non l'adversaire)
        Outputs :
            x, y : coordonées du point d'attaque
        """



        c_list = [0, 0, 0, 0]  #h, g, b, d
        c_ind = [[i-1, j], [i, j-1], [i+1, j], [i, j+1]]
        ind = self.grille_attaque[i][j]
        if direction == None:  # si l'on a déjà touché 2 fois un autre bateau que celui que l'on doit couler alors on peut déjà avoir sa direction
            if 0 <= i-1 and self.grille_attaque[i-1][j] == ind:
                self.direction = "v"
            elif i+1 < 10 and self.grille_attaque[i+1][j] == ind:
                self.direction = "v"
            elif 0 <= j-1 and self.grille_attaque[i][j-1] == ind:
                self.direction = "h"
            elif j+1 < 10 and self.grille_attaque[i][j+1] == ind:
                self.direction = "h"

        if direction == None:  # = si l'on a touché précedemment et que l'on n'a pas plus d'informations
            horiz = [self.grille_attaque[i][y] for y in range(10)]
            vert = [self.grille_attaque[x][j] for x in range(10)]
            for k in range(5):
                if self.liste_bateaux_en_jeu[k]:
                    n = self.bateau[k][1]
                    if 0 <= i - n + 1 and vert[i - n + 1:i + 1].count(0) == n-1:
                        c_list[0] += 1
                    if i + n - 1 < 10 and vert[i:i + n].count(0) == n-1:
                        c_list[2] += 1
                    for a in range(1, n-1):
                        if 0 <= i + a - n + 1 and i + a < 10 and vert[i + a - n + 1:i + a + 1].count(0) == n-1:
                            c_list[0] += 1
                            c_list[2] += 1
                    if 0 <= j - n + 1 and horiz[j - n + 1:j + 1].count(0) == n-1:
                        c_list[1] += 1
                    if j + n - 1 < 10 and horiz[j:j + n].count(0) == n-1:
                        c_list[3] += 1
                    for a in range(1, n-1):
                        if 0 <= j + a - n + 1 and j + a < 10 and horiz[j + a - n + 1:j + a + 1].count(0) == n-1:
                            c_list[1] += 1
                            c_list[3] += 1
            x, y = 0, 0
            maxi = 0
            for a in range(4):
                c = c_list[a]
                if c > maxi:
                    maxi = c
                    x, y = c_ind[a]
                    if ennemi.grille_def[x][y] == ind:
                        if a % 2 == 0:
                            self.direction = "v"
                        else:
                            self.direction = "h"
                    else:
                        self.direction = None

        elif direction == "v":  # si le bateau que l'on doit couler est à la verticale sur le plateau
            l_t = self.en_coulage[0]
            u, v = l_t[0], l_t[1]
            line = [self.grille_attaque[a][v] for a in range(10)]
            ind = line[u]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            if 0 <= u - 1 and line[u - 1] == 0:
                x, y = u - 1, v
            elif 10 > u + 1 and line[u + 1] == 0:
                x, y = u + 1, v
            elif 0 <= u - 2 and line[u - 2] == 0 and not intersection(range_list, line[u - 2:u + 1]):
                x, y = u - 2, v
            elif 10 > u + 2 and line[u + 2] == 0 and not intersection(range_list, line[u:u + 3]):
                x, y = u + 2, v
            elif 0 <= u - 3 and line[u - 3] == 0 and not intersection(range_list, line[u - 3:u + 1]):
                x, y = u - 3, v
            elif 10 > u + 3 and line[u + 3] == 0 and not intersection(range_list, line[u:u + 4]):
                x, y = u + 3, v
            elif 0 <= u - 4 and line[u - 4] == 0 and not intersection(range_list, line[u - 4:u + 1]):
                x, y = u - 4, v
            elif 10 > u + 4 and line[u + 4] == 0 and not intersection(range_list, line[u:u + 5]):
                x, y = u + 4, v

        else:  # si le bateau que l'on doit couler est à l'horizontale sur le plateau
            l_t = self.en_coulage[0]
            u, v = l_t[0], l_t[1]
            line = [self.grille_attaque[u][a] for a in range(10)]
            ind = line[v]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            if 0 <= v - 1 and line[v - 1] == 0:
                x, y = u, v - 1
            elif 10 > v + 1 and line[v + 1] == 0:
                x, y = u, v + 1
            elif 0 <= v - 2 and line[v - 2] == 0 and not intersection(range_list, line[v - 2:v + 1]):
                x, y = u, v - 2
            elif 10 > v + 2 and line[v + 2] == 0 and not intersection(range_list, line[v:v + 3]):
                x, y = u, v + 2
            elif 0 <= v - 3 and line[v - 3] == 0 and not intersection(range_list, line[v - 3:v + 1]):
                x, y = u, v - 3
            elif 10 > v + 3 and line[v + 3] == 0 and not intersection(range_list, line[v:v + 4]):
                x, y = u, v + 3
            elif 0 <= v - 4 and line[v - 4] == 0 and not intersection(range_list, line[v - 4:v + 1]):
                x, y = u, v - 4
            elif 10 > v + 4 and line[v + 4] == 0 and not intersection(range_list, line[v:v + 5]):
                x, y = u, v + 4

        return(x, y)

    def attaque(self, ennemi):
        """
        Définit en 2 étapes :
        - On recherche à l'aide des probabilités quelle case est la plus susceptible
        d'être occupée par un bateau adverse
        - On se concentre sur le bateau déjà touché et on calcule les probabilités que ce
        bateau puisse être positionné dans chaque direction pour déterminer la plus probable

        Inputs :
            ennemi : joueur ennemi (permet de savoir si l'on a touché ou non l'adversaire)
        Outputs :
            (i, j) : coordonées du point d'attaque
        """

        i, j = 0, 0
        if self.mem == []:  # on cherche a toucher une premiere fois un bateau

            select_query = '''
                SELECT B_X, B_Y FROM NAV_J
            '''

            cursor.execute(select_query)

            rows = cursor.fetchall()
            Pos_Bat = []

            for row in rows:
                Pos_Bat.append(row)

            PB = np.zeros((10, 10))
            for i in range(10):
                for j in range(10):
                    PB[i][j] = Pos_Bat.count((i, j))

            i, j = 0, 0
            maxi = 0
            for k in range(10):
                for l in range(10):
                    if PB[k][l] > maxi:
                        maxi = PB[k][l]
                        i, j = k, l

            x = ennemi.grille_def[i][j]
            if x == 0:
                self.grille_attaque[i][j] = -1
                self.bateau_en_cours = 0
            elif x > 0:
                # print("TOUCHE")
                self.grille_attaque[i][j] = x
                if not ennemi.va_couler(x):
                    self.touche = True
                    self.coule = False
                    self.en_coulage.append([i, j])
                    self.mem.append([i, j])
                    self.bateau_en_cours = x
                else:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(x)
                    self.bateau_en_cours = 0
                    self.en_coulage = self.mem

        else:  # dans le cas où l'on a déjà touché un bateau et que l'on cherche maintenant à le couler
            h, g = self.en_coulage[0]
            self.bateau_en_cours = self.grille_attaque[h][g]
            i, j = self.compte_possibilites_touche(h, g, self.direction, ennemi)

            ind = ennemi.grille_def[i][j]
            if ind == 0:
                self.grille_attaque[i][j] = -1
                bo = self.est_mort(h, g, self.direction, ennemi)
                ind = abs(self.bateau_en_cours)
                if bo:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]
            elif ind != 0:
                self.grille_attaque[i][j] = ind
                bo = not self.est_mort(i, j, self.direction, ennemi)
                if bo:
                    self.touche = True
                    self.coule = False
                    self.mem.append([i, j])
                    if abs(ind) == abs(self.bateau_en_cours):
                        self.en_coulage.append([i, j])
                else:
                    self.touche = False
                    self.coule = True
                    self.direction = None
                    self.clean(ind)
                    self.en_coulage = self.mem
                    self.bateau_en_cours = 0
                    if self.mem != []:
                        e, f = self.mem[0][0], self.mem[0][1]
                        self.bateau_en_cours = -ennemi.grille_def[e][f]

        return(i, j)



class JOUEUR(IA):
    """
    Définit une première ébauche d'interface homme machine qui permet simplement d'acquérir et d'utiliser
    les valeurs données par le joueur

    Auteur :
        Arne Jacobs
    """

    def __init__(self):
        super().__init__()
        self.grille_apparence = [['_' for i in range(10)] for i in range(10)]
        self.grille_def = None

    # def placer(self):
    #     """
    #     On propose le choix de placer aléatoirement les bateaux ou de les placer
    #     un à un grâce à la méthode place_def.
    #
    #     Outputs :
    #         grille_def : grille contenant tous les bateaux placés correctement
    #     """
    #
    #
    #     print("")
    #     print("Voulez vous placer les bateaux aléatoirement ? y/n")
    #     test = input()
    #     while test not in ["y", "n"]:
    #         print("Répondez par y (Yes) ou n (No)")
    #         test = input()
    #     if test == "n":
    #         self.grille_def = self.place_def()
    #     else:
    #         self.grille_def = self.place_bateau(self.bateau)
    #         print("")
    #         print("Voici comment sont positionnés vos bateaux :")
    #         print(self.show_def())
    #     return(self.grille_def)

    # def place_def(self):
    #     """
    #     On place un à un les différents bateaux à l'aide des informations données par le joueur
    #
    #     Outputs :
    #         grille_def : grille contenant tous les bateaux placés correctement
    #     """
    #
    #
    #     self.grille_def = [[0 for i in range(10)] for j in range(10)]
    #     for a in range(5):
    #         print(self.show_def())
    #         n = self.bateau[a][1]
    #         print("plaçons le " + self.bateau[a][2] + " de longueur " + str(n))
    #         print("Veuillez saisir la ligne")
    #         i = int(input())
    #         while i not in range(1, 11):
    #             print("veuillez saisir un chiffre entre 1 et 10")
    #             i = int(input())
    #         print("Veuillez saisir la colonne")
    #         j = int(input())
    #         while j not in range(1, 11):
    #             print("veuillez saisir un chiffre entre 1 et 10")
    #             j = int(input())
    #         print("Saisissez le direction du bateau : v pour aller vers la bas, h pour aller vers la droite, n pour replacer le bateau")
    #         direction = input()
    #
    #         if direction == "n":
    #             print("plaçons le " + self.bateau[a][2] + " de longueur " + str(self.bateau[a][1]))
    #             print("Veuillez saisir la ligne")
    #             i = int(input())
    #             while i not in range(1, 11):
    #                 print("veuillez saisir un chiffre entre 1 et 10")
    #                 i = int(input())
    #             print("Veuillez saisir la colonne")
    #             j = int(input())
    #             while j not in range(1, 11):
    #                 print("veuillez saisir un chiffre entre 1 et 10")
    #                 j = int(input())
    #
    #         horiz = [self.grille_def[i-1][l] for l in range(10)]
    #         vert = [self.grille_def[l][j-1] for l in range(10)]
    #
    #         while direction not in ["n", "v", "h"] or (direction == "v" and i-1+n > 9) or (direction == "h" and j-1+n > 9) or (direction == "h" and horiz[j-1:j-1+n].count(0) != n) or (direction == "v" and vert[i-1:i-1+n].count(0) != n):
    #             print("veuillez saisir une direction valable")
    #             direction = input()
    #
    #         if direction == "h":
    #             ind = self.bateau[a][0]
    #             for l in range(n):
    #                 self.grille_def[i-1][j-1+l] = ind
    #         else:
    #             ind = self.bateau[a][0]
    #             for l in range(n):
    #                 self.grille_def[i-1+l][j-1] = ind
    #
    #
    #     return(self.grille_def)

    def show_apparence(self):  # question d'ésthetique
        return(np.matrix(self.grille_apparence))

    def attaque(self, ennemi):
        """
        On attaque en fonction des coordonées que nous donne le joueur
        On code tout de même une vérification de ces coordonées pour ne pas provoquer d'erreurs dans le programme.

        Inputs :
            ennemi : joueur ennemi (permet de savoir si l'on a touché ou non l'adversaire)
        Outputs :
            (i, j) : coordonées du point d'attaque
        """


        print(self.show_apparence())
        print('Veuillez entrer la ligne pour attaquer (entre 1 et 10) : ')
        i = int(input())
        while i not in range(1,11):
            print("veuillez saisir un chiffre entre 1 et 10")
            i = int(input())
        print('Veuillez entrer la colonne pour attaquer (entre 1 et 10) : ')
        j = int(input())
        while j not in range(1,11):
            print("veuillez saisir un chiffre entre 1 et 10")
            j = int(input())
        ind = ennemi.grille_def[i-1][j-1]
        if ind > 0:
            self.grille_attaque[i-1][j-1] = ind
            self.grille_apparence[i-1][j-1] = "X"
            print("Touché")
        else:
            self.grille_attaque[i-1][j-1] = -1
            self.grille_apparence[i-1][j-1] = "O"
            print("Loupé")
        return i-1, j-1


class DUELTEST():
    """
    Permet d'effectuer des duels tests entre une IA témoin et une IA que l'on veut évaluer

    Auteur :
        Romain Jaugey
    """

    def __init__(self):
        self.compteur = 0

    def combat(self, ia):
        """
        Permet de lancer et de stopper le duel lorsque l'un des participants a gagné

        Inputs :
            ia : IA que l'on veut évaluer
        Outputs :
            self.compteur : nombre de coups nécessaires pour finir la partie
        """


        j1 = TEMOIN()
        j2 = ia
        while not j2.verif_fini() and self.compteur < 100:

            self.etape_2_sur_1(j1, j2)

            self.compteur += 1
        return(self.compteur)

    def etape_1_sur_2(self, j1, j2):  # permet l'attaque de j1 sur j2
        x, y = j1.attaque(j2)
        j2.defend(j1, x, y)

    def etape_2_sur_1(self, j1, j2):  # permet l'attaque de j2 sur j1
        x, y = j2.attaque(j1)
        j1.defend(j2, x, y)


class DUELREEL():
    """
    Permet d'effectuer un duel entre un joueur et un adversaire (IA ou deuxième joueur)

    Auteur :
        Romain Jaugey
    """


    def __init__(self):
        self.compteur1 = 0
        self.compteur2 = 0

    def combat(self, ia):
        j1 = JOUEUR()
        j2 = ia
        while not j2.verif_fini() and not j1.verif_fini() and self.compteur1+self.compteur2 < 200:
            print("")
            print("")
            print("A votre de tour de jouer")
            print("")
            self.etape_1_sur_2(j1, j2)
            self.compteur1 += 1
            if j1.verif_fini():
                print("j1 à gagné en "+str(self.compteur1)+" coups")

            print("")
            print("")
            print("Au tour de l'adversaire de jouer")
            print("")

            self.etape_2_sur_1(j1, j2)
            time.sleep(1)
            self.compteur2 += 1
            if j2.verif_fini():
                print("l'adversaire a gagné en "+str(self.compteur1)+" coups")

        return(self.compteur1)

    def etape_1_sur_2(self, j1, j2):

        x, y = j1.attaque(j2)
        j2.defend(j1, x, y)

    def etape_2_sur_1(self, j1, j2):
        x, y = j2.attaque(j1)
        print(j2.show_attaque())
        j1.defend(j2, x, y)


def moyenne_coups_facile(n):    #  moyenne de 95.37 sur 100 000 parties
    c = 0
    liste_coups = np.array([0 for i in range(101)])
    for i in range(n):
        if i % 1000 == 0:
            print(i)
        j = FACILE()
        comb = DUELTEST()
        x = comb.combat(j)
        liste_coups[x] += 1
        c += x
    liste_coups = liste_coups
    plt.plot([i for i in range(101)], liste_coups, label="IA facile : "+str(round(c/n, 2)))
    plt.grid()
    plt.xlabel("nombre de coups")
    plt.ylabel("nombre de parties")
    plt.legend()
    plt.show()
    return(round(c/n, 2))

def moyenne_coups_moyen(n):    #  moyenne de 50.9 sur 1 000 000 parties
    t0 = time.time()
    c = 0
    liste_coups = np.array([0 for i in range(101)])
    for i in range(n):
        if i % 1000 == 0:
            print(i)
        j = MOYEN()
        comb = DUELTEST()
        x = comb.combat(j)
        liste_coups[x] += 1
        c += x
    liste_coups = liste_coups
    plt.plot([i for i in range(101)], liste_coups, label="IA moyenne : "+str(round(c/n, 2)))
    plt.grid()
    plt.xlabel("nombre de coups")
    plt.ylabel("nombre de parties")
    plt.title("IA moyenne")
    plt.show()
    return(round(c/n, 2))

def moyenne_coups_difficile(n):    #  moyenne de xxx sur xxx xxx parties
    c = 0
    liste_coups = np.array([0 for i in range(101)])
    for i in range(n):
        if i % 100 == 0:
            print(i)
        j = DIFFICILE()
        comb = DUELTEST()
        x = comb.combat(j)
        liste_coups[x] += 1
        c += x
    liste_coups = liste_coups
    plt.plot([i for i in range(101)], liste_coups)
    plt.grid()
    plt.xlabel("nombre de coups")
    plt.ylabel("nombre de parties")
    plt.title("IA moyenne : " + str(round(c/n, 2)) + " coups en moyenne")
    plt.show()
    return(round(c/n, 2))

def comparaison(n):
    c = 0
    liste_coups = np.array([0 for i in range(101)])
    for i in range(n):
        if i % 1000 == 0:
            print(1, i)
        j = FACILE()
        comb = DUELTEST()
        x = comb.combat(j)
        liste_coups[x] += 1
        c += x
    liste_coups = liste_coups
    plt.plot([i for i in range(101)], liste_coups, label="IA facile : "+str(round(c/n, 2)))

    c = 0
    liste_coups = np.array([0 for i in range(101)])
    for i in range(n):
        if i % 1000 == 0:
            print(2, i)
        j = MOYEN()
        comb = DUELTEST()
        x = comb.combat(j)
        liste_coups[x] += 1
        c += x
    liste_coups = liste_coups
    plt.plot([i for i in range(101)], liste_coups, label="IA moyenne : "+str(round(c/n, 2)))

    c = 0
    liste_coups = np.array([0 for i in range(101)])
    for i in range(n):
        if i % 100 == 0:
            print(3, i)
        j = DIFFICILE()
        comb = DUELTEST()
        x = comb.combat(j)
        liste_coups[x] += 1
        c += x
    liste_coups = liste_coups
    plt.plot([i for i in range(101)], liste_coups, label="IA difficile : "+str(round(c/n, 2)))

    plt.grid()
    plt.xlabel("nombre de coups")
    plt.ylabel("nombre de parties")
    plt.legend()
    plt.title("Comparaison des coups nécessaires pour gagner")
    plt.show()

def lancer_combat():
    comb = DUELREEL()
    print("Veuillez choisir votre adversaire")
    print("1 si IA FACILE")
    print("2 si IA MOYEN")
    print("3 si IA DIFFICILE")
    print("4 si JOUEUR ADVERSE")
    n = int(input())
    while n not in range(1, 5):
        print("Veuillez saisir un chiffre entre 1 et 4")
        n = int(input())
    if n == 1:
        j = FACILE()
    elif n == 2:
        j = MOYEN()
    elif n == 3:
        j = DIFFICILE()
    else:
        j = JOUEUR()

    print(comb.combat(j))


#print(lancer_combat())

# j = DIFFICILE()
# comb = DUELTEST()
# print(comb.combat(j))
