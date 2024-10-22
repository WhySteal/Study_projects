import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random


""" Настраиваемые параметры программы---------------------"""
STUDENT = "Перехожих A.Д, perehojih2001@yandex.ru, Проектирование интеллектуальных систем, 2024 год."
N = 10 #Размерность
GAMMA = 20 #Гамма функция для усиления шансов хороших результатов (значение 1 для сброса функции)
POPULATIONSIZE = 20 #Размер популяции
GENERATION = 70 #Количество поколений
SELECTTYPE = "Tournament" #Варианты Селекции Tournament, Roulet
MUTATIONCHANCE = 0.2 #Вероятность мутации
PCOUT = 0 #Компьютор - отправитель
PCIN = N-1 #Компьютер - получатель
STEPBYSTEP = False #Режим работы (пошаговый/циклический)
AUTO = True #Автозаполнение графа
""" ------------------------------------------------------  """

#----Метод рулетки-----
def roulet(fitList, waysList):
    sum = 0
    ch = []
    for i in range(len(fitList)):
        sum+= fitList[i]
    for i in range(len(fitList)):
        ch.append((1 / (1 + (fitList[i]/sum)))** GAMMA / (POPULATIONSIZE + 1))
    p = random.choices(waysList, ch)
    return p[0]


#-----Метод турнира------
def tournament(groupSize, waysList, fitList):
    winners = []
    for i in range(0, len(waysList) - 1 - groupSize, groupSize): #Номер группы
        minI = 100000
        minWay = 100000
        for j in range(groupSize):
            if fitList[i + j] < minWay:
                minI = i + j
                minWay = fitList[i + j]
        winners.append(waysList[minI])
    return(winners)


#Скрещивание 1 точка_________________________________
def cross_1Point(osob1, osob2):
    os1 = []
    os2 = []
    for i in range(len(osob1)//2):
        os1.append(osob1[i])
        os2.append(osob2[i])
    for i in range(len(osob2)//2, len(osob2)):
        os1.append(osob2[i])
        os2.append(osob1[i])
    return os1, os2


#Перебор всех возможных путей
def allWays(start, end, graph, path=[]):
    path = path + [start]

    if start == end:
        return [path]
    all_paths = []
    for vertex in graph[start]:
        if vertex in path:
            continue
        new_paths = allWays(vertex, end, graph, path)
        for p in new_paths:
            all_paths.append(p)
    return all_paths


#Задание графа и его изображение ------------------------------------------------
Graph = nx.Graph()

# Матрица трансцендентности
mat = np.ones((N, N)) * 1000
for i in range(N):
    Graph.add_node(i)
    for j in range(N):
        if i == j:
            mat[i,j] = 0

stop = False
edge_labels = {}
if AUTO == False:
    while stop != True:
        insert = input('Введите узлы сети и пропускную способность между '
                    'ними (для остановки ввода данных введите'
                    '"end"): ').split(' ')
        if insert[0] == 'end':
            stop = True
        else:
            # Добавляем узлы и значения ребер
            Graph.add_edge(int(insert[0]), int(insert[1]))
            edge_labels[(int(insert[0]), int(insert[1]))] = insert[2]
            # Заполнение матрицы
            mat[int(insert[0])][int(insert[1])] = int(insert[2])
            mat[int(insert[1])][int(insert[0])] = int(insert[2])
else: #Если авто заполнение включено
    k = random.randint(5, N**2 - 1)
    for i in range(k):
        a = random.randint(0,N-1)
        b = random.randint(0,N-1)
        c = random.randint(1, 200)
        if a != b:
            insert = [a, b, c]
# Добавляем узлы и значения ребер
            Graph.add_edge(int(insert[0]), int(insert[1]))
            edge_labels[(int(insert[0]), int(insert[1]))] = insert[2]
# Заполнение матрицы
            mat[int(insert[0])][int(insert[1])] = int(insert[2])
            mat[int(insert[1])][int(insert[0])] = int(insert[2])
for i in range(N):
    Graph.add_node(i)
    for j in range(N):
        if i == j:
            mat[i,j] = 0
pos = nx.spring_layout(Graph)
nx.draw(Graph, pos, with_labels=True)
nx.draw_networkx_edge_labels(Graph, pos, edge_labels=edge_labels, font_color='red')
print(mat)
plt.show()
# ----------------------------------------------------------------------------------
# Инициализация начальной популяции --------------------------------------------


Ways = allWays(PCIN, PCOUT, Graph)

genSize = 0
for i in range(len(Ways)):
    if len(Ways[i]) > genSize:
        genSize = len(Ways[i])
for i in range(len(Ways)):
    while len(Ways[i]) < genSize:
        Ways[i].append(0)

FitSize = [0] * len(Ways)
for i in range(len(Ways)):
    for j in range(genSize - 1):
        FitSize[i] += mat[Ways[i][j], Ways[i][j+1]]
"""
Ways = POPULATIONSIZE * [[]]
FitSize = [0]*POPULATIONSIZE
genSize = 0
for i in range(POPULATIONSIZE):
    Ways[i] = []*N
    Ways[i].append(PCOUT)
    while Ways[i][-1] != PCIN:
        Ways[i].append(random.randint(1, N-1))
        FitSize[i] += mat[Ways[i][-2], Ways[i][-1]]
        if Ways[i][-1] == Ways[i][-2] or mat [Ways[i][-2], Ways[i][-1]] == 1000:
            FitSize[i] -= mat[Ways[i][-2], Ways[i][-1]]
            Ways[i].pop()
    if len(Ways[i]) > genSize:
        genSize = len(Ways[i])
for i in range(POPULATIONSIZE):
    while len(Ways[i]) < genSize:
        if (len(Ways[i]) % 2 == 0):
            Ways[i].append(N-1)
        else: Ways[i].insert(0, PCOUT)            """
#-----------------------------------------------------------------------------------
#Селекция___________________________________________________
midList = []
maxList = []
minList = []
for epoch in range(GENERATION):
    #Для метода рулетки
    WaysNew_roulet = []
    for i in range(POPULATIONSIZE):
        WaysNew_roulet.append(roulet(FitSize, Ways))

    #Для метода турнира
    WaysNew_tournament = []
    GROUPSIZE = 2
    WaysNew_tournament = (tournament(GROUPSIZE, Ways, FitSize))

    #Скрещивание
    WaysCross = []
    if SELECTTYPE == "Roulet":
        for j in range(0, len(WaysNew_roulet) - 1, 2):
            os1, os2 = cross_1Point(WaysNew_roulet[j], WaysNew_roulet[j+1])
            WaysCross.append(os1)
            WaysCross.append(os2)
        
    if SELECTTYPE == "Tournament":
        for j in range(0, len(WaysNew_tournament) - 1, 2):
            os1, os2 = cross_1Point(WaysNew_tournament[j], WaysNew_tournament[j+1])
            WaysCross.append(os1)
            WaysCross.append(os2)
        for j in range(0, len(WaysNew_tournament) - 3, 2):
            os1, os2 = cross_1Point(WaysNew_tournament[j], WaysNew_tournament[N-1-j])
            WaysCross.append(os1)
            WaysCross.append(os2)

    #Мутация____________
    for i in range(len(WaysCross)):
        pm = random.random()
        if pm <= MUTATIONCHANCE:
            p1 = random.randint(1, genSize - 2)
            p2 = random.randint(1, genSize - 2)
            promej = WaysCross[i][p1]
            WaysCross[i][p1] = WaysCross[i][p2]
            WaysCross[i][p2] = promej
            Ways = WaysCross
    #Нахождение фитнес функции
    FitSize = [0] * len(Ways)
    midFit = 0
    maxFit = 0
    minFit = 100000
    for i in range(len(Ways)):
        for j in range(genSize - 1):
            FitSize[i] += mat[Ways[i][j], Ways[i][j+1]]
        midFit += FitSize[i]
        if FitSize[i] < minFit:
            minFit = FitSize[i]
        if FitSize[i] > maxFit:
            maxFit = FitSize[i]
    midFit = midFit / len(FitSize)
    print("среднее значение приспособленности поколения: ", midFit)
    midList.append(midFit)
    maxList.append(maxFit)
    minList.append(minFit)

x = np.arange(0, GENERATION, 1)
fig = plt.figure(figsize=(15, 7))
plt.plot(x, maxList, label='Максимальное значение')
plt.plot(x, minList, label='Минимальное значение')
plt.plot(x, midList, label='Среднее значение')

plt.title("График зависимости значения функции приспособленности от номера поколения")
plt.xlabel("Поколение")
plt.ylabel('Значение функции приспособленности')
plt.grid(True)
plt.legend(loc='best', fontsize=10)
plt.xlim(0, GENERATION-1)
plt.xticks(np.arange(0, GENERATION, 1))

plt.show()