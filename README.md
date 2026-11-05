# radar-diario

Dados do widget KWGT das newsletters diárias (Tech IA, Estudo Bíblico, Desafio de Teclado).

`widget.json` é servido pelo GitHub Pages e lido pelo widget com `wg()`.

## Como atualizar (tarefas agendadas)
- Mantenha o formato: `atualizado` (ISO com -03:00), `data` ("Qui, 5 nov"), e `itens` sempre com 3 entradas na ordem tech, biblia, piano.
- `titulo` até ~55 caracteres; `resumo` até ~90 caracteres; `link` é o URL fixo de cada página.
- Atualize só o item da sua newsletter, preserve os outros, faça commit e push na branch `main`.
