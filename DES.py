def _hex2bits(h):
    h = h.strip().upper()
    mp = {
        '0':"0000",'1':"0001",'2':"0010",'3':"0011",'4':"0100",'5':"0101",
        '6':"0110",'7':"0111",'8':"1000",'9':"1001",'A':"1010",'B':"1011",
        'C':"1100",'D':"1101",'E':"1110",'F':"1111"
    }
    out = ""
    for c in h:
        if c not in mp: raise ValueError("hex tidak valid")
        out += mp[c]
    return out

def _bits2hex(b):
    if len(b) % 4 != 0: raise ValueError("panjang bit bukan kelipatan 4")
    mp = {
        "0000":'0',"0001":'1',"0010":'2',"0011":'3',"0100":'4',"0101":'5',
        "0110":'6',"0111":'7',"1000":'8',"1001":'9',"1010":'A',"1011":'B',
        "1100":'C',"1101":'D',"1110":'E',"1111":'F'
    }
    out = ""
    for i in range(0, len(b), 4):
        out += mp[b[i:i+4]]
    return out

def _xor_bits(a, b):
    return "".join("0" if x==y else "1" for x,y in zip(a,b))

def _permute(bits, table):
    return "".join(bits[i-1] for i in table)

def _lrot(s, n):
    n = n % len(s)
    return s[n:] + s[:n]

# ---------- tabel DES ----------
IP = [
 58,50,42,34,26,18,10,2, 60,52,44,36,28,20,12,4, 62,54,46,38,30,22,14,6,
 64,56,48,40,32,24,16,8, 57,49,41,33,25,17,9,1,  59,51,43,35,27,19,11,3,
 61,53,45,37,29,21,13,5, 63,55,47,39,31,23,15,7
]
FP = [
 40,8,48,16,56,24,64,32, 39,7,47,15,55,23,63,31, 38,6,46,14,54,22,62,30,
 37,5,45,13,53,21,61,29, 36,4,44,12,52,20,60,28, 35,3,43,11,51,19,59,27,
 34,2,42,10,50,18,58,26, 33,1,41,9,49,17,57,25
]
E = [
 32,1,2,3,4,5, 4,5,6,7,8,9, 8,9,10,11,12,13,
 12,13,14,15,16,17, 16,17,18,19,20,21, 20,21,22,23,24,25,
 24,25,26,27,28,29, 28,29,30,31,32,1
]
P = [
 16,7,20,21,29,12,28,17, 1,15,23,26,5,18,31,10,
 2,8,24,14,32,27,3,9, 19,13,30,6,22,11,4,25
]
PC1 = [
 57,49,41,33,25,17,9, 1,58,50,42,34,26,18, 10,2,59,51,43,35,27,
 19,11,3,60,52,44,36, 63,55,47,39,31,23,15, 7,62,54,46,38,30,22,
 14,6,61,53,45,37,29, 21,13,5,28,20,12,4
]
PC2 = [
 14,17,11,24,1,5, 3,28,15,6,21,10, 23,19,12,4,26,8,
 16,7,27,20,13,2, 41,52,31,37,47,55, 30,40,51,45,33,48,
 44,49,39,56,34,53, 46,42,50,36,29,32
]
SHIFTS = [1,1,2,2,2,2,2,2, 1,2,2,2,2,2,2,1]

SBOX = [
 [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
  [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
  [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
  [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],

 [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
  [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
  [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
  [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],

 [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
  [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
  [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
  [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],

 [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
  [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
  [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
  [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],

 [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
  [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
  [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
  [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],

 [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
  [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
  [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
  [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],

 [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
  [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
  [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
  [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],

 [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
  [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
  [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
  [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]],
]

def _sbox_subst(b48):
    out = ""
    for i in range(8):
        chunk = b48[6*i:6*i+6]
        row = (ord(chunk[0]) - 48) * 2 + (ord(chunk[5]) - 48)
        col = ((ord(chunk[1])-48)<<3) | ((ord(chunk[2])-48)<<2) | ((ord(chunk[3])-48)<<1) | (ord(chunk[4])-48)
        val = SBOX[i][row][col]
        out += f"{val:04b}"
    return out

def _f(r32, subkey48):
    r_exp = _permute(r32, E)
    mixed = _xor_bits(r_exp, subkey48)
    s_out = _sbox_subst(mixed)
    return _permute(s_out, P)

def _key_schedule_16(key64_bits):
    k56 = _permute(key64_bits, PC1)
    c = k56[:28]; d = k56[28:]
    subkeys = []
    for s in SHIFTS:
        c = _lrot(c, s)
        d = _lrot(d, s)
        subkeys.append(_permute(c + d, PC2))
    return subkeys

def _des_block_encrypt_hex(pt_hex16, key_hex16):
    if len(pt_hex16) != 16 or len(key_hex16) != 16:
        raise ValueError("Plaintext & key harus 16 hex (64 bit)")
    block = _hex2bits(pt_hex16)
    kbits = _hex2bits(key_hex16)
    subkeys = _key_schedule_16(kbits)
    state = _permute(block, IP)
    L = state[:32]; R = state[32:]
    for i in range(16):
        f = _f(R, subkeys[i])
        L, R = R, _xor_bits(L, f)
    preout = R + L
    out_bits = _permute(preout, FP)
    return _bits2hex(out_bits)

def _des_block_decrypt_hex(ct_hex16, key_hex16):
    if len(ct_hex16) != 16 or len(key_hex16) != 16:
        raise ValueError("Ciphertext & key harus 16 hex (64 bit)")
    block = _hex2bits(ct_hex16)
    kbits = _hex2bits(key_hex16)
    subkeys = _key_schedule_16(kbits)[::-1]
    state = _permute(block, IP)
    L = state[:32]; R = state[32:]
    for i in range(16):
        f = _f(R, subkeys[i])
        L, R = R, _xor_bits(L, f)
    preout = R + L
    out_bits = _permute(preout, FP)
    return _bits2hex(out_bits)

def _pkcs5_pad_hex(hexmsg):
    if len(hexmsg) % 2 != 0: raise ValueError("hex message harus genap panjangnya")
    byte_len = len(hexmsg) // 2
    padlen = 8 - (byte_len % 8)
    if padlen == 0: padlen = 8
    pad_byte = f"{padlen:02X}"
    return hexmsg + (pad_byte * padlen)

def _pkcs5_unpad_hex(hexmsg):
    if len(hexmsg) == 0 or len(hexmsg) % 2 != 0:
        raise ValueError("cipher hex tidak valid")
    last_byte = hexmsg[-2:]
    padlen = int(last_byte, 16)
    if padlen < 1 or padlen > 8:
        raise ValueError("padding tidak valid")
    if len(hexmsg) < padlen*2:
        raise ValueError("panjang padding tidak valid")
    if hexmsg[-padlen*2:] != (last_byte * padlen):
        raise ValueError("nilai padding tidak konsisten")
    return hexmsg[:-padlen*2]

def des_ecb_encrypt_hex(message_hex, key_hex16):
    if len(key_hex16) != 16: raise ValueError("key harus 16 hex")
    msg = _pkcs5_pad_hex(message_hex)
    out = ""
    for i in range(0, len(msg), 16):
        blk = msg[i:i+16]
        out += _des_block_encrypt_hex(blk, key_hex16)
    return out

def des_ecb_decrypt_hex(cipher_hex, key_hex16):
    if len(key_hex16) != 16: raise ValueError("key harus 16 hex")
    if len(cipher_hex) % 16 != 0: raise ValueError("cipher hex harus kelipatan 16")
    tmp = ""
    for i in range(0, len(cipher_hex), 16):
        blk = cipher_hex[i:i+16]
        tmp += _des_block_decrypt_hex(blk, key_hex16)
    return _pkcs5_unpad_hex(tmp)

# UTF-8 helpers
def str_to_hex_utf8(s):
    b = s.encode('utf-8')
    h = ""
    for byte in b:
        hx = f"{byte:02X}"
        h += hx
    return h

def hex_utf8_to_str(h):
    if len(h) % 2 != 0:
        raise ValueError("hex tidak valid (panjang ganjil)")
    b_arr = []
    for i in range(0, len(h), 2):
        b_arr.append(int(h[i:i+2], 16))
    return bytes(b_arr).decode('utf-8')

def encrypt_text(text, key_hex16):
    return des_ecb_encrypt_hex(str_to_hex_utf8(text), key_hex16)

def decrypt_text(cipher_hex, key_hex16):
    return hex_utf8_to_str(des_ecb_decrypt_hex(cipher_hex, key_hex16))


# untuk menampilkan proses)
def encrypt_text_with_trace(text, key_hex16):
    """Return (cipher_hex, trace_string)"""
    msg_hex = str_to_hex_utf8(text)
    padded = _pkcs5_pad_hex(msg_hex)
    blocks = [padded[i:i+16] for i in range(0, len(padded), 16)]
    ct_blocks = []
    trace_lines = []
    trace_lines.append("=== ENCRYPT TRACE ===")
    trace_lines.append(f"Plaintext       : {text!r}")
    # show utf-8 bytes
    bs = [f'{b:02X}' for b in text.encode('utf-8')]
    trace_lines.append(f"UTF-8 bytes     : {' '.join(bs)}")
    trace_lines.append(f"Hex before pad  : {msg_hex}")
    padlen = (8 - (len(msg_hex)//2 % 8)) or 8
    trace_lines.append(f"PKCS#5 pad len  : {padlen} byte(s)")
    trace_lines.append(f"Hex after pad   : {padded}")
    for idx, blk in enumerate(blocks, 1):
        ct = _des_block_encrypt_hex(blk, key_hex16)
        ct_blocks.append(ct)
        trace_lines.append(f"Block {idx:02d} PT : {blk}  ->  CT : {ct}")
    cipher_hex = "".join(ct_blocks)
    trace_lines.append(f"Cipher (concat) : {cipher_hex}")
    return cipher_hex, "\n".join(trace_lines)

def decrypt_text_with_trace(cipher_hex, key_hex16):
    """Return (plaintext, trace_string)"""
    if len(cipher_hex) % 16 != 0:
        raise ValueError("cipher hex harus kelipatan 16")
    ct_blocks = [cipher_hex[i:i+16] for i in range(0, len(cipher_hex), 16)]
    pt_blocks = []
    trace_lines = []
    trace_lines.append("=== DECRYPT TRACE ===")
    trace_lines.append(f"Cipher (input)  : {cipher_hex}")
    for idx, blk in enumerate(ct_blocks, 1):
        pt = _des_block_decrypt_hex(blk, key_hex16)
        pt_blocks.append(pt)
        trace_lines.append(f"Block {idx:02d} CT : {blk}  ->  PT : {pt}")
    concat_hex = "".join(pt_blocks)
    trace_lines.append(f"PT hex concat   : {concat_hex}")
    unpadded = _pkcs5_unpad_hex(concat_hex)
    trace_lines.append(f"Unpadded hex    : {unpadded}")
    try:
        plaintext = hex_utf8_to_str(unpadded)
        trace_lines.append(f"Plaintext UTF-8 : {plaintext!r}")
    except Exception as e:
        plaintext = ""
        trace_lines.append(f"[Decode UTF-8 error] {e}")
    return plaintext, "\n".join(trace_lines)
