#!/usr/bin/env python3
"""Transpilador inicial Hzhon-Luau.

Converte um subconjunto legível de Hzhon para Luau válido, preservando um mapa
simples de linhas por meio de comentários --#hzhon-linha.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


class LuauErro(Exception):
    pass


SERVICOS = {
    "servico": "game:GetService",
    "jogadores": "Players",
    "replicado": "ReplicatedStorage",
    "servidor": "ServerScriptService",
    "armazenamento": "ServerStorage",
    "entrada": "UserInputService",
    "som": "SoundService",
    "colecao": "CollectionService",
    "dados": "DataStoreService",
    "gui": "StarterGui",
}

OPERADORES = {
    " e ": " and ", " ou ": " or ", "nao ": "not ", "==": "==", " verdadeiro": " true", " falso": " false", " nulo": " nil"
}


def substituir_expressao(texto: str) -> str:
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


def indentacao(nivel: int) -> str:
    return "    " * nivel


def transpilar(fonte: str, nome_origem: str = "script.hz") -> str:
    linhas = fonte.splitlines()
    saida = [f"-- Gerado por Hzhon-Luau a partir de {nome_origem}", "--!strict", ""]
    nivel = 0
    pilha: list[str] = []

    for numero, original in enumerate(linhas, 1):
        linha = original.strip()
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith("/*"):
            saida.append(indentacao(nivel) + "-- " + linha[2:].strip(" */"))
            continue
        if linha == "fim" or linha.startswith("senao"):
            if linha == "fim":
                if not pilha:
                    raise LuauErro(f"Linha {numero}: 'fim' sem bloco aberto")
                nivel -= 1
                pilha.pop()
                saida.append(indentacao(nivel) + "end --#hzhon-linha " + str(numero))
            else:
                nivel = max(0, nivel - 1)
                if linha.startswith("senao_se"):
                    cond = linha[len("senao_se"):].strip()
                    saida.append(indentacao(nivel) + "elseif " + substituir_expressao(cond) + " then --#hzhon-linha " + str(numero))
                else:
                    saida.append(indentacao(nivel) + "else --#hzhon-linha " + str(numero))
                nivel += 1
            continue

        prefixo = indentacao(nivel)
        convertido = None
        bloco = False

        m = re.match(r"fixo\s+([\w_]+)\s*=\s*(.*)", linha)
        if m:
            convertido = f"local {m.group(1)} = {substituir_expressao(m.group(2))}"
        m2 = re.match(r"var\s+([\w_]+)\s*=\s*(.*)", linha)
        if m2:
            convertido = f"local {m2.group(1)} = {substituir_expressao(m2.group(2))}"
        m = re.match(r"funcao\s+([\w_]+)\s*\((.*)\)", linha)
        if m:
            convertido = f"local function {m.group(1)}({m.group(2)})"
            bloco = True
        m = re.match(r"funcao_anonima\s*\((.*)\)\s*=>\s*(.*)", linha)
        if m:
            convertido = f"function({m.group(1)}) return {substituir_expressao(m.group(2))} end"
        m = re.match(r"se\s+(.+)", linha)
        if m:
            convertido = f"if {substituir_expressao(m.group(1))} then"
            bloco = True
        m = re.match(r"enquanto\s+(.+)", linha)
        if m:
            convertido = f"while {substituir_expressao(m.group(1))} do"
            bloco = True
        m = re.match(r"para_cada\s+(\w+)\s+em\s+(.+)", linha)
        if m:
            convertido = f"for _, {m.group(1)} in ipairs({substituir_expressao(m.group(2))}) do"
            bloco = True
        m = re.match(r"para_numero\s+(\w+)\s+de\s+(.+)\s+ate\s+(.+)", linha)
        if m:
            convertido = f"for {m.group(1)} = {substituir_expressao(m.group(2))}, {substituir_expressao(m.group(3))} do"
            bloco = True
        m = re.match(r"retorne(?:\s+(.+))?", linha)
        if m:
            convertido = "return" + (" " + substituir_expressao(m.group(1)) if m.group(1) else "")
        m = re.match(r"imprimir\s+(.+)", linha)
        if m:
            convertido = f"print({substituir_expressao(m.group(1))})"
        m = re.match(r"espere\s+(.+)", linha)
        if m:
            convertido = f"task.wait({substituir_expressao(m.group(1))})"
        m = re.match(r"iniciar_tarefa\s+(.+)", linha)
        if m:
            convertido = f"task.spawn({substituir_expressao(m.group(1))})"
        m = re.match(r"atributo\s+(.+?)\s*,\s*([\"'].*?[\"'])\s*,\s*(.+)", linha)
        if m:
            convertido = f"{m.group(1)}:SetAttribute({m.group(2)}, {substituir_expressao(m.group(3))})"
        m = re.match(r"conectar\s+(.+?)\s+com\s+(.+)", linha)
        if m:
            convertido = f"{m.group(1)}:Connect({substituir_expressao(m.group(2))})"
        m = re.match(r"ouvir\s+(.+?)\s+com\s+funcao\s*\((.*)\)", linha)
        if m:
            convertido = f"{m.group(1)}:Connect(function({m.group(2)})"
            bloco = True
        m = re.match(r"servico\s+([\w_]+)\s+como\s+(\w+)", linha)
        if m:
            nome = SERVICOS.get(m.group(1), m.group(1))
            convertido = f"local {m.group(2)} = game:GetService(\"{nome}\")"
        m = re.match(r"objeto\s+([\w_]+)\s+como\s+(.+)", linha)
        if m:
            convertido = f"local {m.group(1)} = {substituir_expressao(m.group(2))}"
        m = re.match(r"buscar\s+(.+?)\s+como\s+(\w+)", linha)
        if m:
            convertido = f"local {m.group(2)} = {substituir_expressao(m.group(1))}:FindFirstChildWhichIsA(\"BasePart\")"
        m = re.match(r"esperar_evento\s+(.+)", linha)
        if m:
            convertido = f"{m.group(1)}:Wait()"

        if convertido is None:
            convertido = substituir_expressao(linha)
        saida.append(prefixo + convertido + " --#hzhon-linha " + str(numero))
        if bloco:
            nivel += 1
            pilha.append(convertido.split()[0])

    if pilha:
        raise LuauErro("O script terminou com blocos Hzhon abertos: " + ", ".join(pilha))
    return "\n".join(saida) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="hzhon luau", description="Transpilar Hzhon para Luau/Roblox")
    parser.add_argument("entrada")
    parser.add_argument("-o", "--saida", default=None)
    args = parser.parse_args(argv)
    origem = Path(args.entrada)
    destino = Path(args.saida) if args.saida else origem.with_suffix(".luau")
    try:
        destino.write_text(transpilar(origem.read_text(encoding="utf-8"), origem.name), encoding="utf-8")
    except (OSError, LuauErro) as exc:
        parser.error(str(exc))
    print(f"Luau gerado: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
