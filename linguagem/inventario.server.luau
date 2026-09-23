-- Gerado por Hzhon-Luau a partir de inventario.roblox.hz
--!strict

local Jogadores = game:GetService("Players") --#hzhon-linha 2
local Replicado = game:GetService("ReplicatedStorage") --#hzhon-linha 3
local itens_iniciais = {"Bastão", "Poção"} --#hzhon-linha 5
local function preparar_jogador(jogador) --#hzhon-linha 7
    local inventario = {} --#hzhon-linha 8
    jogador:SetAttribute("HzhonPronto", true) --#hzhon-linha 9
    print("Inventário preparado para " .. tostring(jogador.Name)) --#hzhon-linha 10
    return inventario --#hzhon-linha 11
end --#hzhon-linha 12
local function adicionar_item(inventario, item) --#hzhon-linha 14
    table.insert(inventario, item) --#hzhon-linha 15
    return inventario --#hzhon-linha 16
end --#hzhon-linha 17
Jogadores.PlayerAdded:Connect(function(jogador) --#hzhon-linha 19
    local inventario = preparar_jogador(jogador) --#hzhon-linha 20
    for _, item in ipairs(itens_iniciais) do --#hzhon-linha 21
        adicionar_item(inventario, item) --#hzhon-linha 22
    end --#hzhon-linha 23
    print("Itens iniciais entregues") --#hzhon-linha 24
end --#hzhon-linha 25
