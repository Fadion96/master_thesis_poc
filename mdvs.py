from mcl import Fr, G1, G2, mcl_init, CurveType, pairing
from functools import reduce
import operator

mcl_init(CurveType.MCL_BLS12_381)

def keygen(g):
    sk_p, sk_v = Fr(), Fr()
    sk_p.set_by_CSPRNG()
    sk_v.set_by_CSPRNG()
    pk_p = g * sk_p
    pk_v = g * sk_v
    return sk_p, pk_p, sk_v, pk_v

def sign(g, msg, pks, sk, p_id, v_id):
    a_list = []
    r_list = []
    h_list = []
    for i in range(len(pks)):
        if i == p_id:
            a_list.append(None)
            r_list.append(None)
            h_list.append(None)
        else:
            a_i = Fr()
            a_i.set_by_CSPRNG()
            a_list.append(a_i)
            r_i = g * a_i
            r_list.append(r_i)
            h_i = Fr.set_hash_of(f"{msg}{r_i.getStr()}")
            h_list.append(h_i)
    a = Fr()
    a.set_by_CSPRNG()
    r_list[p_id] = (g * a) + reduce(operator.add, [pks[i] * h_list[i].neg() for i in range(len(pks)) if i != p_id ])
    h = Fr.set_hash_of(f"{msg}{r_list[p_id].getStr()}")
    s = reduce(operator.add, [a_list[i] + a + (sk * h) for i in range(len(pks)) if i != p_id])
    r_list[v_id] = pks[v_id] * a_list[v_id]
    g_hat = G2.hashAndMapToG2(f'{msg}{r_list}{pks}')
    S = g_hat * s
    return (r_list, S)

def verify(g, msg, pks, sk, p_id, v_id, R, S):
    g_hat = G2.hashAndMapToG2(f'{msg}{R}{pks}')
    R[v_id] = R[v_id] * sk.inv()
    h_list = []
    for i in range(len(pks)):
        h_i = Fr.set_hash_of(f"{msg}{R[i].getStr()}")
        h_list.append(h_i)
    prod = R[v_id] + (pks[v_id] * h_list[v_id])
    for i in range(len(pks)):
        if i == v_id:
            continue
        else:
            prod += R[i] + (pks[i] * h_list[i])
    assert pairing(g, S) == pairing(prod, g_hat)

def sim(g, msg, pks, sk, p_id, v_id):
    a_list = []
    r_list = []
    h_list = []
    for i in range(len(pks)):
        if i == v_id:
            a_list.append(None)
            r_list.append(None)
            h_list.append(None)
        else:
            a_i = Fr()
            a_i.set_by_CSPRNG()
            a_list.append(a_i)
            r_i = g * a_i
            r_list.append(r_i)
            h_i = Fr.set_hash_of(f"{msg}{r_i.getStr()}")
            h_list.append(h_i)
    a = Fr()
    a.set_by_CSPRNG()
    r = (g * a) + reduce(operator.add, [pks[i] * h_list[i].neg() for i in range(len(pks)) if i != v_id ])
    h = Fr.set_hash_of(f"{msg}{r.getStr()}")
    s = reduce(operator.add, [a_list[i] + a + (sk * h) for i in range(len(pks)) if i != v_id])
    r_list[v_id] = r * sk
    g_hat = G2.hashAndMapToG2(f'{msg}{r_list}{pks}')
    S = g_hat * s
    return (r_list, S)



if __name__ == "__main__":
    msg = "Master Thesis"
    g = G1.hashAndMapToG1("DVS")
    sk_p, pk_p, sk_v, pk_v = keygen(g)
    # R, s = sign(g, msg, [pk_p, pk_v], sk_p, 0, 1)
    R, s = sim(g, msg, [pk_p, pk_v], sk_v, 0, 1)
    verify(g, msg, [pk_p, pk_v], sk_v, 0, 1, R, s)