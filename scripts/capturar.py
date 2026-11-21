"""Captura das fontes de um pedido aprovado. Esqueleto da F0; implementação na F1.

Uso previsto (só no runner do captura.yml, depois da chave 2):
    python scripts/capturar.py --pedido pedidos/<AAAAMMDDTHHMMSSZ>.json

Contrato, por item do pedido e por URL candidata:
  1. Baixar com wget (--warc-file) ou warcio, preservando requisição, resposta,
     cabeçalhos, status e redirecionamentos em captura.warc.gz (ISO 28500).
  2. Calcular SHA-256 e SHA-512 dos bytes exatos servidos.
  3. Regime integral: gravar original.<ext>. Regime trecho: gravar só os hashes;
     os bytes integrais vão para o cofre privado (F3).
  4. Montar manifesto.json canônico com hashes, URLs, status, content type,
     ferramentas e versões, e o hash do próprio pedido (chave 1 na custódia).
  5. Obter carimbos RFC 3161 sobre o hash do manifesto em duas TSAs, guardando
     .tsq e .tsr verificáveis com `openssl ts -verify`.
  6. Deixar para o workflow a atestação Sigstore (actions/attest) e para a F3 o
     arquivamento pelo Save Page Now 2.
  7. Acionar extrair.py e conferir.py; atualizar FICHA.md; rodar indexar.py;
     acrescentar a linha do REGISTRO.md.

Restrições:
  - Tudo vai para fontes/<dominio>/<id>/capturas/<ts_utc>/, pasta nova a cada
    captura; nada existente é sobrescrito.
  - O log do workflow é público: nunca imprimir conteúdo da fonte.
"""

import sys

if __name__ == "__main__":
    sys.exit("capturar.py: não implementado (F1)")
