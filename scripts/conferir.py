"""Conferência dos trechos do pedido contra o texto canônico. Esqueleto da F0.

Uso previsto:
    python scripts/conferir.py --pedido pedidos/<ts>.json --fonte fontes/<dominio>/<id>

Contrato, conforme a tipologia da referência (P8):
  - citacao_literal: casamento determinístico de string depois de normalização
    (NFC, espaços, aspas tipográficas). Resultado: exata,
    exata_apos_normalizacao, divergente (com diff) ou nao_localizada.
  - parafrase e alusao: registrar a passagem candidata por offsets e marcar
    pendente_confirmacao.
  - mencao: conferir título, autoria, data, número e versão contra os
    metadados do original.
  - dispositivo: localizar a âncora estrutural e verificar se a redação está
    vigente, revogada ou alterada.

Grava conferencia.json na pasta da captura. Divergência é resultado, não erro.
"""

import sys

if __name__ == "__main__":
    sys.exit("conferir.py: não implementado (F2)")
