"""Verificação periódica de fixidez. Esqueleto da F0; implementação na F3.

Uso previsto (fixidez.yml, mensal):
    python scripts/fixidez.py

Contrato:
  1. Recalcular SHA-256 e SHA-512 de todos os bytes em fontes/**/capturas/ e
     comparar com os manifestos.
  2. Verificar os .tsr de cada manifesto com `openssl ts -verify`.
  3. Repetir a conferência no cofre privado, pela deploy key.
  4. Abrir issue para qualquer divergência, sem imprimir conteúdo.
"""

import sys

if __name__ == "__main__":
    sys.exit("fixidez.py: não implementado (F3)")
