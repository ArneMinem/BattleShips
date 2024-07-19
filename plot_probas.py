import random as rd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
from matplotlib.ticker import MultipleLocator


"""
Permet d'afficher la grille représentant les probabilités de présence d'un bateau
tout au long d'une partie

Auteur :
    Romain Jaugey
"""



def intersection(l1, l2):
    for x in l1:
        if x in l2:
            return True
    return False

class IA():
    def __init__(self):
        self.grille_attaque = [[0 for i in range(10)] for i in range(10)]  # 0 si pas tiré sur la case, -1 si tiré dans le vide et 1, 2, 3, 4, 5 si un bateau est touché et 8 si coulé
        self.bateau = [[1, 5, "porte-avions"], [2, 4, "croiseur"], [3, 3, "contre-torpilleur"], [4, 3, "contre-torpilleur"], [5, 2, "torpilleur"]]
        self.grille_def = self.place_bateau(self.bateau)
        self.en_coulage = []
        self.liste_bateaux_en_jeu = [True, True, True, True, True]
        self.mem = []
        self.grille_probas = [[0 for i in range(10)] for j in range(10)]

    def place_bateau(self, bat):
        g = self.create_grille_def(bat)
        def verif_bonne_grille(grille):
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

    def create_grille_def(self, bat):  # on place de manière aléatoire sur le plateau les 5 bateaux (1 par 1) sans chevauchement et sans dépassement du plateau
        grille_og = [[0 for i in range(10)] for i in range(10)]
        test = [True, True, True, True, True]
        while True in test:
            b = test.index(True)  # on cherche un bateau qui n'est pas encore placé (True si non placé et False si déjà posé sur le plateau)
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
            # print(l, a, b, self.en_coulage, self.mem)
            if self.grille_attaque[a][b] == ind:
                # print("tIN")
                aux.append(l)
        # print(aux, "AUX")
        for x in aux:
            # print(x)
            if x in self.en_coulage:
                self.en_coulage.remove(x)
            if x in self.mem:
                self.mem.remove(x)

    def verif_fini(self):
        return (True not in self.liste_bateaux_en_jeu)

    def defend(self, ennemi, i, j):  # -9 si l'adversaire a tiré dans le vide et -x si l'adversaire a touche un bateau numero x
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
                # print(x)
                ennemi.liste_bateaux_en_jeu[x-1] = False

    def va_couler(self, ind):
        c = 0
        for i in range(10):
            for j in range(10):
                if ind == self.grille_def[i][j]:
                    c += 1
        return (c == 1)

    def est_mort(self, ind):
        c = 0
        for i in range(10):
            for j in range(10):
                if self.grille_attaque[i][j] == ind:
                    c += 1
        return(c == self.bateau[ind-1][1])

    def show_attaque(self):
        return np.matrix(self.grille_attaque)

    def show_def(self):
        return np.matrix(self.grille_def)

    def tone_into_hex(self, p):
        ton = int((1-p) * 255)
        lettres = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
        fin = lettres[ton % 16]
        debut = lettres[ton//16]
        ton = debut+fin
        ton = "#" + (3*ton)
        return ton

    def show_probas(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.axis([0, 10, 0, 10])

        arf = [ax.xaxis, ax.yaxis]
        for axis in range(2):
            arf[axis].set_minor_locator(MultipleLocator(1))
            if axis == 0:
                arf[axis].set_ticks(np.arange(10) + 0.5)
            else:
                arf[axis].set_ticks(np.array([9-i for i in range(10)]) + 0.5)
            arf[axis].set_ticklabels(range(10))


        maxi = np.amax(self.grille_probas)
        maxi = max(maxi, 1)
        for i in range(10):
            for j in range(10):
                x = self.grille_probas[i][j]
                f = self.tone_into_hex(x/maxi)
                rect = ptc.Rectangle((j, 9-i), 1, 1, color=f )
                ax.add_patch(rect)


        ax.grid(which='minor')
        plt.show()

class TEMOIN(IA):
    def attaque(self, ennemi):
        i, j = 0, 0
        x = ennemi.grille_def[i][j]
        if x == 0:
            self.grille_attaque[i][j] = 0
        else:
            self.grille_attaque[i][j] = x
        return(i, j)

class DIFFICILE(IA):

    def __init__(self):
        super().__init__()
        self.touche = False
        self.coule = False
        self.side = ["haut", "droite", "bas", "gauche"]
        self.direction = None
        self.bateau_en_cours = 0

    def compte_possibilites_recherche(self, i, j):
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
        c_list = [0, 0, 0, 0]  #h, g, b, d
        c_ind = [[i-1, j], [i, j-1], [i+1, j], [i, j+1]]
        ind = self.grille_attaque[i][j]
        if direction == None:
            if 0 <= i-1 and self.grille_attaque[i-1][j] == ind:
                self.direction = "v"
            elif i+1 < 10 and self.grille_attaque[i+1][j] == ind:
                self.direction = "v"
            elif 0 <= j-1 and self.grille_attaque[i][j-1] == ind:
                self.direction = "h"
            elif j+1 < 10 and self.grille_attaque[i][j+1] == ind:
                self.direction = "h"

        if direction == None:
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
            # print(c_list, c_ind, "YOOOOOEGZGZERGZERGRezgrer")
            for a in range(4):
                c = c_list[a]
                if c > maxi:
                    maxi = c
                    x, y = c_ind[a]
                    # print(ind, ennemi.grille_def[x][y], "LE PB DOIT ETRE LA")
                    if ennemi.grille_def[x][y] == ind:
                        if a % 2 == 0:
                            self.direction = "v"
                        else:
                            self.direction = "h"
                    else:
                        self.direction = None

        elif direction == "v":
            l_t = self.en_coulage[0]
            u, v = l_t[0], l_t[1]
            line = [self.grille_attaque[a][v] for a in range(10)]
            ind = line[u]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            # print(range_list)
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

        else:
            l_t = self.en_coulage[0]
            u, v = l_t[0], l_t[1]
            line = [self.grille_attaque[u][a] for a in range(10)]
            ind = line[v]
            range_list = [k for k in range(-9, 10)]
            range_list.remove(self.bateau_en_cours)
            range_list.remove(0)
            # print(range_list)
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

        self.grille_probas = [[0 for p in range(10)] for p in range(10)]
        for o in range(4):
            a, b = c_ind[o][0], c_ind[o][1]
            if a in range(10) and b in range(10):
                self.grille_probas[a][b] = c_list[o]
        return(x, y)

    def attaque(self, ennemi):    #ca tire un coup au bout en trop
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
            # print("FIN")

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

        else:
            h, g = self.en_coulage[0]
            self.bateau_en_cours = self.grille_attaque[h][g]
            i, j = self.compte_possibilites_touche(h, g, self.direction, ennemi)

            ind = ennemi.grille_def[i][j]
            if ind == 0:
                self.grille_attaque[i][j] = -1
            elif ind > 0:
                self.grille_attaque[i][j] = ind
                if not self.est_mort(ind):
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

class DUELTEST():
    def __init__(self):
        self.compteur = 0

    def combat(self, ia):
        j1 = TEMOIN()
        j2 = ia
        while not j2.verif_fini() and self.compteur < 100:

            self.etape_2_sur_1(j1, j2)
            self.compteur += 1

            # print("FIN DU TOUR")
        return(self.compteur)

    def etape_1_sur_2(self, j1, j2):
        x, y = j1.attaque(j2)
        j2.defend(j1, x, y)

    def etape_2_sur_1(self, j1, j2):
        x, y = j2.attaque(j1)
        j2.show_probas()
        j1.defend(j2, x, y)


j = DIFFICILE()
comb = DUELTEST()
print(comb.combat(j))
