# fontes

Uma pasta por fonte, em `fontes/<dominio>/<id>/`, com os domínios `normas`, `julgados`, `doutrina`, `ciencia`, `tecnica` e `web`. Cada pasta contém:

- `FICHA.md`: frontmatter YAML conforme `schema/ficha.schema.json`, seguido de descrição curta;
- `texto.md`: texto canônico, extraído dos bytes capturados, com âncoras estáveis;
- `capturas/<AAAAMMDDTHHMMSSZ>/`: bytes, WARC, manifesto, carimbos, atestação e conferência de cada captura, append-only.

Tudo aqui é gerado pelo pipeline de captura e nada se escreve à mão.

O conteúdo de terceiros guardado nesta pasta não está sob a licença MIT do repositório. Cada fonte segue o regime declarado no campo `regime_autoral` da sua FICHA.
