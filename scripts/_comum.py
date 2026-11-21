"""Funções comuns aos scripts da biblioteca_mourax."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
DOMINIOS = ("normas", "julgados", "doutrina", "ciencia", "tecnica", "web")


class CarregadorSemDatas(yaml.SafeLoader):
    """SafeLoader sem a conversão implícita de datas.

    O YAML converteria `1998-02-19` num objeto date e `2026-11-21T15:30:00Z`
    num datetime. O esquema exige datas como texto ISO e o catálogo é JSON
    canônico; manter o texto evita que a mesma FICHA produza bytes diferentes
    conforme a versão da biblioteca ou o fuso da máquina.
    """


CarregadorSemDatas.yaml_implicit_resolvers = {
    inicial: [
        (tag, regex)
        for tag, regex in resolvedores
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for inicial, resolvedores in yaml.SafeLoader.yaml_implicit_resolvers.items()
}

# Frontmatter delimitado por linhas "---". O .gitattributes garante LF em
# qualquer clone, por isso a expressão não precisa aceitar CRLF.
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def ler_frontmatter(caminho: Path) -> dict:
    """Lê o frontmatter YAML de uma FICHA.md, sem converter datas."""
    texto = caminho.read_text(encoding="utf-8")
    achado = _FRONTMATTER.match(texto)
    if not achado:
        raise ValueError("frontmatter YAML ausente ou mal delimitado")
    dados = yaml.load(achado.group(1), Loader=CarregadorSemDatas)
    if not isinstance(dados, dict):
        raise ValueError("frontmatter não é um mapeamento")
    return dados


def listar_fichas(raiz: Path = RAIZ) -> list[Path]:
    """FICHAs em fontes/<dominio>/<id>/FICHA.md, em ordem estável."""
    return sorted((raiz / "fontes").glob("*/*/FICHA.md"))


def json_canonico(obj) -> str:
    """JSON determinístico para arquivos gerados.

    Chaves ordenadas, separadores sem espaço e UTF-8 literal. Basta para o
    catálogo. Para o manifesto carimbado da F1, avaliar a RFC 8785 (JCS), que
    fixa também a serialização de números.
    """
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
