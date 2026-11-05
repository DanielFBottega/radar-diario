# radar-diario

Dados do widget KWGT das newsletters diárias (Tech IA, Estudo Bíblico, Desafio de Teclado).

`widget.json` é a fonte dos dados. `feed.xml` (RSS gerado por `build_feed.py`) é servido pelo GitHub Pages e lido pelos widgets com `wg(url, rss, índice, title|desc|link)`. O título de cada item é `rótulo | título`.

## Como atualizar (tarefas agendadas)
- Mantenha o formato: `atualizado` (ISO com -03:00), `data` ("Qui, 5 nov"), e `itens` sempre com 3 entradas na ordem tech, biblia, piano.
- `titulo` até ~55 caracteres; `resumo` até ~90 caracteres; `link` é o URL fixo de cada página.
- Atualize só o item da sua newsletter e preserve os outros.
- Depois de editar `widget.json`, rode `python3 build_feed.py` para regenerar `feed.xml` (é o arquivo que o widget KWGT lê). Faça commit dos dois arquivos e push na branch `main`.
