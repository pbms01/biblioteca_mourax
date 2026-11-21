"""Detector determinístico de referências a fontes. Esqueleto da F0; F2.

Uso previsto:
    python scripts/detectar.py --entrada <exportacao ou transcrição> --saida <ocorrencias.jsonl>

Roda fora do repositório, na área privada: a entrada são conversas.

Contrato:
  1. Registrar ocorrências de URL, DOI, arXiv, ISBN, padrões normativos (lei,
     lei complementar, decreto, medida provisória, Constituição, artigo com
     diploma, súmula, súmula vinculante, tema), padrões de julgados (REsp, RE,
     HC, RHC, ADI, ADPF, AgRg e equivalentes), citações entre aspas ou em bloco
     próximas de atribuição e padrões autor-ano.
  2. Para cada ocorrência: conversa, mensagem, autoria (usuário, assistente ou
     anexo), janela de contexto e o trecho literal exato da entrada.
  3. Filtro de sigilo (P9), antes de qualquer LLM e de qualquer saída: descartar
     números de processos concretos (salvo precedente publicado invocado como
     autoridade), conteúdo de anexos de autos, nomes de partes e dados pessoais.
"""

import sys

if __name__ == "__main__":
    sys.exit("detectar.py: não implementado (F2)")
