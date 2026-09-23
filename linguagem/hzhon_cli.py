#!/usr/bin/env python3
"""CLI alpha da Hzhon: executa programas e gera sites a partir de .hz."""
from __future__ import annotations

import argparse
import html
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from hzhon import executar_fonte


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


def criar_site(nome: str) -> Path:
    raiz = Path(nome)
    raiz.mkdir(parents=True, exist_ok=True)
    arquivo = raiz / "site.hz"
    if arquivo.exists():
        raise FileExistsError(f"O projeto '{nome}' já existe.")
    arquivo.write_text('''site "Meu primeiro site Hzhon"\ntema "escuro"\npagina inicio "/"\n    navegacao\n    cabecalho "ALPHA HZHON"\n        titulo "Um site escrito na minha linguagem."\n        subtitulo "Sem escrever HTML diretamente: o Hzhon gera a página final para você."\n        botao "Conhecer a linguagem" "#recursos"\n    fim\n    secao "O que posso criar"\n        cartao "Páginas"\n            texto "Landing pages, portfólios e páginas de documentação."\n        fim\n        cartao "Projetos"\n            texto "A mesma linguagem também pode organizar lógica, dados e automações."\n        fim\n    fim\n    rodape "Criado com Hzhon — programação em português."\nfim\nfim\n''', encoding="utf-8")
    (raiz / "dist").mkdir()
    (raiz / "README.md").write_text(f'''# {nome}\n\nSite criado com Hzhon.\n\n```bash\nhzhon construir site.hz --saida dist\nhzhon servir dist\n```\n''', encoding="utf-8")
    return raiz


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="hzhon", description="Linguagem Hzhon e gerador de sites em português")
    sub = parser.add_subparsers(dest="comando")
    novo = sub.add_parser("novo", help="criar um projeto")
    novo.add_argument("tipo", choices=["site"])
    novo.add_argument("nome")
    construir = sub.add_parser("construir", help="gerar arquivos web a partir de um .hz")
    construir.add_argument("entrada")
    construir.add_argument("--saida", default="dist")
    executar = sub.add_parser("executar", help="executar um programa Hzhon")
    executar.add_argument("arquivo")
    testar = sub.add_parser("testar", help="executar a suíte de testes do projeto")
    testar.add_argument("pasta", nargs="?", default=".")
    formatar = sub.add_parser("formatar", help="formatar um arquivo Hzhon sem alterar sua lógica")
    formatar.add_argument("arquivo")
    servir = sub.add_parser("servir", help="servir uma pasta construída")
    servir.add_argument("pasta", nargs="?", default="dist")
    servir.add_argument("--porta", type=int, default=8080)
    args = parser.parse_args(argv)
    try:
        if args.comando == "novo":
            projeto = criar_site(args.nome)
            print(f"Projeto Hzhon criado em {projeto}/site.hz")
            return 0
        if args.comando == "construir":
            arquivos = construir_site(Path(args.entrada), Path(args.saida))
            print(f"Construção concluída: {len(arquivos)} página(s) em {args.saida}/")
            return 0
        if args.comando == "executar":
            executar_fonte(Path(args.arquivo).read_text(encoding="utf-8"))
            return 0
        if args.comando == "testar":
            pasta = Path(args.pasta).resolve()
            resultado = subprocess.run([sys.executable, "-m", "unittest", "discover", "-v"], cwd=pasta)
            return resultado.returncode
        if args.comando == "formatar":
            caminho = Path(args.arquivo)
            linhas = caminho.read_text(encoding="utf-8").splitlines()
            nivel = 0
            saida = []
            fechamentos = {"fim", "senao", "senao_se"}
            aberturas = {"site", "pagina", "cabecalho", "secao", "cartao", "formulario", "lista", "funcao", "se", "enquanto", "para_cada"}
            for linha in linhas:
                texto = linha.strip()
                if not texto: continue
                comando = texto.split(maxsplit=1)[0]
                if comando in fechamentos: nivel = max(0, nivel - 1)
                saida.append("    " * nivel + texto)
                if comando in aberturas: nivel += 1
            caminho.write_text("\n".join(saida) + "\n", encoding="utf-8")
            print(f"Arquivo formatado: {caminho}")
            return 0
        if args.comando == "servir":
            pasta = Path(args.pasta).resolve()
            os.chdir(pasta)
            servidor = ThreadingHTTPServer(("0.0.0.0", args.porta), SimpleHTTPRequestHandler)
            print(f"Hzhon web em http://localhost:{args.porta}/ (Ctrl+C para parar)")
            servidor.serve_forever()
            return 0
        parser.print_help()
        return 0
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"Erro Hzhon: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
