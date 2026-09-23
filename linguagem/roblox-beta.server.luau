-- Gerado por Hzhon-Luau beta a partir de roblox-beta.hz
-- alvo: server
--!strict

local Jogadores = game:GetService("Players") --#hzhon-linha 2
local Replicado = game:GetService("ReplicatedStorage") --#hzhon-linha 3
local Dados = game:GetService("DataStoreService") --#hzhon-linha 4
local AtualizarInventario = Replicado:WaitForChild("AtualizarInventario") --#hzhon-linha 6
local ConsultarInventario = Replicado:WaitForChild("ConsultarInventario") --#hzhon-linha 7
local Inventarios = Dados:GetDataStore("HzhonInventariosV1") --#hzhon-linha 8
Jogadores.PlayerAdded:Connect(function(jogador) --#hzhon-linha 10
    jogador:SetAttribute("HzhonBeta", true) --#hzhon-linha 11
    local chave = tostring(jogador.UserId) --#hzhon-linha 12
    local inventario = Inventarios:GetAsync(chave) --#hzhon-linha 13
    print("Inventário carregado para " .. tostring(jogador.Name)) --#hzhon-linha 14
end --#hzhon-linha 15
AtualizarInventario.OnServerEvent:Connect(function(jogador, item) --#hzhon-linha 17
    local sucesso, erro = pcall(function() Inventarios:SetAsync(tostring(jogador.UserId), item) end) --#hzhon-linha 18
    AtualizarInventario:FireClient(jogador, item) --#hzhon-linha 19
end --#hzhon-linha 20
ConsultarInventario.OnServerInvoke = function(jogador, pedido) --#hzhon-linha 22
    local inventario = Inventarios:GetAsync(tostring(jogador.UserId)) --#hzhon-linha 23
    return inventario --#hzhon-linha 24
end --#hzhon-linha 25
