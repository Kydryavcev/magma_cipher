# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 08:58:34 2023

@author: mlgluharev
"""

from datablocks import Datablock
from math import *
from random import randint
import numpy as np

# Функция rndtransp() возвращает случайную перестановку элементов списка lst
def rndtransp(lst):
    res = lst.copy()
    l = len(res)
    for i in range(0, l):
        j = randint(i, l - 1)
        if j != i:
            res[i], res[j] = res[j], res[i]
    return res

# Функция entropy() вычисляет среднюю энтропию элемента в блоке данных
# и возвращает ее.
#
# Параметры:
#     block - блок данных;
#     sz - размер элемента в битах.

def entropy(block, sz):
    oldSz = Datablock.elemSize
    Datablock.elemSize = sz
    probabilityTable = block.getProbabilityTable()
    h = 0
    for k in probabilityTable:
        p = probabilityTable[k]
        h -= p * log(p, 2)
        
    Datablock.elemSize = oldSz
    
    return h    


# Функция truthTable() преобразует последовательность значений, хранимых
# в блоке block, в таблицу истинности
def truthTable(dblock):
    arr = dblock.asBitArray()
    tt = np.array(arr).reshape(len(dblock), Datablock.elemSize)

    return tt

# Функция extTruthTable() создает расширенный вариант таблицы истинности tt: добавляет столбцы значений
# линейных комбинаций функций
def extTruthTable(tt):
    koefsIntArr = np.arange(1, 2 ** Datablock.elemSize)
    arr = []
    for ki in koefsIntArr:
        arr.append(Datablock(int(ki)).setBitSize(Datablock.elemSize).asBitArray())

    koef = np.array(arr).T
    res = np.dot(tt, koef)
    res = res % 2
    
    return res
    
# Функция conjugateTruthTable() возвращает таблицу значений сопряженных функций
# Параметр tt - таблица истинности
def conjugateTruthTable(tt):
    ctt = tt.copy()
    for i in range(0, len(ctt)):
        for j in range(0, len(ctt[i])):
            if ctt[i][j] == 0:
                ctt[i][j] = 1
            elif ctt[i][j] == 1:
                ctt[i][j] = -1
            else:
                raise Exception("Таблица истинноста содержит недопустимое значение ")
    return ctt

# Функция Hadamard() строит матрицу Адамара размером 2**n на 2**n
def Hadamard(n):
    if n < 0:
        raise Exception("Указан недопустимый размер матрицы ", n)
    if n == 0:
        return np.array([[1]])
    
    had = Hadamard(n - 1)
    l = len(had)
    res = np.zeros((2 * l, 2 * l))
    
    for i in range(0, l):
        for j in range(0, l):
            hij = had[i][j]
            res[i][j] = res[i][j + l] = res[i + l][j] = hij
            res[i + l][j + l] = -hij
    
    return res

# Функция оценивает сбалансированность компонентных булевых функций.
#
# Параметр ua - таблица спектров Уолша-Адамара.
# Номер строки таблицы - десятично представление вектора alpha.
# Номер столбца - номер компонентной булевой функции.
#
# Возвращаемое значение: список номеров сбалансированных функций.
def balanced(ua):
    res = []
    for j in range(0, len(ua[0])):
        if ua[0][j] == 0:
            res.append(j)
    return res

# Функция corrImmOrders() оценивает корреляционную иммунность компонентных булевых функций.
#
# Параметр ua - таблица спектров Уолша-Адамара.
# Номер строки таблицы - десятично представление вектора alpha.
# Номер столбца - номер компонентной булевой функции.
#
# Возвращаемое значение: список значений порядка корреляционной иммунности.
# Порядковый номер элемента списка соответствует номеру компонентной булевой функции.
# Нулевое значение - функция не корреляционно-иммунная.
def corrImmOrders(ua):
    res = np.ones((Datablock.elemSize))
    for w in range(1, ceil(log2(len(ua)))):
        for i in range(1, len(ua) - 1):
            if Datablock(i).wt() == w:
                for j in range(0, len(ua[i])):
                    uaij = ua[i][j]
                    resj = res[j]
                    if ua[i][j] != 0 and res[j] == w:
                        res[j] = res[j] - 1
        for k in range(0, len(res)):
            if res[k] == w:
                res[k] += 1
    return res

# Функция corrEffective() оценивает корреляционную эффективность компонентных булевых функций.
#
# Параметр ua - таблица спектров Уолша-Адамара.
# Номер строки таблицы - десятично представление вектора alpha.
# Номер столбца - номер компонентной булевой функции.
#
# Возвращаемое значение: список номеров корреляционно-эффективных функций.
def corrEffective(ua):
    res = []
    for j in range(0, len(ua[0])):
        count = 0
        for i in range(0, len(ua)):
            if ua[i][j] == 0:
                count += 1
        if count >= len(ua) / 2:
            res.append(j)
    return res

# Функция nonlinearity() оценивает нелинейность компонентных булевых функций.
#
# Параметр ua - таблица спектров Уолша-Адамара.
# Номер строки таблицы - десятично представление вектора alpha.
# Номер столбца - номер компонентной булевой функции.
#
# Возвращаемое значение: список номеров корреляционно-эффективных функций.
# Порядковый номер элемента списка соответствует номеру компонентной булевой функции.
def nonlinearity(ua):
    res = []
    for j in range(0, len(ua[0])):
        nl = 0
        for i in range(0, len(ua)):
            if abs(ua[i][j]) > nl:
                nl = abs(ua[i][j])
        nl *= -0.5
        n = ceil(log2(len(ua)))
        nl += 2 ** (n - 1)
        res.append(nl)
    return res

# Функция maxNonlinearity() возвращает максимальную нелинейность компонентной
# булевой функции, количество аргументов которой равно n
def maxNonlinearity(n):
    return floor(2 ** (n - 1) - 2 ** (n / 2 - 1))

# Функция autoCorr() возвращает коэффициент автокорреляции функции.
#
# Параметры:
#           ctt - таблица значений сопряженных функций;
#           betta - двоичный вектор betta;
#           j - номер фунции
def autoCorr(ctt, betta, j):
    r = 0
    l = len(ctt)
    for i in range(0, len(ctt)):
        r += ctt[i][j] * ctt[i ^ betta][j] / l
    return r

# Функция autoCorrTable() строит таблицу коэффициентов автокорреляции
# для сопряженных функций, заданных таблицей ctt
#
# В результирующей таблице:
#   номер строки - десятичное представлние вектора betta;
#   номер столбца - номер сопряженной функции
def autoCorrTable(ctt):
    rows = len(ctt)
    cols = len(ctt[0])
    res = np.zeros((rows, cols))
    
    for betta in range(0, rows):
        for j in range(0, cols):
            res[betta][j] = autoCorr(ctt, betta, j)
    return res

# Функция pc() оценивает соответствие булевой функции критерию распространения
# изменений порядка k. Кроме порядка, параметрами функции являются таблица
# коэффициентов автокорреляции и номер компонентной булевой функции.
#
# Возвращаемое значение:
#    True - соответствует;
#    False - не соответствует.
def pc(ac, j, k):
    res = True
    for i in range(0, len(ac)):
        if Datablock(i).wt() in range(1, k + 1) and ac[i][j] != 0:
            res = False
    return res

