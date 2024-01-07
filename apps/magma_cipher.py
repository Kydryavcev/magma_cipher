from datablocks import *
from typing import *

# Значения подстановок, записанные в виде массивов (кортежей)
SUBSTITUTION_VALUES = ((12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1),
                       (6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15),
                       (11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0),
                       (12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11),
                       (7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12),
                       (5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0),
                       (8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7),
                       (1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2))

def magma_cipher(datablock: Datablock, key: Datablock, direction: bool) -> Datablock:
    if key.getBitSize() != 256:
        raise Exception("Ключ не подходящего размера.")

    datablockSize = datablock.getBitSize()

    if datablockSize % 64 != 0:
        raise Exception("Блок данных не подходящего размера.")

    result = Datablock().setBitSize(datablockSize)

    oldSize = Datablock.elemSize

    Datablock.elemSize = 64

    for i in range(0, len(datablock)):
        result[i] = __magma_round(datablock[i], key, direction)

    Datablock.elemSize = oldSize

    return result

def __magma_round(datablock: Datablock, key: Datablock, direction: bool) -> Datablock:
    if datablock.getBitSize() != 64:
        raise Exception("Блок данных не подходящего размера. (Рас)шифрование невозможно.")

    if key.getBitSize() != 256:
        raise Exception("Ключ не подходящего размера. (Рас)шифрование невозможно.")

    oldSize = Datablock.elemSize

    Datablock.elemSize = 32

    dataSubblock1 = datablock[1]
    dataSubblock0 = datablock[0]

    for i in range(0,31):
        dataSubblock1, dataSubblock0 = __G(dataSubblock1, dataSubblock0, __getitemKey(i, key) if direction else __getitemKey(31 - i, key))

    result = __Gl(dataSubblock1, dataSubblock0,  __getitemKey(0, key) if direction else __getitemKey(31, key))

    Datablock.elemSize = oldSize

    return result

def __t(datablock: Datablock) -> Datablock:
    if datablock.getBitSize() != 32:
        raise Exception("Подстановка невозможна.")

    Datablock.elemSize = 4

    datablock.substPolyMixedAbc(SUBSTITUTION_VALUES, True)

    return datablock

def __g(datablock: Datablock, key: Datablock) -> Datablock:
    if datablock.getBitSize() != 32 or key.getBitSize() != 32:
        raise Exception("Подстановка невозможна.")
    sum = (datablock + key) % 2 ** 32
    return __t(((datablock + key) % 2 ** 32).setBitSize(32)).cshl(11)

def __G(datablock1: Datablock, datablock0: Datablock, key: Datablock) -> Tuple[Datablock, Datablock]:
    if datablock1.getBitSize() != 32 or datablock0.getBitSize() != 32 or key.getBitSize() != 32:
        raise Exception("Перестановка невозможна.")

    return (datablock0, (__g(datablock0, key) ^ datablock1).setBitSize(32))

def __Gl(datablock1: Datablock, datablock0: Datablock, key: Datablock) -> Datablock:
    if datablock1.getBitSize() != 32 or datablock0.getBitSize() != 32 or key.getBitSize() != 32:
        raise Exception("Перестановка невозможна.")

    return datablock0.concat(__g(datablock0, key) ^ datablock1)

def __getitemKey(index: int, key: Datablock) -> Datablock:
    oldSize = Datablock.elemSize

    Datablock.elemSize = 32

    if index < 24:
        result = key[7 - (index % 8)]
    else:
        result = key[index % 8]

    Datablock.elemSize = oldSize

    return result