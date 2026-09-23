# Hzhon-Luau beta

A Hzhon-Luau beta transforma arquivos `.roblox.hz` em Luau com `--!strict`, marcação de linha original e três alvos explícitos:

```bash
python3 hzhon_cli.py luau jogo.roblox.hz --alvo server -o Jogo.server.luau
python3 hzhon_cli.py luau entrada.roblox.hz --alvo local -o Entrada.client.luau
python3 hzhon_cli.py luau inventario.roblox.hz --alvo module -o Inventario.module.luau
```

## Recursos beta

A beta suporta `game:GetService`, `PlayerAdded`, `OnServerEvent`, `OnClientEvent`, `FireClient`, `FireServer`, `FireAllClients`, `RemoteFunction` com `OnServerInvoke` e `InvokeServer`, `SetAttribute`, `GetAttribute`, `WaitForChild`, `task.wait`, `task.spawn`, `ModuleScript` com `exportar`, `DataStoreService` com `GetAsync`/`SetAsync`, funções, listas, laços, condicionais e source hints `--#hzhon-linha`.

### Servidor e RemoteEvent

```hzhon
servico replicado como Replicado
evento_remoto Atualizar em Replicado

receber Atualizar com funcao(jogador, valor)
    enviar Atualizar para jogador com valor
fim
```

### ModuleScript

```hzhon
modulo Inventario
funcao criar()
    retorne {}
fim
exportar criar
fim
```

O resultado contém `local Inventario = {}`, uma função local, `Inventario.criar = criar` e `return Inventario`.

### RemoteFunction e eventos do cliente

```hzhon
servico replicado como Replicado
evento_remoto Atualizar em Replicado
remoto_funcao Consultar em Replicado

ouvir_cliente Atualizar com funcao(item)
    imprimir item
fim

responder Consultar com funcao(jogador, pedido)
    retorne pedido
fim

enviar_cliente Atualizar com item
invocar Consultar com pedido como resposta
```

No alvo `server`, `responder` gera `OnServerInvoke`. No alvo `local`, `ouvir_cliente`, `enviar_cliente` e `invocar` geram `OnClientEvent`, `FireServer` e `InvokeServer`, respectivamente. O servidor deve validar todas as entradas recebidas do cliente.

### DataStore

```hzhon
servico dados como Dados
abrir_dados Inventarios como "HzhonInventariosV1"
salvar Inventarios chave texto(jogador.UserId) valor inventario
carregar Inventarios chave texto(jogador.UserId) como inventario
```

O código gerado ainda deve ser envolvido em políticas de retry, validação de dados e limites de chamadas antes de ser usado em produção. A beta gera a estrutura Luau; ela não acessa Roblox durante o build.

## Organização no Roblox Studio

- `*.server.luau` deve ser colocado em `ServerScriptService`.
- `*.client.luau` deve ser colocado em `StarterPlayerScripts`, `StarterGui` ou `StarterCharacterScripts`.
- `*.module.luau` deve ser colocado em `ReplicatedStorage` ou em uma pasta de módulos do projeto.
- RemoteEvents devem existir em `ReplicatedStorage` com o mesmo nome usado no arquivo Hzhon.
- DataStores só funcionam em servidor publicado ou em Studio com acesso a API habilitado para testes.

Rojo e validação de tipos serão as próximas integrações de ferramentas. O arquivo `roblox-beta.hz` demonstra o fluxo completo de inventário, evento remoto e persistência.
