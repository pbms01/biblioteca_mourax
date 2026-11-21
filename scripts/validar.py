"""Validação determinística do repositório (check obrigatório do main).

Uso:
    python scripts/validar.py [--base SHA] [--head-ref REF]
    python scripts/validar.py --somente-pedido pedidos/<AAAAMMDDTHHMMSSZ>.json

Sem --base (ou com o SHA nulo do primeiro push), pula as verificações que
comparam com o estado anterior.

Verificações, na ordem:
  1. Esquemas: metaesquema 2020-12; pedidos/*.json; frontmatter das FICHAs.
  2. Caminhos: id e dominio da FICHA conferem com a pasta; id_pedido confere
     com o nome do arquivo; nada solto em fontes/ fora de pasta com FICHA.
  3. Imutabilidade: nada sob fontes/**/capturas/ nem pedidos/*.json que exista
     na base pode ser alterado, apagado ou renomeado; REGISTRO.md só cresce no
     fim e só com linhas no formato do registro.
  4. Branch de pedido: PR vinda de pedido/<ts> só acrescenta o próprio pedido e
     arquivos em fontes/, e só altera FICHA.md, texto.md e os gerados.
  5. Índice: INDICE.md e catalogo.jsonl iguais à saída de indexar.py.
  6. Material de caso (P9): número no padrão CNJ só em item ou FICHA de
     julgado; CPF em lugar nenhum. É rede grossa; o filtro de verdade é o do
     detectar.py, aplicado antes de qualquer pedido.
  7. Estilo: sem travessão (U+2014) nem meia-risca (U+2013) no texto próprio.

Sai com 0 se tudo passar e com 1 se houver erro, listando todos.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jsonschema import Draft202012Validator  # noqa: E402

import indexar  # noqa: E402
from _comum import DOMINIOS, RAIZ, ler_frontmatter, listar_fichas  # noqa: E402

SHA_NULO = "0" * 40

PEDIDO_ARQ = re.compile(r"^pedidos/([0-9]{8}T[0-9]{6}Z)\.json$")
FICHA_OU_TEXTO = re.compile(r"^fontes/[a-z]+/[a-z0-9-]+/(FICHA|texto)\.md$")
LINHA_REGISTRO = re.compile(r"^## \[[0-9]{4}-[0-9]{2}-[0-9]{2}\] captura \| [a-z0-9]+(-[a-z0-9]+)* \| aprovada$")

CNJ = re.compile(r"\b[0-9]{7}-[0-9]{2}\.[0-9]{4}\.[0-9]\.[0-9]{2}\.[0-9]{4}\b")
CPF = re.compile(r"\b[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}\b")

# Por código de ponto, para que este arquivo não contenha o caractere que proíbe.
TRACOS = {chr(0x2014): "travessão (U+2014)", chr(0x2013): "meia-risca (U+2013)"}

# Arquivos gerados carregam títulos de terceiros, que podem conter travessão
# ou número de processo de precedente: ficam fora das verificações de estilo e
# de material de caso, porque já derivam de FICHAs verificadas.
GERADOS = {"INDICE.md", "catalogo.jsonl", "llms.txt"}
EXTENSOES_TEXTO = {".md", ".txt", ".py", ".json", ".jsonl", ".yml", ".yaml", ".toml", ".cfg", ""}


class Relatorio:
    def __init__(self) -> None:
        self.erros: list[str] = []

    def erro(self, mensagem: str) -> None:
        self.erros.append(mensagem)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=RAIZ, check=True, capture_output=True, text=True
    ).stdout


def git_ok(*args: str) -> bool:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True).returncode == 0


def caminhos_proprios() -> list[str]:
    """Arquivos versionados ou novos não ignorados, fora do conteúdo de terceiros."""
    saida = git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    caminhos = sorted({c for c in saida.split("\0") if c})
    return [
        c
        for c in caminhos
        if not c.startswith(("fontes/", "pedidos/"))
        and c not in GERADOS
        and (RAIZ / c).is_file()
    ]


# 1. Esquemas ---------------------------------------------------------------


def carregar_validadores(rel: Relatorio) -> dict[str, Draft202012Validator]:
    validadores = {}
    for nome in ("ficha", "pedido"):
        caminho = f"schema/{nome}.schema.json"
        try:
            esquema = json.loads((RAIZ / caminho).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(esquema)
        except Exception as exc:  # o relatório lista todos os erros
            rel.erro(f"{caminho}: esquema inválido: {exc}")
            continue
        validadores[nome] = Draft202012Validator(
            esquema, format_checker=Draft202012Validator.FORMAT_CHECKER
        )
    return validadores


def aplicar_esquema(rel: Relatorio, validador, dados, onde: str) -> None:
    for falha in sorted(validador.iter_errors(dados), key=lambda f: list(map(str, f.absolute_path))):
        ponto = "/".join(map(str, falha.absolute_path)) or "(raiz)"
        rel.erro(f"{onde}: {ponto}: {falha.message}")


def verificar_pedido(rel: Relatorio, validador, caminho: str) -> dict | None:
    achado = PEDIDO_ARQ.match(caminho)
    if not achado:
        rel.erro(f"{caminho}: nome fora do padrão pedidos/AAAAMMDDTHHMMSSZ.json")
        return None
    try:
        dados = json.loads((RAIZ / caminho).read_text(encoding="utf-8"))
    except Exception as exc:
        rel.erro(f"{caminho}: JSON ilegível: {exc}")
        return None
    if validador is not None:
        aplicar_esquema(rel, validador, dados, caminho)
    if isinstance(dados, dict) and dados.get("id_pedido") != achado.group(1):
        rel.erro(f"{caminho}: id_pedido diferente do nome do arquivo")
    return dados if isinstance(dados, dict) else None


def pedidos_existentes() -> list[str]:
    return sorted(p.relative_to(RAIZ).as_posix() for p in (RAIZ / "pedidos").glob("*.json"))


# 2. Caminhos ----------------------------------------------------------------


def verificar_fichas(rel: Relatorio, validador) -> None:
    for caminho in listar_fichas(RAIZ):
        relativo = caminho.relative_to(RAIZ).as_posix()
        dominio_pasta, id_pasta = caminho.parent.parent.name, caminho.parent.name
        if dominio_pasta not in DOMINIOS:
            rel.erro(f"{relativo}: domínio '{dominio_pasta}' fora da lista {DOMINIOS}")
        try:
            ficha = ler_frontmatter(caminho)
        except Exception as exc:
            rel.erro(f"{relativo}: {exc}")
            continue
        if validador is not None:
            aplicar_esquema(rel, validador, ficha, relativo)
        if ficha.get("id") != id_pasta:
            rel.erro(f"{relativo}: id diferente do nome da pasta")
        if ficha.get("dominio") != dominio_pasta:
            rel.erro(f"{relativo}: dominio diferente da pasta de domínio")

    for item in sorted((RAIZ / "fontes").glob("*/*")):
        if item.is_dir() and not (item / "FICHA.md").is_file():
            rel.erro(f"{item.relative_to(RAIZ).as_posix()}: pasta de fonte sem FICHA.md")
    for item in sorted((RAIZ / "fontes").glob("*")):
        if item.is_file() and item.name != "README.md":
            rel.erro(f"{item.relative_to(RAIZ).as_posix()}: arquivo solto em fontes/")


# 3 e 4. Comparação com a base ------------------------------------------------


def mudancas(base: str) -> list[tuple[str, str]]:
    """(status, caminho) entre a base e HEAD, com renomeação vista como D + A."""
    saida = git("diff", "--name-status", "--no-renames", "-z", base, "HEAD")
    partes = [p for p in saida.split("\0") if p]
    return [(partes[i][0], partes[i + 1]) for i in range(0, len(partes) - 1, 2)]


def protegido(caminho: str) -> bool:
    if caminho.startswith("fontes/") and "/capturas/" in caminho:
        return True
    return caminho.startswith("pedidos/") and caminho.endswith(".json")


def verificar_imutabilidade(rel: Relatorio, base: str, lista: list[tuple[str, str]]) -> None:
    for status, caminho in lista:
        if status != "A" and protegido(caminho):
            rel.erro(f"{caminho}: arquivo append-only alterado ou removido (status {status})")

    if not git_ok("cat-file", "-e", f"{base}:REGISTRO.md"):
        return
    anterior = git("show", f"{base}:REGISTRO.md")
    atual = (RAIZ / "REGISTRO.md").read_text(encoding="utf-8") if (RAIZ / "REGISTRO.md").exists() else ""
    if not atual.startswith(anterior):
        rel.erro("REGISTRO.md: conteúdo anterior alterado; o registro só cresce no fim")
        return
    for numero, linha in enumerate(atual[len(anterior):].splitlines(), start=anterior.count("\n") + 1):
        if linha.strip() and not LINHA_REGISTRO.match(linha):
            rel.erro(f"REGISTRO.md:{numero}: linha fora do formato '## [AAAA-MM-DD] captura | <id> | aprovada'")


def verificar_branch_pedido(rel: Relatorio, head_ref: str, lista: list[tuple[str, str]]) -> None:
    if not head_ref.startswith("pedido/"):
        return
    esperado = f"pedidos/{head_ref[len('pedido/'):]}.json"
    if not PEDIDO_ARQ.match(esperado):
        rel.erro(f"branch {head_ref}: nome fora do padrão pedido/AAAAMMDDTHHMMSSZ")
    if ("A", esperado) not in lista:
        rel.erro(f"branch {head_ref}: não acrescenta {esperado}")
    for status, caminho in lista:
        if status == "A" and (caminho == esperado or caminho.startswith("fontes/")):
            continue
        if status == "M" and (caminho in GERADOS or caminho == "REGISTRO.md" or FICHA_OU_TEXTO.match(caminho)):
            continue
        rel.erro(f"branch {head_ref}: mudança não permitida numa branch de pedido: {status} {caminho}")


# 5. Índice -------------------------------------------------------------------


def verificar_indice(rel: Relatorio) -> None:
    try:
        catalogo, indice = indexar.gerar(RAIZ)
    except Exception as exc:
        rel.erro(f"indexar.py falhou: {exc}")
        return
    for nome, esperado in (("catalogo.jsonl", catalogo), ("INDICE.md", indice)):
        caminho = RAIZ / nome
        atual = caminho.read_text(encoding="utf-8") if caminho.exists() else None
        if atual != esperado:
            rel.erro(f"{nome}: fora de sincronia com as FICHAs; rode scripts/indexar.py")


# 6. Material de caso -----------------------------------------------------------
# As mensagens indicam só arquivo e posição, nunca o número encontrado: o log do
# workflow é público e repetir o dado ali seria o próprio vazamento.


def _sem_material(rel: Relatorio, texto: str, onde: str, tolera_cnj: bool) -> None:
    if CPF.search(texto):
        rel.erro(f"{onde}: contém número no formato de CPF")
    if not tolera_cnj and CNJ.search(texto):
        rel.erro(f"{onde}: contém número de processo no padrão CNJ fora de fonte do domínio julgados")


def verificar_material_caso_pedido(rel: Relatorio, caminho: str, dados: dict) -> None:
    resto = {k: v for k, v in dados.items() if k != "itens"}
    _sem_material(rel, json.dumps(resto, ensure_ascii=False), f"{caminho} (cabeçalho)", tolera_cnj=False)
    for posicao, item in enumerate(dados.get("itens") or [], start=1):
        dominio = ((item or {}).get("obra") or {}).get("dominio")
        _sem_material(
            rel,
            json.dumps(item, ensure_ascii=False),
            f"{caminho} (item {posicao})",
            tolera_cnj=dominio == "julgados",
        )


def verificar_material_caso(rel: Relatorio, pedidos: dict[str, dict]) -> None:
    for caminho, dados in pedidos.items():
        verificar_material_caso_pedido(rel, caminho, dados)
    for caminho in listar_fichas(RAIZ):
        relativo = caminho.relative_to(RAIZ).as_posix()
        _sem_material(
            rel,
            caminho.read_text(encoding="utf-8"),
            relativo,
            tolera_cnj=caminho.parent.parent.name == "julgados",
        )
    for caminho in caminhos_proprios():
        if Path(caminho).suffix in EXTENSOES_TEXTO:
            try:
                texto = (RAIZ / caminho).read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            _sem_material(rel, texto, caminho, tolera_cnj=False)


# 7. Estilo ---------------------------------------------------------------------


def verificar_estilo(rel: Relatorio) -> None:
    for caminho in caminhos_proprios():
        if Path(caminho).suffix not in EXTENSOES_TEXTO:
            continue
        try:
            linhas = (RAIZ / caminho).read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            rel.erro(f"{caminho}: texto próprio fora de UTF-8")
            continue
        for numero, linha in enumerate(linhas, start=1):
            for caractere, nome in TRACOS.items():
                if caractere in linha:
                    rel.erro(f"{caminho}:{numero}: {nome}")


# Execução ----------------------------------------------------------------------


def resolver_base(base: str | None, head_ref: str, rel: Relatorio) -> str | None:
    if not base or base == SHA_NULO:
        return None
    # Numa PR, o checkout é o commit de merge de teste; o primeiro pai é a ponta
    # do main contra a qual o merge foi montado, base mais fiel que o
    # pull_request.base.sha do evento, que pode estar defasado.
    if head_ref and git_ok("rev-parse", "--verify", "-q", "HEAD^2"):
        return git("rev-parse", "HEAD^1").strip()
    if not git_ok("cat-file", "-e", f"{base}^{{commit}}"):
        rel.erro(f"commit de base {base} indisponível no clone (checkout com fetch-depth 0?)")
        return None
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="", help="SHA do estado anterior")
    parser.add_argument("--head-ref", default="", help="branch de origem da PR")
    parser.add_argument("--somente-pedido", default="", help="valida só este pedido")
    args = parser.parse_args()

    rel = Relatorio()
    validadores = carregar_validadores(rel)

    if args.somente_pedido:
        dados = verificar_pedido(rel, validadores.get("pedido"), args.somente_pedido)
        if dados is not None:
            verificar_material_caso_pedido(rel, args.somente_pedido, dados)
    else:
        pedidos = {}
        for caminho in pedidos_existentes():
            dados = verificar_pedido(rel, validadores.get("pedido"), caminho)
            if dados is not None:
                pedidos[caminho] = dados
        verificar_fichas(rel, validadores.get("ficha"))

        base = resolver_base(args.base, args.head_ref, rel)
        if base is not None:
            lista = mudancas(base)
            verificar_imutabilidade(rel, base, lista)
            verificar_branch_pedido(rel, args.head_ref, lista)

        verificar_indice(rel)
        verificar_material_caso(rel, pedidos)
        verificar_estilo(rel)

    for mensagem in rel.erros:
        print(f"ERRO {mensagem}")
    if rel.erros:
        print(f"validar: {len(rel.erros)} erro(s)")
        return 1
    print("validar: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
