#!/usr/bin/env python3
"""Interpretador inicial da linguagem Hzhon.

Hzhon é uma linguagem experimental em português, executada por uma máquina
virtual simples baseada em AST. Esta versão prioriza clareza, mensagens de erro
e uma sintaxe pequena, mas realmente utilizável.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Callable


class HzhonErro(Exception):
    pass


@dataclass
class Token:
    tipo: str
    lexema: str
    literal: Any
    linha: int

    def __repr__(self) -> str:
        return f"Token({self.tipo}, {self.lexema!r}, {self.literal!r}, linha={self.linha})"


class Lexer:
    PALAVRAS = {
        "var": "VAR", "fixo": "FIXO", "se": "SE", "senao": "SENAO",
        "senao_se": "SENAO_SE", "enquanto": "ENQUANTO", "para_cada": "PARA_CADA",
        "em": "EM", "funcao": "FUNCAO", "retorne": "RETORNE", "fim": "FIM",
        "pare": "PARE", "continue": "CONTINUE", "verdadeiro": "VERDADEIRO",
        "falso": "FALSO", "nulo": "NULO", "e": "E", "ou": "OU", "nao": "NAO",
        "imprimir": "IMPRIMIR",
    }

    def __init__(self, fonte: str):
        self.fonte = fonte
        self.inicio = 0
        self.atual = 0
        self.linha = 1
        self.tokens: list[Token] = []

    def analisar(self) -> list[Token]:
        while not self.fim():
            self.inicio = self.atual
            self.token()
        self.tokens.append(Token("EOF", "", None, self.linha))
        return self.tokens

    def fim(self) -> bool:
        return self.atual >= len(self.fonte)

    def avancar(self) -> str:
        c = self.fonte[self.atual]
        self.atual += 1
        return c

    def adicionar(self, tipo: str, literal: Any = None) -> None:
        texto = self.fonte[self.inicio:self.atual]
        self.tokens.append(Token(tipo, texto, literal, self.linha))

    def conferir(self, esperado: str) -> bool:
        if self.fim() or self.fonte[self.atual] != esperado:
            return False
        self.atual += 1
        return True

    def token(self) -> None:
        c = self.avancar()
        simples = {"(": "ABRE_PAREN", ")": "FECHA_PAREN", "[": "ABRE_COL",
                   "]": "FECHA_COL", ",": "VIRGULA", ".": "PONTO", "+": "MAIS",
                   "-": "MENOS", "*": "VEZES", "%": "MOD", ":": "DOIS_PONTOS"}
        if c in simples:
            self.adicionar(simples[c]); return
        if c == "\n": self.linha += 1; return
        if c in " \t\r": return
        if c == "#":
            while not self.fim() and self.fonte[self.atual] != "\n": self.avancar()
            return
        if c == '"' or c == "'":
            self.string(c); return
        if c.isdigit():
            self.numero(); return
        if c.isalpha() or c == "_" or c in "çãáàâéêíóôúüÇÃÁÀÂÉÊÍÓÔÚÜ":
            self.identificador(); return
        pares = {"=": ("IGUAL", "IGUAL_IGUAL"), "!": (None, "DIFERENTE"),
                 "<": ("MENOR", "MENOR_IGUAL"), ">": ("MAIOR", "MAIOR_IGUAL"),
                 "/": ("BARRA", "COMENTARIO_BLOCO")}
        if c in pares:
            simples_tipo, duplo = pares[c]
            if self.conferir("="): self.adicionar(duplo)
            elif c == "/" and self.conferir("/"):
                while not self.fim() and self.fonte[self.atual] != "\n": self.avancar()
            elif c == "/" and self.conferir("*"):
                while not self.fim() and not (self.fonte[self.atual:self.atual+2] == "*/"):
                    if self.avancar() == "\n": self.linha += 1
                if not self.fim(): self.atual += 2
            elif simples_tipo: self.adicionar(simples_tipo)
            else: raise HzhonErro(f"Linha {self.linha}: símbolo '!' deve ser seguido de '='.")
            return
        raise HzhonErro(f"Linha {self.linha}: caractere inesperado {c!r}.")

    def string(self, delimitador: str) -> None:
        valor = []
        while not self.fim() and self.fonte[self.atual] != delimitador:
            c = self.avancar()
            if c == "\\" and not self.fim():
                escapes = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'"}
                valor.append(escapes.get(self.avancar(), valor[-1] if valor else ""))
            else:
                if c == "\n": self.linha += 1
                valor.append(c)
        if self.fim(): raise HzhonErro(f"Linha {self.linha}: texto não terminado.")
        self.avancar()
        self.adicionar("TEXTO", "".join(valor))

    def numero(self) -> None:
        while not self.fim() and self.fonte[self.atual].isdigit(): self.avancar()
        tipo = "INTEIRO"
        if not self.fim() and self.fonte[self.atual] == "." and self.atual + 1 < len(self.fonte) and self.fonte[self.atual+1].isdigit():
            tipo = "DECIMAL"; self.avancar()
            while not self.fim() and self.fonte[self.atual].isdigit(): self.avancar()
        texto = self.fonte[self.inicio:self.atual]
        self.adicionar(tipo, float(texto) if tipo == "DECIMAL" else int(texto))

    def identificador(self) -> None:
        while not self.fim() and (self.fonte[self.atual].isalnum() or self.fonte[self.atual] == "_" or self.fonte[self.atual] in "çãáàâéêíóôúüÇÃÁÀÂÉÊÍÓÔÚÜ"):
            self.avancar()
        texto = self.fonte[self.inicio:self.atual]
        self.adicionar(self.PALAVRAS.get(texto, "IDENTIFICADOR"))


class Parser:
    def __init__(self, tokens: list[Token]): self.tokens, self.atual = tokens, 0
    def analisar(self):
        saida = []
        while not self.fim(): saida.append(self.declaracao())
        return saida
    def fim(self): return self.verificar("EOF")
    def olhar(self): return self.tokens[self.atual]
    def anterior(self): return self.tokens[self.atual - 1]
    def avancar(self):
        if not self.fim(): self.atual += 1
        return self.anterior()
    def verificar(self, tipo): return self.olhar().tipo == tipo
    def aceitar(self, *tipos):
        for tipo in tipos:
            if self.verificar(tipo): return self.avancar()
        return None
    def exigir(self, tipo, mensagem):
        if self.verificar(tipo): return self.avancar()
        t = self.olhar(); raise HzhonErro(f"Linha {t.linha}: {mensagem} Encontrado {t.lexema!r}.")
    def declaracao(self):
        if self.aceitar("VAR", "FIXO"): return self.declaracao_variavel(self.anterior().tipo == "FIXO")
        if self.aceitar("FUNCAO"): return self.funcao()
        if self.aceitar("SE"): return self.se()
        if self.aceitar("ENQUANTO"): return self.enquanto()
        if self.aceitar("PARA_CADA"): return self.para_cada()
        if self.aceitar("RETORNE"): return ("retorne", self.expressao())
        if self.aceitar("PARE"): return ("pare",)
        if self.aceitar("CONTINUE"): return ("continue",)
        if self.aceitar("IMPRIMIR"): return ("imprimir", self.expressao())
        return ("expr", self.expressao())
    def declaracao_variavel(self, constante):
        nome = self.exigir("IDENTIFICADOR", "Esperava o nome da variável.").lexema
        valor = self.expressao() if self.aceitar("IGUAL") else ("literal", None)
        return ("var", nome, constante, valor)
    def bloco(self, *fim_tokens):
        bloco = []
        while not self.fim() and not any(self.verificar(x) for x in fim_tokens): bloco.append(self.declaracao())
        return bloco
    def funcao(self):
        nome = self.exigir("IDENTIFICADOR", "Esperava o nome da função.").lexema
        self.exigir("ABRE_PAREN", "Esperava '('.")
        params = []
        if not self.verificar("FECHA_PAREN"):
            while True:
                params.append(self.exigir("IDENTIFICADOR", "Esperava nome de parâmetro.").lexema)
                if not self.aceitar("VIRGULA"): break
        self.exigir("FECHA_PAREN", "Esperava ')'.")
        corpo = self.bloco("FIM"); self.exigir("FIM", "Esperava 'fim' após a função.")
        return ("funcao", nome, params, corpo)
    def se(self):
        cond = self.expressao(); corpo = self.bloco("SENAO_SE", "SENAO", "FIM"); ramos = [(cond, corpo)]
        while self.aceitar("SENAO_SE"):
            ramos.append((self.expressao(), self.bloco("SENAO_SE", "SENAO", "FIM")))
        outro = []
        if self.aceitar("SENAO"): outro = self.bloco("FIM")
        self.exigir("FIM", "Esperava 'fim' após o condicional.")
        return ("se", ramos, outro)
    def enquanto(self):
        cond = self.expressao(); corpo = self.bloco("FIM"); self.exigir("FIM", "Esperava 'fim' após enquanto.")
        return ("enquanto", cond, corpo)
    def para_cada(self):
        nome = self.exigir("IDENTIFICADOR", "Esperava variável do para_cada.").lexema
        self.exigir("EM", "Use 'em' para indicar a coleção."); colecao = self.expressao(); corpo = self.bloco("FIM")
        self.exigir("FIM", "Esperava 'fim' após para_cada."); return ("para", nome, colecao, corpo)
    def expressao(self): return self.atribuicao()
    def atribuicao(self):
        expr = self.ou()
        if self.aceitar("IGUAL"):
            valor = self.atribuicao()
            if expr[0] in ("nome", "indice"): return ("atribuir", expr, valor)
            raise HzhonErro(f"Linha {self.anterior().linha}: destino inválido para atribuição.")
        return expr
    def ou(self):
        expr = self.e()
        while self.aceitar("OU"): expr = ("bin", "ou", expr, self.e())
        return expr
    def e(self):
        expr = self.igualdade()
        while self.aceitar("E"): expr = ("bin", "e", expr, self.igualdade())
        return expr
    def igualdade(self):
        expr = self.comparacao()
        while self.aceitar("IGUAL_IGUAL", "DIFERENTE"):
            op = self.anterior().lexema; expr = ("bin", op, expr, self.comparacao())
        return expr
    def comparacao(self):
        expr = self.termo()
        while self.aceitar("MENOR", "MENOR_IGUAL", "MAIOR", "MAIOR_IGUAL"):
            op = self.anterior().lexema; expr = ("bin", op, expr, self.termo())
        return expr
    def termo(self):
        expr = self.fator()
        while self.aceitar("MAIS", "MENOS"):
            op = self.anterior().lexema; expr = ("bin", op, expr, self.fator())
        return expr
    def fator(self):
        expr = self.unario()
        while self.aceitar("VEZES", "BARRA", "MOD"):
            op = self.anterior().lexema; expr = ("bin", op, expr, self.unario())
        return expr
    def unario(self):
        if self.aceitar("NAO", "MENOS"):
            return ("un", self.anterior().lexema, self.unario())
        return self.chamada()
    def chamada(self):
        expr = self.primario()
        while True:
            if self.aceitar("ABRE_PAREN"):
                args = []
                if not self.verificar("FECHA_PAREN"):
                    while True:
                        args.append(self.expressao())
                        if not self.aceitar("VIRGULA"): break
                self.exigir("FECHA_PAREN", "Esperava ')'."); expr = ("chamada", expr, args)
            elif self.aceitar("ABRE_COL"):
                idx = self.expressao(); self.exigir("FECHA_COL", "Esperava ']'."); expr = ("indice", expr, idx)
            else: break
        return expr
    def primario(self):
        t = self.avancar()
        if t.tipo in ("INTEIRO", "DECIMAL", "TEXTO"): return ("literal", t.literal)
        if t.tipo == "VERDADEIRO": return ("literal", True)
        if t.tipo == "FALSO": return ("literal", False)
        if t.tipo == "NULO": return ("literal", None)
        if t.tipo == "IDENTIFICADOR": return ("nome", t.lexema)
        if t.tipo == "ABRE_PAREN":
            expr = self.expressao(); self.exigir("FECHA_PAREN", "Esperava ')'."); return expr
        if t.tipo == "ABRE_COL":
            valores = []
            if not self.verificar("FECHA_COL"):
                while True:
                    valores.append(self.expressao())
                    if not self.aceitar("VIRGULA"): break
            self.exigir("FECHA_COL", "Esperava ']'."); return ("lista", valores)
        raise HzhonErro(f"Linha {t.linha}: esperava uma expressão, encontrei {t.lexema!r}.")


class Ambiente:
    def __init__(self, pai=None): self.valores, self.pai = {}, pai
    def definir(self, nome, valor, constante=False): self.valores[nome] = [valor, constante]
    def encontrar(self, nome):
        if nome in self.valores: return self
        if self.pai: return self.pai.encontrar(nome)
        raise HzhonErro(f"Nome '{nome}' não foi definido.")
    def obter(self, nome): return self.encontrar(nome).valores[nome][0]
    def atribuir(self, nome, valor):
        env = self.encontrar(nome)
        if env.valores[nome][1]: raise HzhonErro(f"'{nome}' é fixo e não pode ser alterado.")
        env.valores[nome][0] = valor


@dataclass
class Funcao:
    nome: str
    params: list[str]
    corpo: list[Any]
    fechamento: Ambiente
    nativa: Callable | None = None
    def chamar(self, interpretador, args):
        if self.nativa: return self.nativa(*args)
        if len(args) != len(self.params): raise HzhonErro(f"A função '{self.nome}' esperava {len(self.params)} argumento(s), recebeu {len(args)}.")
        env = Ambiente(self.fechamento)
        for nome, valor in zip(self.params, args): env.definir(nome, valor)
        try: interpretador.executar_bloco(self.corpo, env)
        except Retorno as r: return r.valor
        return None

class Retorno(Exception):
    def __init__(self, valor): self.valor = valor
class Pare(Exception): pass
class Continue(Exception): pass


class Interpretador:
    def __init__(self):
        self.global_ = Ambiente(); self.ambiente = self.global_
        self.registrar_nativas()
    def registrar_nativas(self):
        self.global_.definir("tamanho", Funcao("tamanho", ["valor"], [], self.global_, lambda v: len(v)))
        self.global_.definir("texto", Funcao("texto", ["valor"], [], self.global_, lambda v: formatar(v)))
        self.global_.definir("numero", Funcao("numero", ["valor"], [], self.global_, lambda v: float(v) if "." in str(v) else int(v)))
        self.global_.definir("faixa", Funcao("faixa", ["fim"], [], self.global_, lambda fim: list(range(int(fim)))))
        self.global_.definir("juntar", Funcao("juntar", ["lista", "separador"], [], self.global_, lambda l, s: s.join(formatar(x) for x in l)))
    def executar(self, programa):
        for stmt in programa: self.executar_stmt(stmt)
    def executar_bloco(self, bloco, ambiente):
        anterior = self.ambiente; self.ambiente = ambiente
        try:
            for stmt in bloco: self.executar_stmt(stmt)
        finally: self.ambiente = anterior
    def executar_stmt(self, s):
        tipo = s[0]
        if tipo == "var": self.ambiente.definir(s[1], self.avaliar(s[3]), s[2])
        elif tipo == "expr": self.avaliar(s[1])
        elif tipo == "imprimir": print(formatar(self.avaliar(s[1])))
        elif tipo == "atribuir": self.avaliar(s)
        elif tipo == "funcao": self.ambiente.definir(s[1], Funcao(s[1], s[2], s[3], self.ambiente))
        elif tipo == "retorne": raise Retorno(self.avaliar(s[1]))
        elif tipo == "pare": raise Pare()
        elif tipo == "continue": raise Continue()
        elif tipo == "se":
            for cond, corpo in s[1]:
                if verdade(self.avaliar(cond)): self.executar_bloco(corpo, Ambiente(self.ambiente)); break
            else: self.executar_bloco(s[2], Ambiente(self.ambiente)) if s[2] else None
        elif tipo == "enquanto":
            while verdade(self.avaliar(s[1])):
                try: self.executar_bloco(s[2], Ambiente(self.ambiente))
                except Continue: continue
                except Pare: break
        elif tipo == "para":
            for item in self.avaliar(s[2]):
                env = Ambiente(self.ambiente); env.definir(s[1], item)
                try: self.executar_bloco(s[3], env)
                except Continue: continue
                except Pare: break
    def avaliar(self, e):
        tipo = e[0]
        if tipo == "literal": return e[1]
        if tipo == "nome": return self.ambiente.obter(e[1])
        if tipo == "lista": return [self.avaliar(x) for x in e[1]]
        if tipo == "atribuir":
            valor = self.avaliar(e[2]); alvo = e[1]
            if alvo[0] == "nome": self.ambiente.atribuir(alvo[1], valor)
            else:
                lista = self.avaliar(alvo[1]); lista[self.avaliar(alvo[2])] = valor
            return valor
        if tipo == "indice": return self.avaliar(e[1])[self.avaliar(e[2])]
        if tipo == "un":
            v = self.avaliar(e[2]); return (not verdade(v)) if e[1] == "nao" else -v
        if tipo == "bin": return self.binario(e[1], e[2], e[3])
        if tipo == "chamada":
            func = self.avaliar(e[1]); args = [self.avaliar(x) for x in e[2]]
            if not isinstance(func, Funcao): raise HzhonErro("O valor chamado não é uma função.")
            return func.chamar(self, args)
        raise HzhonErro("Expressão interna desconhecida.")
    def binario(self, op, esq, dir_):
        a = self.avaliar(esq)
        if op == "e" and not verdade(a): return False
        if op == "ou" and verdade(a): return True
        b = self.avaliar(dir_)
        try:
            return {"+": lambda: a+b, "-": lambda: a-b, "*": lambda: a*b, "/": lambda: a/b,
                    "%": lambda: a%b, "==": lambda: a==b, "!=": lambda: a!=b,
                    "<": lambda: a<b, "<=": lambda: a<=b, ">": lambda: a>b, ">=": lambda: a>=b,
                    "e": lambda: verdade(a) and verdade(b), "ou": lambda: verdade(a) or verdade(b)}[op]()
        except KeyError: raise HzhonErro(f"Operador '{op}' não suportado.")
        except Exception as exc: raise HzhonErro(f"Não foi possível aplicar '{op}': {exc}")


def verdade(v): return bool(v)
def formatar(v):
    if v is None: return "nulo"
    if v is True: return "verdadeiro"
    if v is False: return "falso"
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    if isinstance(v, list): return "[" + ", ".join(formatar(x) for x in v) + "]"
    return str(v)


def executar_fonte(fonte: str) -> None:
    tokens = Lexer(fonte).analisar()
    programa = Parser(tokens).analisar()
    Interpretador().executar(programa)


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Hzhon 0.1.0 — use: python3 hzhon.py arquivo.hz")
        print("REPL ainda não está disponível nesta versão.")
        return 0
    try:
        with open(argv[0], encoding="utf-8") as arq: executar_fonte(arq.read())
    except (HzhonErro, ZeroDivisionError) as exc:
        print(f"Erro Hzhon: {exc}", file=sys.stderr); return 1
    return 0

if __name__ == "__main__": sys.exit(main())
