from mcl import Fr, G1, mcl_init, CurveType
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
    return (r_list, s)

def verify(g, msg, pks, sk, p_id, v_id, R, s):
    R[v_id] = R[v_id] * sk.inv()
    h_list = [Fr.set_hash_of(f"{msg}{R[i].getStr()}") for i in range(len(pks))]
    prod = reduce(operator.add, [R[i] + (pks[i] * h_list[i]) for i in range(len(pks))])
    assert g * s == prod

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
    return (r_list, s)
 
if __name__ == "__main__":
    msg = "Master Thesis"
    g = G1.hashAndMapToG1("DVS")
    sk_p, pk_p, sk_v, pk_v = keygen(g)
    # print(sk_p, pk_p, sk_v, pk_v )
    sk_t, pk_t, sk_z, pk_z = keygen(g)
    # print(sk_t, pk_t, sk_z, pk_z)

    # R, s = sign(g, msg, [pk_p, pk_v], sk_p, 0, 1)
    R, s = sim(g, msg, [pk_p, pk_v], sk_v, 0, 1)
    verify(g, msg, [pk_p, pk_v], sk_v, 0, 1, R, s)
