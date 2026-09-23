#!/usr/bin/env python3
"""CLI da Hzhon: linguagem, web, Roblox e ferramentas de projeto."""
from __future__ import annotations

import argparse
import html
import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from hzhon import HzhonErro, compilar, executar_fonte, repl
from hzhon_luau import transpilar as transpilar_luau

VERSION = "0.7.0"


@dataclass
class No:
    tipo: str
    args: list[str] = field(default_factory=list)
    filhos: list["No"] = field(default_factory=list)


BLOCOS = {"site", "pagina", "secao", "cartao", "cabecalho", "formulario", "lista"}


def ler_linhas(caminho: Path) -> list[list[str]]:
    resultado = []
    for numero, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        try:
            tokens = shlex.split(linha, comments=True)
        except ValueError as exc:
            raise ValueError(f"Linha {numero}: {exc}") from exc
        if tokens:
            resultado.append(tokens)
    return resultado


def analisar_site(caminho: Path) -> No:
    linhas = ler_linhas(caminho)
    if not linhas or linhas[0][0] != "site":
        raise ValueError("O arquivo de site deve começar com: site \"Nome do site\"")
    raiz = No("site", linhas[0][1:])
    pilha = [raiz]
    for tokens in linhas[1:]:
        comando, args = tokens[0], tokens[1:]
        if comando == "fim":
            if len(pilha) == 1:
                if pilha[0].tipo == "site":
                    continue
                raise ValueError("Há um 'fim' sem bloco correspondente.")
            pilha.pop()
            continue
        no = No(comando, args)
        pilha[-1].filhos.append(no)
        if comando in BLOCOS:
            pilha.append(no)
        elif comando not in {"tema", "titulo", "subtitulo", "texto", "paragrafo", "botao", "imagem", "campo", "item", "codigo", "rodape", "navegacao", "espaco"}:
            raise ValueError(f"Comando web desconhecido: {comando}")
    if len(pilha) != 1:
        raise ValueError(f"Bloco '{pilha[-1].tipo}' não foi fechado com 'fim'.")
    return raiz


def arg(no: No, indice: int, padrao: str = "") -> str:
    return no.args[indice] if len(no.args) > indice else padrao


def render_no(no: No, dentro_secao: bool = False) -> str:
    tipo = no.tipo
    if tipo == "titulo":
        return f'<h1>{html.escape(arg(no, 0))}</h1>'
    if tipo == "subtitulo":
        return f'<p class="lead">{html.escape(arg(no, 0))}</p>'
    if tipo in {"texto", "paragrafo"}:
        return f'<p>{html.escape(arg(no, 0))}</p>'
    if tipo == "cabecalho":
        corpo = "".join(render_no(f) for f in no.filhos)
        if no.args:
            corpo = f'<p class="eyebrow">{html.escape(arg(no, 0))}</p>' + corpo
        return f'<header class="hero">{corpo}</header>'
    if tipo == "botao":
        return f'<a class="button" href="{html.escape(arg(no, 1, "#"), quote=True)}">{html.escape(arg(no, 0))}</a>'
    if tipo == "imagem":
        src = html.escape(arg(no, 0), quote=True)
        alt = html.escape(arg(no, 1, "Imagem"), quote=True)
        return f'<img src="{src}" alt="{alt}" loading="lazy">'
    if tipo == "codigo":
        return f'<pre><code>{html.escape(arg(no, 0))}</code></pre>'
    if tipo == "lista":
        itens = "".join(f'<li>{html.escape(x.args[0])}</li>' for x in no.filhos if x.tipo == "item")
        return f'<ul>{itens}</ul>'
    if tipo == "formulario":
        campos = "".join(render_no(f, True) for f in no.filhos)
        acao = html.escape(arg(no, 1, "#"), quote=True)
        return f'<form action="{acao}" method="post">{f"<h3>{html.escape(arg(no, 0))}</h3>" if no.args else ""}{campos}<button class="button" type="submit">Enviar</button></form>'
    if tipo == "campo":
        nome = html.escape(arg(no, 0, "campo"), quote=True)
        rotulo = html.escape(arg(no, 1, arg(no, 0, "Campo")))
        tipo_campo = html.escape(arg(no, 2, "text"), quote=True)
        return f'<label>{rotulo}<input name="{nome}" type="{tipo_campo}" placeholder="{rotulo}"></label>'
    if tipo == "cartao":
        titulo = f'<h3>{html.escape(arg(no, 0))}</h3>' if no.args else ""
        return f'<article class="card">{titulo}{"".join(render_no(f, True) for f in no.filhos)}</article>'
    if tipo == "secao":
        titulo = f'<h2>{html.escape(arg(no, 0))}</h2>' if no.args else ""
        return f'<section><div class="wrap">{titulo}<div class="grid">{"".join(render_no(f, True) for f in no.filhos)}</div></div></section>'
    if tipo == "navegacao":
        return '<nav class="nav"><strong>Hzhon</strong><a href="/">início</a></nav>'
    if tipo == "rodape":
        return f'<footer>{html.escape(arg(no, 0, "Criado com Hzhon"))}</footer>'
    if tipo == "espaco":
        return "<div class=\"space\"></div>"
    return ""


def css(tema: str) -> str:
    escuro = tema in {"escuro", "dark"}
    fundo = "#101b19" if escuro else "#f7f5ed"
    texto = "#edf3ea" if escuro else "#18221f"
    painel = "#1b2b27" if escuro else "#ffffff"
    linha = "#36514a" if escuro else "#d8ded5"
    return f""":root {{ --fundo:{fundo}; --texto:{texto}; --painel:{painel}; --linha:{linha}; --coral:#e56d52; --menta:#bce5d2; --max:1080px; }}
* {{ box-sizing:border-box; }} body {{ margin:0; color:var(--texto); background:var(--fundo); font:16px/1.7 system-ui,-apple-system,Segoe UI,sans-serif; }}
.wrap {{ width:min(var(--max),calc(100% - 40px)); margin:auto; }} .nav {{ display:flex; justify-content:space-between; align-items:center; width:min(var(--max),calc(100% - 40px)); margin:auto; padding:22px 0; }}
.nav strong {{ font:700 20px ui-monospace,monospace; }} .nav strong::first-letter {{ color:var(--coral); }} .nav a {{ color:inherit; text-decoration:none; opacity:.72; }}
.hero {{ padding:110px max(20px,calc((100% - var(--max))/2)) 100px; background:radial-gradient(circle at 80% 30%,#294d42,transparent 38%),var(--fundo); }}
.hero h1 {{ max-width:760px; margin:12px 0; font:400 clamp(44px,8vw,88px)/.98 Georgia,serif; letter-spacing:-.06em; }} .hero h1::first-line {{ color:var(--texto); }} .hero .lead {{ max-width:620px; font-size:19px; opacity:.72; }} .eyebrow {{ color:var(--coral); font:700 11px ui-monospace,monospace; letter-spacing:.14em; text-transform:uppercase; }}
.button {{ display:inline-block; margin:15px 10px 0 0; padding:10px 17px; border-radius:99px; color:#14211e; background:var(--menta); text-decoration:none; font-weight:700; }}
section {{ padding:86px 0; border-top:1px solid var(--linha); }} section h2 {{ margin:0 0 28px; font:400 clamp(32px,5vw,54px)/1 Georgia,serif; letter-spacing:-.045em; }} .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px; }} .card {{ padding:24px; border:1px solid var(--linha); border-radius:14px; background:var(--painel); }} .card h3 {{ margin-top:0; font-size:18px; }} img {{ max-width:100%; border-radius:12px; }} pre {{ overflow:auto; padding:20px; color:var(--menta); background:#0b1312; border-radius:10px; }} footer {{ padding:35px max(20px,calc((100% - var(--max))/2)); border-top:1px solid var(--linha); opacity:.65; }} .space {{ height:24px; }}
form {{ display:grid; gap:13px; max-width:520px; padding:22px; border:1px solid var(--linha); border-radius:14px; background:var(--painel); }} label {{ display:grid; gap:5px; font-size:13px; font-weight:700; }} input {{ width:100%; padding:11px 12px; border:1px solid var(--linha); border-radius:8px; color:var(--texto); background:var(--fundo); }}
@media(max-width:600px) {{ .hero {{ padding-top:70px; }} .nav {{ padding-top:16px; }} }}"""


def construir_site(entrada: Path, saida: Path) -> list[Path]:
    raiz = analisar_site(entrada)
    titulo = arg(raiz, 0, "Site Hzhon")
    tema = "claro"
    paginas = []
    for filho in raiz.filhos:
        if filho.tipo == "tema": tema = arg(filho, 0, "claro")
        if filho.tipo == "pagina": paginas.append(filho)
    if not paginas:
        raise ValueError("O site precisa de pelo menos uma 'pagina'.")
    saida.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for indice, pagina in enumerate(paginas):
        caminho = "/" if indice == 0 else arg(pagina, 1, f"/pagina-{indice}")
        nome = "index.html" if caminho == "/" else caminho.strip("/").replace("/", "-") + ".html"
        corpo = "".join(render_no(f) for f in pagina.filhos)
        documento = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(titulo)}</title><style>{css(tema)}</style></head><body>{corpo}</body></html>'''
        destino = saida / nome
        destino.write_text(documento, encoding="utf-8")
        arquivos.append(destino)
    return arquivos


def analisar_jogo(caminho: Path) -> dict:
    linhas = ler_linhas(caminho)
    if not linhas or linhas[0][0] != "jogo":
        raise ValueError("O arquivo de jogo deve começar com: jogo \"Nome\"")
    jogo = {"titulo": arg(No("jogo", linhas[0][1:]), 0, "Jogo Hzhon"), "largura": 960, "altura": 540, "fundo": "#101b19", "mensagem": "Chegue ao objetivo!", "jogadores": [], "inimigos": [], "plataformas": [], "controles": {}, "objetivo": None}
    fechou = False
    for tokens in linhas[1:]:
        comando, args = tokens[0], tokens[1:]
        if comando == "fim":
            fechou = True
            continue
        try:
            if comando == "tela": jogo["largura"], jogo["altura"] = int(args[0]), int(args[1])
            elif comando == "fundo": jogo["fundo"] = args[0]
            elif comando == "mensagem": jogo["mensagem"] = " ".join(args)
            elif comando in {"jogador", "inimigo"}:
                item = {"nome": args[0], "x": float(args[1]), "y": float(args[2]), "tamanho": float(args[3]), "cor": args[4]}
                jogo["jogadores" if comando == "jogador" else "inimigos"].append(item)
            elif comando == "plataforma":
                jogo["plataformas"].append({"x": float(args[0]), "y": float(args[1]), "largura": float(args[2]), "altura": float(args[3]), "cor": args[4]})
            elif comando == "objetivo":
                jogo["objetivo"] = {"x": float(args[0]), "y": float(args[1]), "tamanho": float(args[2]), "cor": args[3]}
            elif comando == "controle":
                jogo["controles"].setdefault(args[0], {})[args[1]] = args[2].lower()
            else:
                raise ValueError(f"Linha desconhecida no jogo: {comando}")
        except (IndexError, ValueError) as exc:
            raise ValueError(f"Comando de jogo inválido: {' '.join(tokens)}") from exc
    if not fechou: raise ValueError("O jogo precisa terminar com 'fim'.")
    if not jogo["jogadores"]: raise ValueError("O jogo precisa de pelo menos um 'jogador'.")
    if not jogo["objetivo"]: raise ValueError("O jogo precisa de um 'objetivo'.")
    return jogo


def jogo_html(jogo: dict) -> str:
    dados = json.dumps(jogo, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(jogo["titulo"])}</title><style>
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#07100f;color:#edf3ea;font:16px system-ui,sans-serif}}main{{width:min(100%,1000px);padding:20px}}h1{{font:400 clamp(26px,5vw,48px) Georgia,serif;margin:0 0 6px}}p{{opacity:.72;margin:0 0 16px}}.game-wrap{{position:relative;border:1px solid #36514a;border-radius:16px;overflow:hidden;background:#101b19;box-shadow:0 20px 70px #0008}}canvas{{display:block;width:100%;height:auto;image-rendering:auto}}.hud{{position:absolute;inset:14px 16px auto;display:flex;justify-content:space-between;pointer-events:none;font-weight:700;text-shadow:0 2px 5px #000}}button{{border:0;border-radius:999px;padding:10px 16px;background:#bce5d2;color:#14211e;font-weight:700;cursor:pointer;margin-top:14px}}.touch{{display:flex;gap:8px;justify-content:center}}.touch button{{min-width:58px;background:#294d42;color:#edf3ea}}@media(min-width:700px){{.touch{{display:none}}}}</style></head><body><main><h1>{html.escape(jogo["titulo"])}</h1><p>Jogo criado com Hzhon — sem escrever HTML ou JavaScript.</p><div class="game-wrap"><canvas id="jogo" width="{jogo["largura"]}" height="{jogo["altura"]}"></canvas><div class="hud"><span id="estado">jogando</span><span id="pontos">0</span></div></div><div class="touch"><button data-key="left">◀</button><button data-key="up">▲</button><button data-key="right">▶</button></div><button id="reiniciar">Reiniciar jogo</button></main><script>const CONFIG={dados};const canvas=document.querySelector('#jogo'),ctx=canvas.getContext('2d'),keys={{}},estado=document.querySelector('#estado');let ganhou=false;const player={{...CONFIG.jogadores[0],vx:0,vy:0,inicioX:CONFIG.jogadores[0].x,inicioY:CONFIG.jogadores[0].y}};const inimigos=CONFIG.inimigos.map(x=>({{...x,vx:1}}));const objetivo=CONFIG.objetivo;function caixa(o){{return{{x:o.x,y:o.y,w:o.tamanho||o.largura,h:o.tamanho||o.altura}}}}function toca(a,b){{return a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y}}function reiniciar(){{player.x=player.inicioX;player.y=player.inicioY;player.vx=0;player.vy=0;ganhou=false;estado.textContent='jogando'}}function desenhar(){{ctx.fillStyle=CONFIG.fundo;ctx.fillRect(0,0,canvas.width,canvas.height);CONFIG.plataformas.forEach(p=>{{ctx.fillStyle=p.cor;ctx.fillRect(p.x,p.y,p.largura,p.altura)}});inimigos.forEach(e=>{{ctx.fillStyle=e.cor;ctx.fillRect(e.x,e.y,e.tamanho,e.tamanho)}});ctx.fillStyle=objetivo.cor;ctx.fillRect(objetivo.x,objetivo.y,objetivo.tamanho,objetivo.tamanho);ctx.fillStyle=player.cor;ctx.fillRect(player.x,player.y,player.tamanho,player.tamanho)}}function atualizar(){{if(!ganhou){{const c=CONFIG.controles[player.nome]||{{esquerda:'a',direita:'d',cima:'w'}};player.vx=0;if(keys[c.esquerda]||keys['arrowleft'])player.vx=-4;if(keys[c.direita]||keys['arrowright'])player.vx=4;if((keys[c.cima]||keys['arrowup']||keys[' '])&&player.noChao)player.vy=-11;player.vy+=.5;player.x=Math.max(0,Math.min(canvas.width-player.tamanho,player.x+player.vx));const antes=player.y;player.y+=player.vy;player.noChao=false;CONFIG.plataformas.forEach(p=>{{const ch=caixa(p),pro=caixa(player);if(toca(pro,ch)&&antes+player.tamanho<=ch.y+4&&player.vy>=0){{player.y=ch.y-player.tamanho;player.vy=0;player.noChao=true}}}});if(player.y>canvas.height+80)reiniciar();inimigos.forEach(e=>{{e.x+=e.vx;if(e.x<0||e.x+e.tamanho>canvas.width)e.vx*=-1;if(toca(caixa(player),caixa(e))){{estado.textContent='tente novamente';reiniciar()}}}});if(toca(caixa(player),caixa(objetivo))){{ganhou=true;estado.textContent='vitória!'}}}}desenhar();requestAnimationFrame(atualizar)}}window.addEventListener('keydown',e=>{{keys[e.key.toLowerCase()]=true}});window.addEventListener('keyup',e=>{{keys[e.key.toLowerCase()]=false}});document.querySelectorAll('[data-key]').forEach(b=>{{b.onpointerdown=()=>keys[b.dataset.key]=true;b.onpointerup=()=>keys[b.dataset.key]=false}});document.querySelector('#reiniciar').onclick=reiniciar;atualizar();</script></body></html>'''


def construir_jogo(entrada: Path, saida: Path) -> Path:
    jogo = analisar_jogo(entrada)
    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / "index.html"
    destino.write_text(jogo_html(jogo), encoding="utf-8")
    return destino


def criar_site(nome: str) -> Path:
    raiz = Path(nome)
    raiz.mkdir(parents=True, exist_ok=True)
    arquivo = raiz / "site.hz"
    if arquivo.exists():
        raise FileExistsError(f"O projeto '{nome}' já existe.")
    arquivo.write_text('''site "Meu primeiro site Hzhon"\ntema "escuro"\npagina inicio "/"\n    navegacao\n    cabecalho "BETA HZHON 0.7"\n        titulo "Um site escrito na minha linguagem."\n        subtitulo "Sem escrever HTML diretamente: o Hzhon gera a página final para você."\n        botao "Conhecer a linguagem" "#recursos"\n    fim\n    secao "O que posso criar"\n        cartao "Páginas"\n            texto "Landing pages, portfólios e páginas de documentação."\n        fim\n        cartao "Projetos"\n            texto "A mesma linguagem também organiza lógica, dados e automações."\n        fim\n    fim\n    rodape "Criado com Hzhon 0.7 — programação em português."\nfim\nfim\n''', encoding="utf-8")
    (raiz / "dist").mkdir()
    (raiz / "README.md").write_text(f'''# {nome}\n\nSite criado com Hzhon.\n\n```bash\nhzhon construir site.hz --saida dist\nhzhon servir dist\n```\n''', encoding="utf-8")
    return raiz


def criar_projeto_roblox(nome: str) -> Path:
    raiz = Path(nome)
    if raiz.exists():
        raise FileExistsError(f"O projeto '{nome}' já existe.")
    (raiz / "src").mkdir(parents=True)
    (raiz / "src" / "server.roblox.hz").write_text('''servico jogadores como Jogadores
ouvir Jogadores.PlayerAdded com funcao(jogador)
    imprimir "Jogador conectado: " + texto(jogador.Name)
fim
''', encoding="utf-8")
    (raiz / "src" / "client.roblox.hz").write_text('''servico jogadores como Jogadores
servico entrada como Entrada
var jogador = Jogadores.LocalPlayer

ouvir Entrada.InputBegan com funcao(input, processado)
    se processado == falso
        imprimir "Entrada recebida por " + texto(jogador.Name)
    fim
fim
''', encoding="utf-8")
    (raiz / "src" / "util.roblox.hz").write_text('''modulo Util
funcao dizer(mensagem)
    imprimir mensagem
fim
exportar dizer
fim
''', encoding="utf-8")
    (raiz / "README.md").write_text(f'''# {nome}

Projeto Roblox criado com Hzhon-Luau beta.

```bash
python3 ../hzhon_cli.py luau src/server.roblox.hz --alvo server -o {nome}.server.luau
python3 ../hzhon_cli.py luau src/client.roblox.hz --alvo local -o {nome}.client.luau
python3 ../hzhon_cli.py luau src/util.roblox.hz --alvo module -o {nome}.module.luau
```
''', encoding="utf-8")
    return raiz


def criar_projeto_linguagem(nome: str) -> Path:
    raiz = Path(nome)
    if raiz.exists():
        raise FileExistsError(f"O projeto '{nome}' já existe.")
    (raiz / "src").mkdir(parents=True)
    (raiz / "src" / "main.hz").write_text(
        '''# Projeto criado com Hzhon 0.7 beta
var pessoa = {
    nome: "mundo",
    versao: 0.7
}

imprimir "Olá, " + pessoa.nome + "!"
imprimir "Tipo: " + tipo(pessoa)
''',
        encoding="utf-8",
    )
    (raiz / "hzhon.toml").write_text(
        f'''[projeto]
nome = "{raiz.name}"
versao = "0.7.0"
entrada = "src/main.hz"
''',
        encoding="utf-8",
    )
    (raiz / "README.md").write_text(
        f'''# {raiz.name}

Projeto criado com Hzhon.

```bash
hzhon verificar src/main.hz
hzhon executar src/main.hz
```
''',
        encoding="utf-8",
    )
    return raiz


def formatar_hzhon(caminho: Path) -> str:
    """Formata blocos Hzhon sem alterar comentários ou expressões."""
    linhas: list[str] = []
    nivel = 0
    fechamentos = {"fim", "senao", "senao_se", "capture"}
    aberturas = {
        "site",
        "pagina",
        "cabecalho",
        "secao",
        "cartao",
        "formulario",
        "lista",
        "funcao",
        "se",
        "enquanto",
        "para_cada",
        "tente",
    }
    for original in caminho.read_text(encoding="utf-8").splitlines():
        texto = original.strip()
        if not texto:
            if linhas and linhas[-1] != "":
                linhas.append("")
            continue
        comando = texto.split(maxsplit=1)[0]
        if comando in fechamentos:
            nivel = max(0, nivel - 1)
        linhas.append("    " * nivel + texto)
        if comando in aberturas:
            nivel += 1
        if comando in {"senao", "senao_se", "capture"}:
            nivel += 1
    while linhas and linhas[-1] == "":
        linhas.pop()
    return "\n".join(linhas) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="hzhon",
        description="Linguagem Hzhon, gerador web e ferramentas para Roblox",
    )
    parser.add_argument("--version", action="version", version=f"Hzhon {VERSION} beta")
    sub = parser.add_subparsers(dest="comando")
    novo = sub.add_parser("novo", help="criar um projeto")
    novo.add_argument("tipo", choices=["projeto", "site", "roblox"])
    novo.add_argument("nome")
    construir = sub.add_parser("construir", help="gerar arquivos web a partir de um .hz")
    construir.add_argument("entrada")
    construir.add_argument("--saida", default="dist")
    jogo = sub.add_parser("jogo", help="gerar um jogo Canvas a partir de um .jogo.hz")
    jogo.add_argument("entrada")
    jogo.add_argument("--saida", default="dist-jogo")
    executar = sub.add_parser("executar", help="executar um programa Hzhon")
    executar.add_argument("arquivo")
    verificar = sub.add_parser("verificar", help="verificar sintaxe sem executar")
    verificar.add_argument("arquivo")
    sub.add_parser("repl", help="abrir o REPL interativo")
    sub.add_parser("versao", help="mostrar a versão da Hzhon")
    sub.add_parser("diagnostico", help="verificar o ambiente local da Hzhon")
    testar = sub.add_parser("testar", help="executar a suíte de testes do projeto")
    testar.add_argument("pasta", nargs="?", default=".")
    formatar = sub.add_parser("formatar", help="formatar um arquivo Hzhon sem alterar sua lógica")
    formatar.add_argument("arquivo")
    servir = sub.add_parser("servir", help="servir uma pasta construída")
    servir.add_argument("pasta", nargs="?", default="dist")
    servir.add_argument("--porta", type=int, default=8080)
    servir.add_argument("--host", default="0.0.0.0")
    luau = sub.add_parser("luau", help="transpilar para Roblox/Luau beta")
    luau.add_argument("entrada")
    luau.add_argument("-o", "--saida", default=None)
    luau.add_argument("--alvo", choices=["server", "local", "module"], default="server")
    args = parser.parse_args(argv)
    try:
        if args.comando == "novo":
            if args.tipo == "site":
                projeto = criar_site(args.nome)
            elif args.tipo == "roblox":
                projeto = criar_projeto_roblox(args.nome)
            else:
                projeto = criar_projeto_linguagem(args.nome)
            print(f"Projeto Hzhon criado em {projeto}/")
            return 0
        if args.comando == "construir":
            arquivos = construir_site(Path(args.entrada), Path(args.saida))
            print(f"Construção concluída: {len(arquivos)} página(s) em {args.saida}/")
            return 0
        if args.comando == "jogo":
            arquivo = construir_jogo(Path(args.entrada), Path(args.saida))
            print(f"Jogo Hzhon construído em: {arquivo}")
            return 0
        if args.comando == "executar":
            caminho = Path(args.arquivo)
            executar_fonte(caminho.read_text(encoding="utf-8"), caminho)
            return 0
        if args.comando == "verificar":
            caminho = Path(args.arquivo)
            compilar(caminho.read_text(encoding="utf-8"))
            print(f"Sintaxe válida: {caminho}")
            return 0
        if args.comando == "repl":
            return repl()
        if args.comando == "versao":
            print(f"Hzhon {VERSION} beta")
            return 0
        if args.comando == "diagnostico":
            raiz = Path(__file__).resolve().parent
            verificacoes = {
                "python": sys.version_info >= (3, 10),
                "runtime": (raiz / "hzhon.py").is_file(),
                "cli": (raiz / "hzhon_cli.py").is_file(),
                "luau": (raiz / "hzhon_luau.py").is_file(),
            }
            for nome, ok in verificacoes.items():
                print(f"{'OK' if ok else 'ERRO'} {nome}")
            return 0 if all(verificacoes.values()) else 1
        if args.comando == "testar":
            pasta = Path(args.pasta).resolve()
            resultado = subprocess.run([sys.executable, "-m", "unittest", "discover", "-v"], cwd=pasta)
            return resultado.returncode
        if args.comando == "formatar":
            caminho = Path(args.arquivo)
            caminho.write_text(formatar_hzhon(caminho), encoding="utf-8")
            print(f"Arquivo formatado: {caminho}")
            return 0
        if args.comando == "luau":
            entrada = Path(args.entrada)
            destino = Path(args.saida) if args.saida else entrada.with_suffix(".luau")
            destino.write_text(transpilar_luau(entrada.read_text(encoding="utf-8"), entrada.name, args.alvo), encoding="utf-8")
            print(f"Luau beta gerado ({args.alvo}): {destino}")
            return 0
        if args.comando == "servir":
            pasta = Path(args.pasta).resolve()
            os.chdir(pasta)
            servidor = ThreadingHTTPServer((args.host, args.porta), SimpleHTTPRequestHandler)
            print(f"Hzhon web em http://{args.host}:{args.porta}/ (Ctrl+C para parar)")
            servidor.serve_forever()
            return 0
        parser.print_help()
        return 0
    except (ValueError, HzhonErro, FileNotFoundError, FileExistsError, OSError) as exc:
        print(f"Erro Hzhon: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
