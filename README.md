# biblioteca_mourax

Acervo de fontes de conhecimento efetivamente usadas em conversas com modelos de linguagem. Cada fonte é guardada na íntegra ou, no mínimo, no trecho relevante, conferida contra original confiável e preservada com o hash dos bytes servidos, carimbos de tempo de terceiros e a URL (ou o conjunto de URLs) de procedência. A organização privilegia a leitura eficiente por LLM sem perder a leitura humana.

Estado: F0 (esqueleto). Nenhuma fonte registrada.

## Por onde começar

- Agentes de IA leem o [AGENTS.md](AGENTS.md), com as convenções e as regras invioláveis. O Claude Code lê o [CLAUDE.md](CLAUDE.md), que importa o AGENTS.md.
- A porta de entrada para LLM é o [llms.txt](llms.txt), no formato da proposta llmstxt.org.
- O catálogo está no [INDICE.md](INDICE.md), para leitura humana, e no `catalogo.jsonl`, para leitura por programa. Ambos são gerados por `scripts/indexar.py`.
- O histórico das capturas aprovadas está no [REGISTRO.md](REGISTRO.md), que só cresce no fim.

## Como uma fonte entra

O registro depende de duas aprovações do titular, dadas em canais distintos.

1. Chave 1, na conversa. O modelo detecta a referência, localiza o candidato a original e propõe o registro. Só depois da aprovação expressa grava o pedido em `pedidos/<AAAAMMDDTHHMMSSZ>.json`, numa branch `pedido/<AAAAMMDDTHHMMSSZ>`.
2. Chave 2, no GitHub. O push dessa branch aciona `.github/workflows/captura.yml`, cujo job usa o environment `captura`, com o titular como revisor obrigatório. Antes da aprovação o job não começa e não acessa os segredos do environment.

A captura é feita pelo runner do GitHub Actions, nunca pelo modelo. O runner baixa os bytes, calcula SHA-256 e SHA-512, preserva o contexto HTTP em WARC, obtém carimbos RFC 3161 de duas autoridades, grava atestação Sigstore no log público Rekor, aciona o arquivamento independente pelo Wayback Machine e confere os trechos literais. O resultado chega como pull request e só entra no `main` depois de passar no `validar.yml`.

Enquanto a captura estiver inativa (AGENTS.md, seção Fase atual), o pedido aprovado entra no `main` por pull request e aguarda a captura em lote.

## O que não entra

Material de caso: peças e documentos de autos, números de processos concretos em análise, nomes de partes e dados pessoais. A regra vale também para o cofre privado. Precedente publicado, invocado como autoridade, é fonte e pode entrar.

## Regime autoral

Atos oficiais (Lei 9.610/1998, art. 8º, IV), obras em domínio público e obras sob licença que permita redistribuição são guardados na íntegra. Obra protegida fica só pelo trecho relevante, nos limites do art. 46, III, da mesma lei, com o hash dos bytes integrais no manifesto público e os bytes integrais num repositório privado.

## Licença

O código, os esquemas, os workflows e a documentação própria deste repositório estão sob a licença MIT ([LICENSE](LICENSE)). O conteúdo de terceiros guardado em `fontes/` não está sob essa licença: cada fonte segue o regime declarado no campo `regime_autoral` da sua FICHA.
