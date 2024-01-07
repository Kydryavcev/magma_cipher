from block_encryption import *
from datablocks       import *

datablock = Datablock("Я не люблю фатального исхода. От жизни никогда не устаю. Я не люблю любое время года, когда веселых песен не пою.")
key = Datablock(0xffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff)
# datablock = Datablock(0x92def06b3c130a59db54c704f8189d204a98fb2e67a8024c8912409b17b57e41)
#datablock = Datablock(0x8912409b17b57e414a98fb2e67a8024cdb54c704f8189d2092def06b3c130a59)
#key = Datablock(0xffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff)


datablockEnc = easy_replacement(datablock, key, True)

print(datablockEnc.asText())
# print(datablockEnc.asInt(16))

datablockDenc = easy_replacement(datablockEnc, key, False)

print(datablockDenc.asText())
# print(datablockDenc.asInt(16))
# exit(0)
Datablock.elemSize = 64
IV = Datablock(0x12345678).setBitSize(32)
datablockgam = gamming(datablock, IV, key)
#
# print(datablockgam.asText())
print(datablockgam.asInt(16))
#
datablockgamopen = gamming(datablockgam, IV, key)
#
# print(datablockgamopen.asText())
print(datablockgamopen.asInt(16))
IV = Datablock(0x1234567890abcdef234567890abcdef1).setBitSize(128)
datablockgof     = gamming_with_output_feedback(datablock, IV, key)
# print(datablockgof.asInt(16))
datablockgofopen = gamming_with_output_feedback(datablockgof, IV, key)

# print(datablockgofopen.asText())
# print(datablockgofopen.asInt(16))

# datablockgcf     = gamming_with_cipher_feedback(datablock, IV, key, True)
# print(datablockgcf.asInt(16))
# datablockgcfopen = gamming_with_cipher_feedback(datablockgcf, IV, key, False)
# # print(datablockgcfopen.asText())
# print(datablockgcfopen.asInt(16))
# IV = Datablock(0x1234567890abcdef234567890abcdef134567890abcdef12).setBitSize(192)
# datablockcbc = cipher_block_chaining(datablock,IV,key,True)
# print(datablockcbc.asInt(16))
# datablockcbcopen = cipher_block_chaining(datablockcbc,IV,key,False)
# print(datablockcbcopen.asInt(16))

# MAC = message_authentication_code(datablock, key, 32)
#
# print(MAC.asInt(16))