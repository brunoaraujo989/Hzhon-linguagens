# Hzhon-Luau para Roblox

A variante Hzhon-Luau permite escrever um subconjunto de scripts Roblox em português e transpilar para Luau válido.

## Primeiro script

```hzhon
servico jogadores como Jogadores

funcao preparar(jogador)
    atributo jogador, "HzhonPronto", verdadeiro
    imprimir "Jogador conectado"
fim

ouvir Jogadores.PlayerAdded com funcao(jogador)
    preparar(jogador)
fim
```

Gere o Luau:

```bash
python3 hzhon_cli.py luau meu-script.roblox.hz -o ServerScriptService/MeuScript.server.luau
```

A saída inclui `--!strict` e comentários `--#hzhon-linha N` para que o caminho de debug possa ser mapeado de volta ao arquivo original.

## Recursos alpha

A primeira camada mapeia serviços `game:GetService`, funções, variáveis locais, constantes, condicionais, laços, listas para tabelas, `PlayerAdded`, `Connect`, `SetAttribute`, `task.wait`, `task.spawn`, `print`, `tostring` e iteração `para_cada` para `ipairs`.

O exemplo `inventario.roblox.hz` demonstra um inventário inicial associado ao evento `Players.PlayerAdded`.

## Limites atuais

Esta é uma primeira camada de transpile, não um runtime Roblox completo. Ainda serão adicionados ModuleScripts, RemoteEvents tipados, DataStores com validação, CollectionService, interfaces de plugins, APIs cliente/servidor e source maps formais. Scripts gerados devem ser revisados e testados no Roblox Studio antes de uso em produção.

## Fluxo recomendado

1. Escreva o arquivo `.roblox.hz`.
2. Gere o `.luau` com a CLI.
3. Coloque o resultado na pasta correspondente usando Rojo ou Roblox Studio.
4. Ative `--!strict` e revise as permissões cliente/servidor.
5. Teste eventos, replicação e persistência em um ambiente privado.
