# AGENTS.md · biblioteca_mourax

Instruções para qualquer agente que leia ou altere este repositório (Claude Code, Codex e outros). O `CLAUDE.md` importa este arquivo.

## Propósito

Acervo de fontes de conhecimento citadas em conversas, cada uma conferida contra original confiável e preservada com o hash dos bytes servidos, carimbos de tempo de terceiros e URLs de procedência. Atende a duas leituras: a recuperação da fonte por LLM e a demonstração, perante terceiros, de integridade e anterioridade.

## Regras invioláveis

1. O agente nunca escreve à mão o texto de uma fonte. Bytes, hashes, carimbos, WARC, `texto.md` e resultado da conferência saem do runner do GitHub Actions (`captura.yml`). Ao agente cabe detectar, classificar, localizar o candidato a original, propor e relatar.
2. Nenhum pedido de registro sem aprovação expressa do titular na conversa (chave 1). O agente não aprova, não dispensa e não contorna a aprovação do environment `captura` (chave 2): não chama endpoints de revisão de deployments pendentes, não altera revisores nem regras do environment e não pede a terceiros que o façam.
3. Append-only. Nada dentro de `fontes/**/capturas/` nem `pedidos/*.json` se altera, apaga ou renomeia depois de entrar no `main`; correção gera captura nova. `REGISTRO.md` só cresce no fim. O `validar.yml` reprova o que violar isso.
4. Material de caso nunca entra, nem no cofre privado: peças e documentos de autos, números de processos concretos em análise, nomes de partes, dados pessoais. Precedente publicado, invocado como autoridade, é fonte e pode entrar.
5. `sinteses/` guarda derivados de modelo e nunca é consultado como fonte. Toda afirmação de uma síntese aponta para a âncora da fonte que a sustenta.
6. Os logs de workflow deste repositório são públicos. Nenhum script imprime conteúdo de obra protegida nem o dado que motivou a reprovação por material de caso.
7. `INDICE.md` e `catalogo.jsonl` são gerados por `scripts/indexar.py` e não se editam à mão. A partir da F1, o `llms.txt` também.
8. O texto próprio do repositório é escrito em português brasileiro, salvo código e termos técnicos, sem travessão (U+2014) nem meia-risca (U+2013). Texto de terceiros, em `fontes/` e `pedidos/`, fica como no original.
9. Toda alteração no `main` entra por pull request, com o check `validar` verde.

## Ordem de leitura para recuperar uma fonte

1. `llms.txt` ou `INDICE.md`, para localizar a fonte por domínio.
2. `catalogo.jsonl`, para filtrar por identificador, tipo, data ou status.
3. `fontes/<dominio>/<id>/FICHA.md`, para metadados, procedência, regime e status.
4. `fontes/<dominio>/<id>/texto.md#<ancora>`, lendo só o trecho necessário.

Antes de citar uma fonte do acervo, confira o `status_verificacao` da FICHA. Só `verificada` sustenta afirmação sem ressalva.

## Estrutura

```
llms.txt                  porta de entrada para LLM (llmstxt.org)
AGENTS.md                 este arquivo
CLAUDE.md                 importa o AGENTS.md
INDICE.md                 catálogo por domínio (gerado)
catalogo.jsonl            um objeto JSON por fonte (gerado)
REGISTRO.md               append-only: uma linha por captura aprovada
schema/                   ficha.schema.json, pedido.schema.json
pedidos/                  pedidos aprovados (chave 1), um JSON por lote
fontes/<dominio>/<id>/    FICHA.md, texto.md, capturas/<AAAAMMDDTHHMMSSZ>/
sinteses/                 derivados de modelo, rotulados e ancorados
scripts/                  validar, indexar, capturar, extrair, conferir, detectar, fixidez
.github/workflows/        validar.yml, captura.yml
```

Domínios: `normas`, `julgados`, `doutrina`, `ciencia`, `tecnica`, `web`.

## Identificadores e âncoras

- Normas: URN LEX no campo `urn` (por exemplo, `urn:lex:br:federal:lei:1998-02-19;9610`) e pasta com slug derivado (`br-federal-lei-1998-02-19-9610`).
- Julgados: `br-<tribunal>-<classe>-<numero>`.
- DOI e arXiv: identificador nativo, com versão fixada no arXiv (`vN`).
- Web: domínio seguido de hash curto da URL.
- Âncoras: por dispositivo nas normas (`#art-46-iii`) e por parágrafo nos demais textos (`#p-0042`). Toda remissão interna aponta para âncora, de modo que o leitor carregue só o trecho necessário.

## Grau da fonte (`grau_fonte`)

1. Primária oficial: DOU para a norma como publicada; inteiro teor no portal do tribunal ou no DJe para julgados; página do editor ou DOI para doutrina e artigos; arXiv com versão; publicação do próprio autor para declaração dele.
2. Oficial compilada: Planalto e equivalentes, para a redação vigente. Quando a questão envolver vigência, capturam-se a versão publicada e a compilada.
3. Secundária: agregadores, notícias, blogs de terceiros. Nunca recebe `verificada`; fica `pendente_fonte_primaria`.

## Regime de armazenamento

- `integral`: atos oficiais (Lei 9.610/1998, art. 8º, IV), obras em domínio público e obras sob licença aberta que permita redistribuição, com a licença capturada junto.
- `trecho`: obra protegida. No repositório público ficam só a passagem relevante (art. 46, III), o hash dos bytes integrais e o link do Wayback; os bytes integrais vão para o cofre privado `biblioteca_mourax_cofre`.

## Tipologia da referência e conferência

- `citacao_literal`: casamento determinístico de string contra o `texto.md`, depois de normalização (NFC, espaços, aspas tipográficas). Resultados: `exata`, `exata_apos_normalizacao`, `divergente` (com diff) e `nao_localizada`.
- `parafrase` e `alusao`: o agente indica a passagem candidata; o trecho gravado é recortado por offsets do `texto.md`, nunca redigitado, e depende de confirmação do titular.
- `mencao`: confere-se a identidade (título, autoria, data, número, versão) contra os metadados do original.
- `dispositivo`: localização estrutural (artigo, parágrafo, inciso, alínea), com preservação das marcas de redação revogada ou alterada.

Divergência é resultado, não erro, e é sempre relatada ao titular.

## Fluxo de registro

1. Detecção e resolução pelo agente (skill `proveniencia-fontes`, comandos `/fontes`, `/fontes projeto` e `/fontes acervo`). Obra que já esteja em pedido anterior ou no catálogo não gera pedido novo.
2. Chave 1: proposta item por item e aprovação expressa na conversa.
3. Pedido: o agente grava `pedidos/<AAAAMMDDTHHMMSSZ>.json`, conforme `schema/pedido.schema.json`, numa branch `pedido/<AAAAMMDDTHHMMSSZ>`, e faz o push. A branch só acrescenta esse arquivo. Com a captura inativa (seção Fase atual), o fluxo para aqui de outro modo: o agente abre PR da branch para o `main` e, com o check `validar` verde, avisa o titular, que faz o merge; o pedido fica no `main` à espera da captura em lote. O agente nunca faz merge no `main`.
4. Chave 2: o `captura.yml` aguarda a aprovação do titular no environment `captura`. Num push, o GitHub executa a versão do workflow que está na própria branch; por isso, ao aprovar, o titular confere que o push só acrescentou o pedido.
5. Captura pelo runner, commit na mesma branch e pull request para o `main`.
6. `validar.yml`: esquemas, coerência de caminhos, imutabilidade, limites da branch de pedido, índice em sincronia, material de caso e estilo.
7. Merge pelo titular. O agente lê a PR e relata o resultado por referência: verificada, divergente (com diff), pendente de fonte primária ou falha de captura.

## REGISTRO.md

Uma linha por captura aprovada, sempre acrescentada no fim, neste formato:

```
## [AAAA-MM-DD] captura | <id> | aprovada
```

## Fase atual

F0, com registro de pedidos.

- Registro de pedidos: ativo.
- Captura: inativa.

`validar.py` e `indexar.py` funcionam; `capturar.py`, `extrair.py`, `conferir.py`, `detectar.py` e `fixidez.py` são esqueletos que descrevem o contrato e terminam com erro. O `captura.yml` só tem disparo manual até a F1; os pedidos acumulados no `main` serão capturados em lote quando ela entrar. As duas linhas acima são lidas pela skill `proveniencia-fontes` para decidir o envio; ao mudar a fase, mantenha o formato.
