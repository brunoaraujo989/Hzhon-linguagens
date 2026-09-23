#!/usr/bin/env python3
"""Transpiler beta Hzhon-Luau para Roblox.

O arquivo fonte continua em português; a saída é Luau com --!strict e marcas
--#hzhon-linha para diagnóstico. O transpiler não executa APIs Roblox localmente.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


class LuauErro(Exception):
    pass


SERVICOS = {
    "jogadores": "Players", "replicado": "ReplicatedStorage", "servidor": "ServerScriptService",
    "armazenamento": "ServerStorage", "entrada": "UserInputService", "som": "SoundService",
    "colecao": "CollectionService", "dados": "DataStoreService", "gui": "StarterGui",
    "iluminacao": "Lighting", "teleporte": "TeleportService", "texto": "TextChatService",
    "insercao": "InsertService", "debris": "Debris", "contexto": "ContextActionService",
}


def expr(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(r"\[([^\[\]]*)\]", lambda m: "{" + m.group(1) + "}", texto)
    texto = texto.replace("verdadeiro", "true").replace("falso", "false").replace("nulo", "nil")
    texto = re.sub(r"\bnao\s+", "not ", texto)
    texto = re.sub(r"\be\b", "and", texto)
    texto = re.sub(r"\bou\b", "or", texto)
    texto = re.sub(r"\btexto\s*\(", "tostring(", texto)
    texto = re.sub(r"\btamanho\s*\(", "#(", texto)
    texto = re.sub(r"\baleatorio\s*\(", "math.random(", texto)
    if '"' in texto or "'" in texto:
        texto = re.sub(r"\s\+\s", " .. ", texto)
    return texto


def transpilar(fonte: str, nome_origem: str = "script.hz", alvo: str = "server") -> str:
    if alvo not in {"server", "local", "module"}:
        raise LuauErro(f"Alvo desconhecido: {alvo}. Use server, local ou module.")
    saida = [f"-- Gerado por Hzhon-Luau beta a partir de {nome_origem}", f"-- alvo: {alvo}", "--!strict", ""]
    nivel = 0
    pilha: list[str] = []
    modulo: str | None = None

    def emitir(texto: str, linha: int) -> None:
        saida.append("    " * nivel + texto + f" --#hzhon-linha {linha}")

    for numero, original in enumerate(fonte.splitlines(), 1):
        linha = original.strip()
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith("/*"):
            emitir("-- " + linha[2:].strip(" */"), numero)
            continue

        if linha == "fim" or linha.startswith("senao"):
            if linha == "fim":
                if not pilha:
                    raise LuauErro(f"Linha {numero}: 'fim' sem bloco aberto")
                tipo = pilha.pop()
                nivel -= 1
                if tipo == "modulo":
                    emitir("return " + (modulo or "modulo"), numero)
                else:
                    emitir("end", numero)
                continue
            nivel = max(0, nivel - 1)
            if linha.startswith("senao_se"):
                emitir("elseif " + expr(linha[len("senao_se"):]), numero)
            else:
                emitir("else", numero)
            nivel += 1
            continue

        convertido: str | None = None
        abre: str | None = None
        m = re.match(r"modulo\s+(\w+)", linha)
        if m:
            modulo = m.group(1)
            convertido, abre = f"local {modulo} = {{}}", "modulo"
        m = re.match(r"fixo\s+([\w_]+)\s*=\s*(.*)", linha)
        if m: convertido = f"local {m.group(1)} = {expr(m.group(2))}"
        m = re.match(r"var\s+([\w_]+)\s*=\s*(.*)", linha)
        if m: convertido = f"local {m.group(1)} = {expr(m.group(2))}"
        m = re.match(r"servico\s+([\w_]+)\s+como\s+(\w+)", linha)
        if m:
            convertido = f"local {m.group(2)} = game:GetService(\"{SERVICOS.get(m.group(1), m.group(1))}\")"
        m = re.match(r"funcao\s+([\w_]+)\s*\((.*)\)", linha)
        if m: convertido, abre = f"local function {m.group(1)}({m.group(2)})", "bloco"
        m = re.match(r"funcao_anonima\s*\((.*)\)\s*=>\s*(.*)", linha)
        if m: convertido = f"function({m.group(1)}) return {expr(m.group(2))} end"
        m = re.match(r"se\s+(.+)", linha)
        if m: convertido, abre = f"if {expr(m.group(1))} then", "bloco"
        m = re.match(r"enquanto\s+(.+)", linha)
        if m: convertido, abre = f"while {expr(m.group(1))} do", "bloco"
        m = re.match(r"para_cada\s+(\w+)\s+em\s+(.+)", linha)
        if m: convertido, abre = f"for _, {m.group(1)} in ipairs({expr(m.group(2))}) do", "bloco"
        m = re.match(r"para_numero\s+(\w+)\s+de\s+(.+?)\s+ate\s+(.+)", linha)
        if m: convertido, abre = f"for {m.group(1)} = {expr(m.group(2))}, {expr(m.group(3))} do", "bloco"
        m = re.match(r"retorne(?:\s+(.+))?", linha)
        if m: convertido = "return" + (" " + expr(m.group(1)) if m.group(1) else "")
        m = re.match(r"imprimir\s+(.+)", linha)
        if m: convertido = f"print({expr(m.group(1))})"
        m = re.match(r"espere\s+(.+)", linha)
        if m: convertido = f"task.wait({expr(m.group(1))})"
        m = re.match(r"iniciar_tarefa\s+(.+)", linha)
        if m: convertido = f"task.spawn({expr(m.group(1))})"
        m = re.match(r"atributo\s+(.+?)\s*,\s*([\"'].*?[\"'])\s*,\s*(.+)", linha)
        if m: convertido = f"{m.group(1)}:SetAttribute({m.group(2)}, {expr(m.group(3))})"
        m = re.match(r"ler_atributo\s+(.+?)\s*,\s*([\"'].*?[\"'])\s+como\s+(\w+)", linha)
        if m: convertido = f"local {m.group(3)} = {m.group(1)}:GetAttribute({m.group(2)})"
        m = re.match(r"objeto\s+(\w+)\s+como\s+(.+)", linha)
        if m: convertido = f"local {m.group(1)} = {expr(m.group(2))}"
        m = re.match(r"filho\s+(.+?)\s+como\s+(\w+)", linha)
        if m: convertido = f"local {m.group(2)} = {m.group(1)}:WaitForChild(\"{m.group(2)}\")"
        m = re.match(r"buscar\s+(.+?)\s+como\s+(\w+)", linha)
        if m: convertido = f"local {m.group(2)} = {expr(m.group(1))}:FindFirstChild(\"{m.group(2)}\")"
        m = re.match(r"ouvir\s+(.+?)\s+com\s+funcao\s*\((.*)\)", linha)
        if m: convertido, abre = f"{m.group(1)}:Connect(function({m.group(2)})", "bloco"
        m = re.match(r"receber\s+(\w+)\s+com\s+funcao\s*\((.*)\)", linha)
        if m: convertido, abre = f"{m.group(1)}.OnServerEvent:Connect(function({m.group(2)})", "bloco"
        m = re.match(r"conectar\s+(.+?)\s+com\s+(.+)", linha)
        if m: convertido = f"{m.group(1)}:Connect({expr(m.group(2))})"
        m = re.match(r"evento_remoto\s+(\w+)\s+em\s+(.+)", linha)
        if m: convertido = f"local {m.group(1)} = {expr(m.group(2))}:WaitForChild(\"{m.group(1)}\")"
        m = re.match(r"enviar\s+(\w+)\s+para\s+(.+?)\s+com\s+(.+)", linha)
        if m: convertido = f"{m.group(1)}:FireClient({m.group(2)}, {expr(m.group(3))})"
        m = re.match(r"enviar_todos\s+(\w+)\s+com\s+(.+)", linha)
        if m: convertido = f"{m.group(1)}:FireAllClients({expr(m.group(2))})"
        m = re.match(r"abrir_dados\s+(\w+)\s+como\s+([\"'].*?[\"'])", linha)
        if m: convertido = f"local {m.group(1)} = Dados:GetDataStore({m.group(2)})"
        m = re.match(r"salvar\s+(\w+)\s+chave\s+(.+?)\s+valor\s+(.+)", linha)
        if m: convertido = f"local sucesso, erro = pcall(function() {m.group(1)}:SetAsync({expr(m.group(2))}, {expr(m.group(3))}) end)"
        m = re.match(r"carregar\s+(\w+)\s+chave\s+(.+?)\s+como\s+(\w+)", linha)
        if m: convertido = f"local {m.group(3)} = {m.group(1)}:GetAsync({expr(m.group(2))})"
        m = re.match(r"exportar\s+(\w+)", linha)
        if m and modulo: convertido = f"{modulo}.{m.group(1)} = {m.group(1)}"
        if linha == "pare": convertido = "break"
        if linha == "continue": convertido = "continue"
        if convertido is None: convertido = expr(linha)

        emitir(convertido, numero)
        if abre:
            nivel += 1
            pilha.append(abre)

    if pilha:
        raise LuauErro("O script terminou com blocos Hzhon abertos: " + ", ".join(pilha))
    return "\n".join(saida) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="hzhon luau", description="Transpilar Hzhon para Luau/Roblox beta")
    parser.add_argument("entrada")
    parser.add_argument("-o", "--saida", default=None)
    parser.add_argument("--alvo", choices=["server", "local", "module"], default="server")
    args = parser.parse_args(argv)
    origem = Path(args.entrada)
    destino = Path(args.saida) if args.saida else origem.with_suffix(".luau")
    try:
        destino.write_text(transpilar(origem.read_text(encoding="utf-8"), origem.name, args.alvo), encoding="utf-8")
    except (OSError, LuauErro) as exc:
        parser.error(str(exc))
    print(f"Luau beta gerado ({args.alvo}): {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
