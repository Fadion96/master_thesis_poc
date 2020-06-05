#include <iostream>
#include <mcl/bls12_381.hpp>
#include <vector>
#include <tuple>
#include <cassert>

using namespace mcl::bn;
using namespace std;

tuple<Fr, Fr, G1, G1> keyGen(G1 g) {
    Fr sk_p, sk_v;
    sk_p.setByCSPRNG();
    sk_v.setByCSPRNG();
    Fr neg_skp;
    G1 pk_p, pk_v;
    pk_p = g * sk_p;
    pk_v = g * sk_v;
    return {sk_p, sk_v, pk_p, pk_v};
}

tuple<vector<G1>, Fr> sign(G1 g, string msg, vector<G1> public_keys, 
                            Fr sk, int p_id, int v_id){                                
    vector<Fr> a_list;
    vector<G1> r_list;
    vector<Fr> h_list;
    int counter = 0;
    for (auto pk: public_keys){
        if (counter == p_id){
            a_list.push_back(Fr(0));
            r_list.push_back(g);
            h_list.push_back(Fr(0));
            counter++;
        }
        else{
            Fr a_i;
            a_i.setByCSPRNG();
            a_list.push_back(a_i);
            G1 r_i = g * a_i;
            r_list.push_back(r_i);
            Fr h_i;
            h_i.setHashOf(msg + r_i.getStr());
            h_list.push_back(h_i);
        }
    }
    Fr a;
    a.setByCSPRNG();
    G1 r = g * a;
    for (int i=0; i < public_keys.size(); i++){
        if (i == p_id){
            continue;
        }
        else {
            Fr neg_h;
            Fr::neg(neg_h, h_list[i]);
            r += public_keys[i] *  neg_h;
        }
    }
    Fr h;
    h.setHashOf(msg + r.getStr());
    Fr s = 0;
     for (int i=0; i < public_keys.size(); i++){
        if (i == p_id){
            continue;
        }
        else {
            s += a_list[i] + a + ( sk * h);
        }
    }
    G1 r_v = public_keys[v_id] * a_list[v_id];
    r_list[v_id] = r_v;
    r_list[p_id] = r;
    return {r_list, s};
}

void verify (G1 g, string msg, vector<G1> public_keys, 
                Fr sk, int p_id, int v_id, vector<G1> R, Fr s){
    Fr sk_inv;
    Fr::inv(sk_inv, sk);
    G1 r_v = R[v_id] * sk_inv;
    R[v_id] = r_v;    vector<Fr> h_list;
    for (int i=0; i < public_keys.size(); i++){
        Fr h;
        h.setHashOf(msg + (R[i]).getStr());  
        h_list.push_back(h);
    }
    G1 prod = R[v_id] + (public_keys[v_id] * h_list[v_id]);
    for (int i=0; i < public_keys.size(); i++){
        if (i == v_id){
            continue;
        }
        else {
            prod += R[i] + (public_keys[i] * h_list[i]);
        }
    }
    assert (g * s == prod);
}

int main(){
	initPairing(mcl::BLS12_381);
    G1 g;
    string msg = "Master Thesis";
    hashAndMapToG1(g, "DVS");
    auto [sk_p, sk_v, pk_p, pk_v] = keyGen(g);
    vector<G1> public_keys = {pk_p, pk_v};
    auto [R, s] = sign(g, msg, public_keys, sk_p, 0, 1);
    verify(g, msg, public_keys, sk_v, 0, 1, R, s);
}

