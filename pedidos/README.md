# pedidos

Pedidos de registro aprovados pelo titular na conversa (chave 1), um arquivo por lote: `pedidos/<AAAAMMDDTHHMMSSZ>.json`, conforme `schema/pedido.schema.json`, com no máximo 20 itens.

Cada pedido chega numa branch `pedido/<AAAAMMDDTHHMMSSZ>`, cujo push aciona o `captura.yml`. Depois de entrar no `main`, o arquivo não se altera nem se apaga, porque integra a cadeia de custódia: a partir da F1, ele é hasheado e carimbado junto com a captura.
