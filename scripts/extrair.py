"""Extração do texto canônico. Esqueleto da F0; implementação na F1.

Uso previsto:
    python scripts/extrair.py --captura fontes/<dominio>/<id>/capturas/<ts_utc>

Contrato:
  1. Ler os bytes capturados (HTML ou PDF) e produzir texto.md em UTF-8, LF,
     normalização Unicode NFC.
  2. Inserir âncoras estáveis: por dispositivo nas normas (#art-46-iii), com as
     marcas de redação revogada ou alterada preservadas; por parágrafo nos
     demais textos (#p-0042).
  3. Regime trecho: texto.md contém só a passagem relevante, recortada por
     offsets do texto extraído, nunca redigitada.
  4. Devolver o bloco texto_canonico da FICHA: sha256 do texto.md e derivado_de
     com ts_utc, sha256 dos bytes de origem, ferramenta e versão.
"""

import sys

if __name__ == "__main__":
    sys.exit("extrair.py: não implementado (F1)")
