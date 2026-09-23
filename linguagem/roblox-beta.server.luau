-- Gerado por Hzhon-Luau beta a partir de roblox-beta.hz
-- alvo: server
--!strict

local Jogadores = game:GetService("Players") --#hzhon-linha 2
local Replicado = game:GetService("ReplicatedStorage") --#hzhon-linha 3
local Dados = game:GetService("DataStoreService") --#hzhon-linha 4
local AtualizarInventario = Replicado:WaitForChild("AtualizarInventario") --#hzhon-linha 6
local Inventarios = Dados:GetDataStore("HzhonInventariosV1") --#hzhon-linha 7
Jogadores.PlayerAdded:Connect(function(jogador) --#hzhon-linha 9
    jogador:SetAttribute("HzhonBeta", true) --#hzhon-linha 10
    local chave = tostring(jogador.UserId) --#hzhon-linha 11
    local inventario = Inventarios:GetAsync(chave) --#hzhon-linha 12
    print("Inventário carregado para " .. tostring(jogador.Name)) --#hzhon-linha 13
end --#hzhon-linha 14
AtualizarInventario.OnServerEvent:Connect(function(jogador, item) --#hzhon-linha 16
    local sucesso, erro = pcall(function() Inventarios:SetAsync(tostring(jogador.UserId), item) end) --#hzhon-linha 17
    AtualizarInventario:FireClient(jogador, item) --#hzhon-linha 18
end --#hzhon-linha 19
