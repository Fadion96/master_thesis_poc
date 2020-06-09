from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from functools import reduce
import operator

group = PairingGroup("SS512")

def keygen(g):
    sk_p, sk_v = group.random(ZR), group.random(ZR)
    pk_p = g ** sk_p
    pk_v = g ** sk_v
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
            a_i = group.random(ZR)
            a_list.append(a_i)
            r_i = g ** a_i
            r_list.append(r_i)
            h_i = group.hash(f"{msg}{r_i}", ZR)
            h_list.append(h_i)
    a = group.random(ZR)
    print([pks[i] ** (- h_list[i]) for i in range(len(pks)) if i != p_id ])
    r_list[p_id] = (g ** a) * reduce(operator.mul, [pks[i] ** (- h_list[i]) for i in range(len(pks)) if i != p_id ])
    h = group.hash(f"{msg}{r_list[p_id]}", ZR)
    s = reduce(operator.add, [a_list[i] + a + (sk * h) for i in range(len(pks)) if i != p_id])
    r_list[v_id] = pks[v_id] * a_list[v_id]
    g_hat = group.hash(f'{msg}{r_list}{pks}', G2)
    S = g_hat ** s
    return (r_list, S)

def verify(g, msg, pks, sk, p_id, v_id, R, S):
    g_hat = group.hash(f'{msg}{R}{pks}', G2)
    R[v_id] = R[v_id] ** (1/sk)
    h_list = [group.hash(f"{msg}{R[i]}") for i in range(len(pks))]
    prod = reduce(operator.mul, [R[i] * (pks[i] ** h_list[i]) for i in range(len(pks))])
    assert pair(g, S) == pair(prod, g_hat)

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
            a_i = group.random(ZR)
            a_list.append(a_i)
            r_i = g ** a_i
            r_list.append(r_i)
            h_i = group.hash(f"{msg}{r_i}", ZR)
            h_list.append(h_i)
    a = group.random(ZR)
    r = (g ** a) * reduce(operator.mul, [pks[i] ** (-h_list[i])for i in range(len(pks)) if i != v_id ])
    h = group.hash(f"{msg}{r}", ZR)
    s = reduce(operator.add, [a_list[i] + a + (sk * h) for i in range(len(pks)) if i != v_id])
    r_list[v_id] = r ** sk
    g_hat = group.hash(f'{msg}{r_list}{pks}', G2)
    S = g_hat ** s
    return (r_list, S)
 
if __name__ == "__main__":
    msg = "Master Thesis"
    g = group.random(G1)
    sk_p, pk_p, sk_v, pk_v = keygen(g)
    R, s = sign(g, msg, [pk_p, pk_v], sk_p, 0, 1)
    # R, s = sim(g, msg, [pk_p, pk_v], sk_v, 0, 1)
    verify(g, msg, [pk_p, pk_v], sk_v, 0, 1, R, s)
