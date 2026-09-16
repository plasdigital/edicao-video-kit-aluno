#!/usr/bin/env python3
"""
Acha os marcadores falados na transcricao e agrupa marcadores proximos em clusters.
Cada cluster = um corte. Pra cada cluster mostra o texto ao redor e as duas
fronteiras candidatas: a ultima palavra boa ANTES e a primeira palavra boa DEPOIS.

Por que fuzzy: TODO ASR erra o marcador. "jacare amarelo" ja saiu como "jacare
amarel", "jacare amarelu", "jacareamarelo". Match exato perde marcador, e marcador
perdido = erro que vaza pro video final. Entao o matcher e tolerante de proposito,
e ainda lista SUSPEITAS (match parcial) pra revisao humana.

Uso:
  achar-marcadores.py <transcript-flat.txt> [--config config.json] [--fps 30]
  achar-marcadores.py <flat.txt> --marcadores "jacare amarelo:curto,jacare vermelho:longo"

  flat format: indice|start|end|texto   (1 palavra por linha, gerado pelo transcrever.py)
  start/end sao inteiros na unidade da fonte (frames se --fps, senao ms).

Saida: clusters com contexto + fronteiras candidatas, e uma lista de suspeitas.
Quem decide o corte final e o agente lendo o contexto, nao esse script.
"""
import argparse, json, re, sys, unicodedata
from difflib import SequenceMatcher

# Similaridade minima por palavra, POR COMPRIMENTO. Um limiar fixo nao funciona:
# numa palavra de 4 letras, trocar 1 letra ja da ~0.75 e vira colisao com palavra
# comum ("code" vs "pode" = 0.750, "lote" vs "note" = 0.750). Numa de 6+, o mesmo
# 0.75 rejeita erro REAL de ASR ("claude" vs "cloud" = 0.727).
# Entao: palavra curta exige quase exato, palavra longa pode relaxar.
RATIO_POR_TAMANHO = ((4, 0.85), (5, 0.78))  # (ate N letras, ratio minimo)
RATIO_LONGA = 0.70                          # 6+ letras
GAP_CLUSTER = 12   # marcadores a <= N palavras viram o mesmo cluster (mesma tropecada)
CTX_ANTES, CTX_DEPOIS = 30, 35

# Por que 12 e nao mais: o cluster vira UM corte, de antes do 1o marcador ate depois
# do ultimo. Se dois marcadores independentes cairem no mesmo cluster, a retomada BOA
# entre eles e deletada junto. 12 palavras ~= tu tropecar duas vezes na mesma frase.
# Marcadores mais distantes que isso sao incidentes separados = cortes separados.


def norm(s):
    """lowercase + sem acento + so letras/numeros. 'Amarelo,' -> 'amarelo'"""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def ratio_min(n):
    for ate, r in RATIO_POR_TAMANHO:
        if n <= ate:
            return r
    return RATIO_LONGA


def parecido(a, b):
    """Uma palavra do marcador bate com uma palavra da transcricao?"""
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b:
        return True
    # prefixo: 'amarelo' vs 'amarel' (ASR corta o fim). So pra palavra longa:
    # em palavra curta o prefixo pega meio dicionario.
    curto, longo = (a, b) if len(a) <= len(b) else (b, a)
    if len(curto) >= 5 and longo.startswith(curto):
        return True
    return SequenceMatcher(None, a, b).ratio() >= ratio_min(max(len(a), len(b)))


def casa_frase(words, i, frase_words):
    """A frase do marcador comeca na palavra i? Retorna o indice final ou None."""
    j = i
    for fw in frase_words:
        if j >= len(words) or not parecido(fw, words[j][3]):
            return None
        j += 1
    return j - 1


def tc(v, fps=0, unit="s"):
    """valor na unidade do flat -> timecode legivel. O flat daqui sai em segundos."""
    if unit == "frames":
        seg = v / (fps or 30.0)
    elif unit == "ms":
        seg = v / 1000.0
    else:
        seg = v
    return f"{int(seg // 60)}:{seg % 60:05.2f}"


def num(v):
    """frame/ms saem int; segundos ficam float. Nao devolve 342.0 pra quem espera 342."""
    return int(v) if float(v).is_integer() else v


def carrega_marcadores(args):
    if args.marcadores:
        out = []
        for item in args.marcadores.split(","):
            frase, _, rb = item.partition(":")
            out.append({"frase": frase.strip(), "rollback": (rb.strip() or "curto")})
        return out
    try:
        with open(args.config) as f:
            cfg = json.load(f)
        return cfg["marcadores"]
    except FileNotFoundError:
        sys.exit(f"erro: nao achei {args.config}. Roda o setup da skill ou passa --marcadores.")
    except KeyError:
        sys.exit(f"erro: {args.config} nao tem a chave 'marcadores'.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("flat")
    p.add_argument("--config", default="config.json")
    p.add_argument("--marcadores", help='ex: "jacare amarelo:curto,jacare vermelho:longo"')
    p.add_argument("--fps", type=float, default=0, help="fps se o flat estiver em frames; omite se estiver em ms")
    p.add_argument("--unit", choices=["s", "ms", "frames"], default="s",
                   help="unidade do flat (o transcrever.py daqui sai em segundos)")
    p.add_argument("--gap", type=int, default=GAP_CLUSTER,
                   help=f"marcadores a <= N palavras viram 1 cluster = 1 corte (default {GAP_CLUSTER})")
    args = p.parse_args()

    marcadores = carrega_marcadores(args)

    # start/end podem vir int (frames, ms) ou float (segundos, --unit s do transcrever.py).
    # float() aceita os dois; so int() rebentava com "invalid literal ... '0.0'".
    words = []
    for ln, l in enumerate(open(args.flat), 1):
        l = l.rstrip("\n")
        if not l:
            continue
        try:
            i, s, e, t = l.split("|", 3)
            words.append((int(i), float(s), float(e), t))
        except ValueError:
            sys.exit(f"erro: {args.flat} linha {ln} malformada: {l!r}\n"
                     f"  esperado: indice|start|end|texto (start/end numericos)\n"
                     f"  gera com: transcrever.py <video> -o {args.flat}")
    n = len(words)
    if not n:
        sys.exit("erro: transcript flat vazio.")

    # acha as ocorrencias completas
    marker_pos, hits = set(), []
    for m in marcadores:
        fw = m["frase"].split()
        for i in range(n):
            fim = casa_frase(words, i, fw)
            if fim is not None:
                for k in range(i, fim + 1):
                    marker_pos.add(k)
                hits.append({"ini": i, "fim": fim, "rollback": m["rollback"], "frase": m["frase"]})
    hits.sort(key=lambda h: h["ini"])

    # remove sobreposicoes (frases que se contem, ex: dois marcadores com a mesma 1a palavra)
    limpos = []
    for h in hits:
        if limpos and h["ini"] <= limpos[-1]["fim"]:
            if (h["fim"] - h["ini"]) > (limpos[-1]["fim"] - limpos[-1]["ini"]):
                limpos[-1] = h
            continue
        limpos.append(h)
    hits = limpos

    # clusteriza
    clusters = []
    for h in hits:
        if clusters and h["ini"] - clusters[-1]["last"] <= args.gap:
            clusters[-1]["hits"].append(h)
            clusters[-1]["last"] = h["fim"]
        else:
            clusters.append({"hits": [h], "first": h["ini"], "last": h["fim"]})

    for ci, cl in enumerate(clusters, 1):
        first, last = cl["hits"][0]["ini"], cl["hits"][-1]["fim"]
        rbs = "+".join(h["rollback"].upper() for h in cl["hits"])
        pior = "longo" if any(h["rollback"] == "longo" for h in cl["hits"]) else "curto"
        print("=" * 90)
        print(f"CLUSTER {ci} | {len(cl['hits'])}x: {rbs} | rollback do cluster: {pior.upper()}")
        # o cluster vira 1 corte so: tudo entre o 1o e o ultimo marcador SAI.
        # se tem fala no meio, avisa, porque pode ser retomada boa sendo engolida.
        if len(cl["hits"]) > 1:
            for a, b in zip(cl["hits"], cl["hits"][1:]):
                meio = [words[k][3] for k in range(a["fim"] + 1, b["ini"])]
                if meio:
                    print(f"  ATENCAO: {len(meio)} palavras entre marcadores VAO SAIR nesse corte: "
                          f"\"{' '.join(meio)}\"")
                    print("           se isso e retomada boa, separa em dois cortes (--gap menor).")
        if first > 0:
            w = words[first - 1]
            print(f"  ANTES  (corte COMECA no FIM dessa): idx{w[0]} '{w[3]}' fim@{w[2]} [{tc(w[2], args.fps, args.unit)}]")
        else:
            print("  ANTES  : cluster no inicio do video, corte comeca em 0")
        if last + 1 < n:
            w = words[last + 1]
            print(f"  DEPOIS (corte TERMINA no INICIO dessa): idx{w[0]} '{w[3]}' inicio@{w[1]} [{tc(w[1], args.fps, args.unit)}]")
        else:
            print("  DEPOIS : cluster no fim do video")
        lo, hi = max(0, first - CTX_ANTES), min(n, last + CTX_DEPOIS)
        buf = [f"<<{words[k][3]}@{words[k][1]}>>" if k in marker_pos else f"{words[k][3]}@{words[k][1]}"
               for k in range(lo, hi)]
        print("  TEXTO: " + " ".join(buf))
        print()

    # suspeitas: palavra parecida com alguma palavra de marcador que NAO virou match completo
    vocab = {w for m in marcadores for w in m["frase"].split()}
    suspeitas = []
    for k, w in enumerate(words):
        if k in marker_pos:
            continue
        if any(parecido(v, w[3]) for v in vocab):
            suspeitas.append(w)
    if suspeitas:
        print("=" * 90)
        print(f"SUSPEITAS ({len(suspeitas)}): palavra parecida com marcador que NAO fechou frase completa.")
        print("Pode ser ASR quebrado (marcador de verdade) ou tu falando a palavra no conteudo. Revisa:")
        for w in suspeitas[:40]:
            print(f"  idx{w[0]} '{w[3]}' @{w[1]} [{tc(w[1], args.fps, args.unit)}]")
        if len(suspeitas) > 40:
            print(f"  ... e mais {len(suspeitas) - 40}")
        print()

    print(f"{len(hits)} marcadores, {len(clusters)} clusters, {len(suspeitas)} suspeitas")
    print(json.dumps([{"cluster": i,
                       "rollback": "longo" if any(h["rollback"] == "longo" for h in c["hits"]) else "curto",
                       "antes_fim": num(words[c["hits"][0]["ini"] - 1][2]) if c["hits"][0]["ini"] > 0 else 0,
                       "depois_inicio": num(words[c["hits"][-1]["fim"] + 1][1]) if c["hits"][-1]["fim"] + 1 < n else None}
                      for i, c in enumerate(clusters, 1)]))


if __name__ == "__main__":
    main()
