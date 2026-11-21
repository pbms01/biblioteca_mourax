"""Gera INDICE.md e catalogo.jsonl a partir das FICHAs.

Uso:
    python scripts/indexar.py               grava os dois arquivos
    python scripts/indexar.py --verificar   só compara; sai com 1 se divergirem

A saída não traz data de geração e não depende da ordem do sistema de
arquivos: é função pura das FICHAs. Por isso o validar.yml pode exigir
sincronia byte a byte e reprovar edição manual dos arquivos gerados.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _comum import DOMINIOS, RAIZ, json_canonico, ler_frontmatter, listar_fichas  # noqa: E402

ROTULOS = {
    "normas": "Normas",
    "julgados": "Julgados",
    "doutrina": "Doutrina",
    "ciencia": "Ciência",
    "tecnica": "Técnica",
    "web": "Web",
}

CAMPOS_CATALOGO = (
    "id",
    "dominio",
    "tipo",
    "titulo",
    "autoria",
    "data_publicacao",
    "versao",
    "urn",
    "doi",
    "arxiv",
    "grau_fonte",
    "regime_armazenamento",
    "status_verificacao",
)


def _ordem(entrada: dict) -> tuple:
    dominio = entrada.get("dominio")
    posicao = DOMINIOS.index(dominio) if dominio in DOMINIOS else len(DOMINIOS)
    return (posicao, entrada.get("id", ""))


def entradas(raiz: Path = RAIZ) -> list[dict]:
    """Uma entrada de catálogo por FICHA, com a captura mais recente."""
    saida = []
    for caminho in listar_fichas(raiz):
        ficha = ler_frontmatter(caminho)
        entrada = {campo: ficha[campo] for campo in CAMPOS_CATALOGO if campo in ficha}
        capturas = sorted(ficha.get("capturas") or [], key=lambda c: c.get("ts_utc", ""))
        if capturas:
            ultima = capturas[-1]
            entrada["ultima_captura"] = {
                "ts_utc": ultima.get("ts_utc"),
                "sha256": ultima.get("sha256"),
            }
        entrada["caminho"] = caminho.parent.relative_to(raiz).as_posix()
        saida.append(entrada)
    saida.sort(key=_ordem)
    return saida


def _escapar(texto: str) -> str:
    return texto.replace("[", "\\[").replace("]", "\\]")


def gerar(raiz: Path = RAIZ) -> tuple[str, str]:
    """Devolve (conteúdo do catalogo.jsonl, conteúdo do INDICE.md)."""
    lista = entradas(raiz)
    catalogo = "".join(json_canonico(e) + "\n" for e in lista)

    linhas = [
        "# Índice",
        "",
        "Gerado por `scripts/indexar.py` a partir das FICHAs. Não editar à mão.",
        "",
        f"Fontes registradas: {len(lista)}.",
    ]
    if not lista:
        linhas += ["", "Nenhuma fonte registrada ainda."]
    for dominio in DOMINIOS:
        do_dominio = [e for e in lista if e.get("dominio") == dominio]
        if not do_dominio:
            continue
        linhas += ["", f"## {ROTULOS[dominio]}", ""]
        for e in do_dominio:
            captura = (e.get("ultima_captura") or {}).get("ts_utc", "sem captura")
            linhas.append(
                f"- [{_escapar(str(e.get('titulo', e.get('id'))))}]({e['caminho']}/FICHA.md)"
                f" · `{e.get('id')}` · grau {e.get('grau_fonte')}"
                f" · {e.get('regime_armazenamento')} · {e.get('status_verificacao')}"
                f" · captura {captura}"
            )
    indice = "\n".join(linhas) + "\n"
    return catalogo, indice


def _ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def _gravar(caminho: Path, conteudo: str) -> None:
    with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(conteudo)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verificar", action="store_true", help="só compara, sem gravar")
    args = parser.parse_args()

    catalogo, indice = gerar(RAIZ)
    alvos = {RAIZ / "catalogo.jsonl": catalogo, RAIZ / "INDICE.md": indice}

    if args.verificar:
        divergentes = [c.name for c, conteudo in alvos.items() if _ler(c) != conteudo]
        for nome in divergentes:
            print(f"{nome}: fora de sincronia com as FICHAs; rode scripts/indexar.py")
        return 1 if divergentes else 0

    for caminho, conteudo in alvos.items():
        _gravar(caminho, conteudo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
