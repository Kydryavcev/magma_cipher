from magma_cipher import magma_cipher
from datablocks   import *
from typing       import *

def easy_replacement(datablock: Datablock, key: Datablock, direction: bool) -> Datablock:
    '''
    Использование шифра "Магма" в режиме *простой замены*.\n
    Параметры:\n
    **datablock** - блок данных для шифрования;\n
    **key**       - ключ шифрования;\n
    **direction** - предписывает выполнять шифрование (True) или расшифрование (False).\n
    Возвращаемое значение:\n
    Зашифрованый блок данных (direction = True), расшифрованный блок данных (direction = False).
    '''
    oldSize = Datablock.elemSize

    Datablock.elemSize = 64

    if direction:
        datablock = datablock_addition(datablock)

    datablock = magma_cipher(datablock, key, direction)

    if not direction:
        datablock = datablock_trim(datablock)

    Datablock.elemSize = oldSize

    return datablock

def gamming(datablock: Datablock, IV: Datablock, key: Datablock) -> Datablock:
    '''
    Использование шифра "Магма" в режиме гаммирования.\n
    Параметры:\n
    **datablock** - блок данных для гаммирования;\n
    **IV**        - синхропосылка (initializing value), предназначенная для инициализации алгоритма шифрования;\n
    **key**       - ключ шифрования.\n
    Возвращаемое значение:\n
    Зашифрованный/расшифрованный блок данных.
    '''
    if  Datablock.elemSize > 64:
        raise Exception("Длина блока превышает допустимое значение.")

    if IV.getBitSize() != 32:
        raise Exception("Синхропосылка некоректная!")

    CTR = (IV.clone() << 32).setBitSize(64)

    result = Datablock().setBitSize(datablock.getBitSize())

    for i in range(0, len(datablock)):
        gamma = magma_cipher(CTR, key, True)
        gamma.setBitSize(Datablock.elemSize, True)

        result[i] = (datablock[i] ^ gamma).setBitSize(datablock[i].getBitSize(), True)

        CTR = (CTR + 1).setBitSize(64, True)

    result.setBitSize(datablock.getBitSize(), True)

    return result

def gamming_with_output_feedback(datablock: Datablock, IV: Datablock, key: Datablock) -> Datablock:
    '''Использование шифра "Магма" в режиме гаммирования с обратной связью по выходу.'''
    if  Datablock.elemSize > 64:
        raise Exception("Длина блока превышает допустимое значение.")

    if IV.getBitSize() % 64 != 0 or IV.getBitSize() == 0:
        raise Exception("Синхропосылка некоректная!")

    result = Datablock().setBitSize(datablock.getBitSize())

    R = IV.clone()

    for i in range(0, len(datablock)):
        MSB64 = Datablock((R.asBitArray())[-64:]).setBitSize(64)

        gamma = magma_cipher(MSB64, key, True)

        result[i] = (datablock[i] ^ gamma).setBitSize(datablock[i].getBitSize(), True)

        R = ((R << 64) | gamma).setBitSize(IV.getBitSize(), True)

    result.setBitSize(datablock.getBitSize(), True)

    return result

def gamming_with_cipher_feedback(datablock: Datablock, IV: Datablock, key: Datablock, direction: bool) -> Datablock:
    '''Использование шифра "Магма" в режиме гаммирования с обратной связью по шифртексту.'''
    if  Datablock.elemSize > 64:
        raise Exception("Длина блока превышает допустимое значение.")

    if IV.getBitSize() < 64:
        raise Exception("Синхропосылка некоректная!")

    result = Datablock().setBitSize(datablock.getBitSize())

    R = IV.clone()

    for i in range(0, len(datablock)):
        MSB64 = Datablock((R.asBitArray())[-64:]).setBitSize(64)

        gamma = magmaCipher(MSB64, key, True)

        result[i] = (datablock[i] ^ gamma).setBitSize(datablock[i].getBitSize(), True)

        R = ((R << Datablock.elemSize) | (result[i] if direction else datablock[i])).setBitSize(IV.getBitSize(), True)

    result.setBitSize(datablock.getBitSize(), True)

    return result

def cipher_block_chaining(datablock: Datablock, IV: Datablock, key: Datablock, direction: bool) -> Datablock:
    '''Использование шифра "Магма" в режиме замены с зацеплением.'''
    if IV.getBitSize() % 64 != 0 or IV.getBitSize() == 0:
        raise Exception("Синхропосылка некоректная!")

    R = IV.clone()

    if direction:
        datablock = datablock_addition(datablock)

    result = Datablock().setBitSize(datablock.getBitSize())

    for i in range(0, len(datablock)):
        MSB64 = Datablock((R.asBitArray())[-64:]).setBitSize(64)

        result[i] = magma_cipher((datablock[i] ^ MSB64).setBitSize(64), key, True) if direction else (magma_cipher(datablock[i], key, False) ^ MSB64)

        R = ((R << 64) | (result[i] if direction else datablock[i])).setBitSize(IV.getBitSize(), True)

    if not direction:
        datablock = datablock_trim(datablock)

    return result

def message_authentication_code(datablock: Datablock, key: Datablock, lenth: int) -> Datablock:
    '''Использование шифра "Магма" в режиме выработки имитовставки.'''
    if lenth > 64 or lenth <= 0:
        raise Exception("Заданная длинна для имитоставки не коректна.")

    oldSize = Datablock.elemSize

    Datablock.elemSize = 64

    R = magma_cipher(Datablock().setBitSize(64), key, True)

    if R.asBitArray()[-1] == 0:
        K1 = (R << 1).setBitSize(64, True)
    else:
        K1 = ((R << 1) ^ Datablock(0x1b)).setBitSize(64, True)

    if K1.asBitArray()[-1] == 0:
        K2 = (K1 << 1).setBitSize(64, True)
    else:
        K2 = ((K1 << 1) ^ Datablock(0x1b)).setBitSize(64, True)

    C = Datablock().setBitSize(64)

    for i in range(0, len(datablock) - 1):
        C = magma_cipher((datablock[i] ^ C).setBitSize(64), key, True)

    if datablock[len(datablock) - 1].getBitSize() == 64:
        lastDatablock = datablock[len(datablock) - 1]
        K = K1
    else:
        lastDatablock = datablock_addition(datablock[len(datablock) - 1])
        K = K2

    MAC = Datablock(magma_cipher((lastDatablock ^ C ^ K).setBitSize(64), key, True).asBitArray()[-lenth:])

    Datablock.elemSize = oldSize

    return MAC

def datablock_addition(datablock: Datablock) -> Datablock:
    '''
    Дополняет блок данных до размера кратново 64 битам. По следующей процедуре:
    Если размер последнего элемента блока данных datablock[-1] равен r < 64, то к нему приписывается
    одна единица и недостающие до полного элемена количество нулей:\n
    datablock[-1] = datablock[-1]||1||0^(64-r-1),\n
    где a||b - конкатенация двоичных векторов.\n
    Если размер последнего элемента блока данных datablock[-1] равен 64, то к блоку данных будет
    приписан дополнительный элемент: ||1||0^(63).
    '''
    datablockResized = datablock.clone()

    dataSize = datablockResized.getBitSize()

    additionBit = 64 - dataSize % 64

    datablockResized.bitConcat(Datablock(1 << additionBit - 1))

    datablockResized.setBitSize(dataSize + additionBit)

    return datablockResized

def datablock_trim(datablock: Datablock) -> Datablock:
    '''Выполняет операцию обратную функции datablock_addition.'''
    Datablock.elemSize = 1

    datablockResized = datablock.clone()

    realLenth = datablockResized.getBitSize()

    while datablockResized[realLenth - 1].asInt(2) == 0:
        realLenth -= 1

    datablockResized.setBitSize(realLenth - 1, True)

    return datablockResized