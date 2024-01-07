from block_encryption import *
from datablocks       import *

datablock = Datablock("Я не люблю фатального исхода. От жизни никогда не устаю. Я не люблю любое время года, когда веселых песен не пою.")
key = Datablock(0xffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff)

datablockEnc = easy_replacement(datablock, key, True)

# print(datablockEnc.asText())

datablockDenc = easy_replacement(datablockEnc, key, False)

# print(datablockDenc.asText())

Datablock.elemSize = 64
IV = Datablock(0x12345678).setBitSize(32)
datablockgam = gamming(datablock, IV, key)

# print(datablockgam.asText())

datablockgamopen = gamming(datablockgam, IV, key)

# print(datablockgamopen.asText())

IV = Datablock(0x1234567890abcdef234567890abcdef1).setBitSize(128)
datablockgof     = gamming_with_output_feedback(datablock, IV, key)

# print(datablockgof.asText())

datablockgofopen = gamming_with_output_feedback(datablockgof, IV, key)

# print(datablockgofopen.asText())

datablockgcf     = gamming_with_cipher_feedback(datablock, IV, key, True)

# print(datablockgcf.asText())

datablockgcfopen = gamming_with_cipher_feedback(datablockgcf, IV, key, False)

# print(datablockgcfopen.asText())

IV = Datablock(0x1234567890abcdef234567890abcdef134567890abcdef12).setBitSize(192)

datablockcbc = cipher_block_chaining(datablock,IV,key,True)

# print(datablockcbc.asText())

datablockcbcopen = cipher_block_chaining(datablockcbc,IV,key,False)

# print(datablockcbcopen.asText())

MAC = message_authentication_code(datablock, key, 32)

print(MAC.asInt(16))