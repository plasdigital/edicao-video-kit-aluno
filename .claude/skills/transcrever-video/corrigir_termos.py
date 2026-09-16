#!/usr/bin/env python3
"""Corrige nomes de ferramenta que o Whisper escreve do jeito que ouviu.

Uso:
    python corrigir_termos.py transcricao/            # só relata (padrão)
    python corrigir_termos.py transcricao/ --aplicar  # grava

Corrige transcricao.md (só o corpo, depois do ---) e flat.txt. No flat, quando a
correção junta ou separa palavras, a palavra nova fica com o início da primeira e o
fim da última — o tempo continua valendo para legenda e corte.

Regras, na ordem:
  1. docs/glossario.md da pasta do aluno (tabela: tipo | escrito errado | certo)
  2. glossario-video.tsv e glossario-ferramentas.tsv, ao lado deste script
  tipo "troca" aplica; tipo "aviso" só mostra o trecho — quem decide é a pessoa.
"""
import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
CAIXA_FIXA = {"n8n"}


def carrega_regras(raiz):
    regras = []
    glossario = raiz / "docs" / "glossario.md"
    if glossario.exists():
        for linha in glossario.read_text(encoding="utf-8").splitlines():
            cols = [c.strip() for c in linha.strip().strip("|").split("|")]
            if len(cols) != 3 or cols[0].lower() not in ("troca", "aviso") or not cols[1]:
                continue
            errado = cols[1].strip("`")
            regras.append((cols[0].lower(), r"\b" + re.escape(errado) + r"\b", cols[2].strip("`")))
    for tsv in ("glossario-video.tsv", "glossario-ferramentas.tsv"):
        arq = AQUI / tsv
        if not arq.exists():
            continue
        for linha in arq.read_text(encoding="utf-8").splitlines():
            partes = linha.split("\t")
            if len(partes) == 3 and partes[0] in ("troca", "aviso"):
                regras.append(tuple(partes))
    return regras


def caixa(achado, novo):
    if novo in CAIXA_FIXA:
        return novo
    if achado[:1].isupper() and not novo[:1].isupper():
        return novo[:1].upper() + novo[1:]
    return novo


def corrige_texto(texto, regras, trocas):
    for tipo, padrao, certo in regras:
        if tipo != "troca":
            continue

        def sub(m):
            final = caixa(m.group(0), certo)
            if final != m.group(0):
                trocas[(m.group(0), final)] = trocas.get((m.group(0), final), 0) + 1
            return final
        texto = re.sub(padrao, sub, texto, flags=re.IGNORECASE)
    return texto


def avisos(texto, regras):
    saida = []
    for tipo, padrao, palpite in regras:
        if tipo != "aviso":
            continue
        for m in re.finditer(padrao, texto, flags=re.IGNORECASE):
            trecho = texto[max(0, m.start() - 45):m.end() + 45].replace("\n", " ")
            saida.append((m.group(0), palpite, trecho))
    return saida


def corrige_flat(linhas, regras, trocas):
    """linhas: [(inicio, fim, texto)]. Aplica cada troca no texto corrido."""
    for tipo, padrao, certo in regras:
        if tipo != "troca":
            continue
        while True:
            corrido, posicoes, cursor = [], [], 0
            for _, _, t in linhas:
                posicoes.append((cursor, cursor + len(t)))
                corrido.append(t)
                cursor += len(t) + 1
            texto = " ".join(corrido)
            alvo = None
            for m in re.finditer(padrao, texto, flags=re.IGNORECASE):
                if caixa(m.group(0), certo) != m.group(0):
                    alvo = m
                    break
            if alvo is None:
                break
            idx = [i for i, (a, b) in enumerate(posicoes) if a < alvo.end() and b > alvo.start()]
            a, b = idx[0], idx[-1]
            final = caixa(alvo.group(0), certo)
            antes = linhas[a][2][:alvo.start() - posicoes[a][0]]
            depois = linhas[b][2][alvo.end() - posicoes[b][0]:]
            trocas[(alvo.group(0), final)] = trocas.get((alvo.group(0), final), 0) + 1
            linhas[a:b + 1] = [(linhas[a][0], linhas[b][1], antes + final + depois)]
    return linhas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvo", help="pasta da transcrição (ou um arquivo .md/.txt)")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--raiz", default=".", help="pasta do kit, onde fica docs/glossario.md")
    args = ap.parse_args()

    regras = carrega_regras(Path(args.raiz))
    alvo = Path(args.alvo)
    arquivos = [alvo] if alvo.is_file() else [p for p in (alvo / "transcricao.md", alvo / "flat.txt") if p.exists()]
    if not arquivos:
        sys.exit("Nada para corrigir: rode a transcrição antes.")

    print(f"Correção de termos — {'APLICANDO' if args.aplicar else 'só relatando (nada gravado)'}")
    total = 0
    for arq in arquivos:
        conteudo = arq.read_text(encoding="utf-8")
        trocas = {}
        if arq.suffix == ".txt":
            linhas = []
            for l in conteudo.splitlines():
                partes = l.split("|", 3)
                if len(partes) == 4:
                    linhas.append((partes[1], partes[2], partes[3]))
            linhas = corrige_flat(linhas, regras, trocas)
            novo = "".join(f"{i}|{a}|{b}|{t}\n" for i, (a, b, t) in enumerate(linhas, 1))
            achados = avisos(" ".join(t for _, _, t in linhas), regras)
        else:
            marca = "\n---\n"
            cab, corpo = conteudo.split(marca, 1) if marca in conteudo else ("", conteudo)
            cab = cab + marca if cab else ""
            corpo = corrige_texto(corpo, regras, trocas)
            novo = cab + corpo
            achados = avisos(corpo, regras)

        print(f"\n  {arq.name}")
        for (errado, certo), n in sorted(trocas.items(), key=lambda x: -x[1]):
            print(f"    {errado} -> {certo}  ({n}x)")
        for errado, palpite, trecho in achados:
            print(f"    ? {errado} -> talvez {palpite}\n        ...{trecho}...")
        if not trocas and not achados:
            print("    nada a corrigir")
        if args.aplicar and trocas:
            arq.write_text(novo, encoding="utf-8")
        total += sum(trocas.values())

    print(f"\n{total} correção(ões) {'aplicadas' if args.aplicar else 'propostas'}.")
    if total and not args.aplicar:
        print("Mostre a lista e, com o OK, rode de novo com --aplicar.")


if __name__ == "__main__":
    main()
