#!/usr/bin/env python3
"""Interpretador da linguagem Hzhon.

O runtime continua pequeno e legível de propósito: a Hzhon deve ser fácil de
estudar, mas já oferece variáveis, funções, listas, mapas, módulos locais,
tratamento de erros e uma biblioteca padrão útil.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


class HzhonErro(Exception):
    """Erro apresentado ao programador Hzhon."""


class Retorno(Exception):
    def __init__(self, valor: Any):
        self.valor = valor


class Pare(Exception):
    pass


class Continue(Exception):
    pass


class FalhaHzhon(Exception):
    def __init__(self, valor: Any):
        self.valor = valor


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
        "var": "VAR",
        "fixo": "FIXO",
        "se": "SE",
        "senao": "SENAO",
        "senao_se": "SENAO_SE",
        "enquanto": "ENQUANTO",
        "para_cada": "PARA_CADA",
        "em": "EM",
        "funcao": "FUNCAO",
        "retorne": "RETORNE",
        "fim": "FIM",
        "pare": "PARE",
        "continue": "CONTINUE",
        "verdadeiro": "VERDADEIRO",
        "falso": "FALSO",
        "nulo": "NULO",
        "e": "E",
        "ou": "OU",
        "nao": "NAO",
        "imprimir": "IMPRIMIR",
        "importe": "IMPORTE",
        "tente": "TENTE",
        "capture": "CAPTURE",
        "lance": "LANCE",
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
        caractere = self.fonte[self.atual]
        self.atual += 1
        return caractere

    def adicionar(self, tipo: str, literal: Any = None) -> None:
        texto = self.fonte[self.inicio : self.atual]
        self.tokens.append(Token(tipo, texto, literal, self.linha))

    def conferir(self, esperado: str) -> bool:
        if self.fim() or self.fonte[self.atual] != esperado:
            return False
        self.atual += 1
        return True

    def token(self) -> None:
        caractere = self.avancar()
        simples = {
            "(": "ABRE_PAREN",
            ")": "FECHA_PAREN",
            "[": "ABRE_COL",
            "]": "FECHA_COL",
            "{": "ABRE_CHAVE",
            "}": "FECHA_CHAVE",
            ",": "VIRGULA",
            ".": "PONTO",
            "+": "MAIS",
            "-": "MENOS",
            "*": "VEZES",
            "%": "MOD",
            ":": "DOIS_PONTOS",
        }
        if caractere in simples:
            self.adicionar(simples[caractere])
            return
        if caractere == "\n":
            self.linha += 1
            return
        if caractere in " \t\r;":
            return
        if caractere == "#":
            while not self.fim() and self.fonte[self.atual] != "\n":
                self.avancar()
            return
        if caractere in "\"'":
            self.string(caractere)
            return
        if caractere.isdigit():
            self.numero()
            return
        if caractere.isalpha() or caractere == "_" or caractere in "çãáàâéêíóôúüÇÃÁÀÂÍÓÔÚÜ":
            self.identificador()
            return
        pares = {
            "=": ("IGUAL", "IGUAL_IGUAL"),
            "!": (None, "DIFERENTE"),
            "<": ("MENOR", "MENOR_IGUAL"),
            ">": ("MAIOR", "MAIOR_IGUAL"),
            "/": ("BARRA", "COMENTARIO_BLOCO"),
        }
        if caractere in pares:
            simples_tipo, duplo = pares[caractere]
            if self.conferir("="):
                self.adicionar(duplo)
            elif caractere == "/" and self.conferir("/"):
                while not self.fim() and self.fonte[self.atual] != "\n":
                    self.avancar()
            elif caractere == "/" and self.conferir("*"):
                while not self.fim() and self.fonte[self.atual : self.atual + 2] != "*/":
                    if self.avancar() == "\n":
                        self.linha += 1
                if not self.fim():
                    self.atual += 2
            elif simples_tipo:
                self.adicionar(simples_tipo)
            else:
                raise HzhonErro(f"Linha {self.linha}: símbolo '!' deve ser seguido de '='.")
            return
        raise HzhonErro(f"Linha {self.linha}: caractere inesperado {caractere!r}.")

    def string(self, delimitador: str) -> None:
        valor: list[str] = []
        while not self.fim() and self.fonte[self.atual] != delimitador:
            caractere = self.avancar()
            if caractere == "\\" and not self.fim():
                escapes = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    '"': '"',
                    "'": "'",
                }
                valor.append(escapes.get(self.avancar(), ""))
            else:
                if caractere == "\n":
                    self.linha += 1
                valor.append(caractere)
        if self.fim():
            raise HzhonErro(f"Linha {self.linha}: texto não terminado.")
        self.avancar()
        self.adicionar("TEXTO", "".join(valor))

    def numero(self) -> None:
        while not self.fim() and self.fonte[self.atual].isdigit():
            self.avancar()
        tipo = "INTEIRO"
        if (
            not self.fim()
            and self.fonte[self.atual] == "."
            and self.atual + 1 < len(self.fonte)
            and self.fonte[self.atual + 1].isdigit()
        ):
            tipo = "DECIMAL"
            self.avancar()
            while not self.fim() and self.fonte[self.atual].isdigit():
                self.avancar()
        texto = self.fonte[self.inicio : self.atual]
        self.adicionar(tipo, float(texto) if tipo == "DECIMAL" else int(texto))

    def identificador(self) -> None:
        acentos = "çãáàâéêíóôúüÇÃÁÀÂÍÓÔÚÜ"
        while not self.fim() and (
            self.fonte[self.atual].isalnum()
            or self.fonte[self.atual] == "_"
            or self.fonte[self.atual] in acentos
        ):
            self.avancar()
        texto = self.fonte[self.inicio : self.atual]
        self.adicionar(self.PALAVRAS.get(texto, "IDENTIFICADOR"))


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.atual = 0

    def analisar(self) -> list[Any]:
        resultado = []
        while not self.fim():
            resultado.append(self.declaracao())
        return resultado

    def fim(self) -> bool:
        return self.verificar("EOF")

    def olhar(self) -> Token:
        return self.tokens[self.atual]

    def anterior(self) -> Token:
        return self.tokens[self.atual - 1]

    def avancar(self) -> Token:
        if not self.fim():
            self.atual += 1
        return self.anterior()

    def verificar(self, tipo: str) -> bool:
        return self.olhar().tipo == tipo

    def aceitar(self, *tipos: str) -> Token | None:
        for tipo in tipos:
            if self.verificar(tipo):
                return self.avancar()
        return None

    def exigir(self, tipo: str, mensagem: str) -> Token:
        if self.verificar(tipo):
            return self.avancar()
        token = self.olhar()
        raise HzhonErro(f"Linha {token.linha}: {mensagem} Encontrado {token.lexema!r}.")

    def declaracao(self) -> Any:
        if self.aceitar("VAR", "FIXO"):
            return self.declaracao_variavel(self.anterior().tipo == "FIXO")
        if self.aceitar("FUNCAO"):
            return self.funcao()
        if self.aceitar("SE"):
            return self.se()
        if self.aceitar("ENQUANTO"):
            return self.enquanto()
        if self.aceitar("PARA_CADA"):
            return self.para_cada()
        if self.aceitar("RETORNE"):
            return ("retorne", self.expressao())
        if self.aceitar("PARE"):
            return ("pare",)
        if self.aceitar("CONTINUE"):
            return ("continue",)
        if self.aceitar("IMPRIMIR"):
            return ("imprimir", self.expressao())
        if self.aceitar("IMPORTE"):
            arquivo = self.exigir("TEXTO", "Use importe \"caminho.hz\".")
            return ("importe", arquivo.literal)
        if self.aceitar("LANCE"):
            return ("lance", self.expressao())
        if self.aceitar("TENTE"):
            return self.tente()
        return ("expr", self.expressao())

    def declaracao_variavel(self, constante: bool) -> Any:
        nome = self.exigir("IDENTIFICADOR", "Esperava o nome da variável.").lexema
        valor = self.expressao() if self.aceitar("IGUAL") else ("literal", None)
        return ("var", nome, constante, valor)

    def bloco(self, *fim_tokens: str) -> list[Any]:
        bloco = []
        while not self.fim() and not any(self.verificar(x) for x in fim_tokens):
            bloco.append(self.declaracao())
        return bloco

    def funcao(self) -> Any:
        nome = self.exigir("IDENTIFICADOR", "Esperava o nome da função.").lexema
        self.exigir("ABRE_PAREN", "Esperava '('.")
        parametros: list[str] = []
        if not self.verificar("FECHA_PAREN"):
            while True:
                parametros.append(
                    self.exigir("IDENTIFICADOR", "Esperava nome de parâmetro.").lexema
                )
                if not self.aceitar("VIRGULA"):
                    break
        self.exigir("FECHA_PAREN", "Esperava ')'.")
        corpo = self.bloco("FIM")
        self.exigir("FIM", "Esperava 'fim' após a função.")
        return ("funcao", nome, parametros, corpo)

    def se(self) -> Any:
        condicao = self.expressao()
        corpo = self.bloco("SENAO_SE", "SENAO", "FIM")
        ramos = [(condicao, corpo)]
        while self.aceitar("SENAO_SE"):
            ramos.append((self.expressao(), self.bloco("SENAO_SE", "SENAO", "FIM")))
        outro = self.bloco("FIM") if self.aceitar("SENAO") else []
        self.exigir("FIM", "Esperava 'fim' após o condicional.")
        return ("se", ramos, outro)

    def enquanto(self) -> Any:
        condicao = self.expressao()
        corpo = self.bloco("FIM")
        self.exigir("FIM", "Esperava 'fim' após enquanto.")
        return ("enquanto", condicao, corpo)

    def para_cada(self) -> Any:
        nome = self.exigir("IDENTIFICADOR", "Esperava variável do para_cada.").lexema
        self.exigir("EM", "Use 'em' para indicar a coleção.")
        colecao = self.expressao()
        corpo = self.bloco("FIM")
        self.exigir("FIM", "Esperava 'fim' após para_cada.")
        return ("para", nome, colecao, corpo)

    def tente(self) -> Any:
        corpo = self.bloco("CAPTURE", "FIM")
        nome_erro = "erro"
        captura: list[Any] = []
        if self.aceitar("CAPTURE"):
            if self.verificar("IDENTIFICADOR"):
                nome_erro = self.avancar().lexema
            captura = self.bloco("FIM")
        self.exigir("FIM", "Esperava 'fim' após tente.")
        return ("tente", corpo, nome_erro, captura)

    def expressao(self) -> Any:
        return self.atribuicao()

    def atribuicao(self) -> Any:
        expressao = self.ou()
        if self.aceitar("IGUAL"):
            valor = self.atribuicao()
            if expressao[0] in ("nome", "indice", "propriedade"):
                return ("atribuir", expressao, valor)
            raise HzhonErro(f"Linha {self.anterior().linha}: destino inválido para atribuição.")
        return expressao

    def ou(self) -> Any:
        expressao = self.e()
        while self.aceitar("OU"):
            expressao = ("bin", "ou", expressao, self.e())
        return expressao

    def e(self) -> Any:
        expressao = self.igualdade()
        while self.aceitar("E"):
            expressao = ("bin", "e", expressao, self.igualdade())
        return expressao

    def igualdade(self) -> Any:
        expressao = self.comparacao()
        while self.aceitar("IGUAL_IGUAL", "DIFERENTE"):
            expressao = ("bin", self.anterior().lexema, expressao, self.comparacao())
        return expressao

    def comparacao(self) -> Any:
        expressao = self.termo()
        while self.aceitar("MENOR", "MENOR_IGUAL", "MAIOR", "MAIOR_IGUAL"):
            expressao = ("bin", self.anterior().lexema, expressao, self.termo())
        return expressao

    def termo(self) -> Any:
        expressao = self.fator()
        while self.aceitar("MAIS", "MENOS"):
            expressao = ("bin", self.anterior().lexema, expressao, self.fator())
        return expressao

    def fator(self) -> Any:
        expressao = self.unario()
        while self.aceitar("VEZES", "BARRA", "MOD"):
            expressao = ("bin", self.anterior().lexema, expressao, self.unario())
        return expressao

    def unario(self) -> Any:
        if self.aceitar("NAO", "MENOS"):
            return ("un", self.anterior().lexema, self.unario())
        return self.chamada()

    def chamada(self) -> Any:
        expressao = self.primario()
        while True:
            if self.aceitar("ABRE_PAREN"):
                argumentos: list[Any] = []
                if not self.verificar("FECHA_PAREN"):
                    while True:
                        argumentos.append(self.expressao())
                        if not self.aceitar("VIRGULA"):
                            break
                self.exigir("FECHA_PAREN", "Esperava ')'.")
                expressao = ("chamada", expressao, argumentos)
            elif self.aceitar("ABRE_COL"):
                indice = self.expressao()
                self.exigir("FECHA_COL", "Esperava ']'.")
                expressao = ("indice", expressao, indice)
            elif self.aceitar("PONTO"):
                nome = self.exigir(
                    "IDENTIFICADOR", "Esperava o nome da propriedade depois de '.'."
                ).lexema
                expressao = ("propriedade", expressao, nome)
            else:
                break
        return expressao

    def primario(self) -> Any:
        token = self.avancar()
        if token.tipo in ("INTEIRO", "DECIMAL", "TEXTO"):
            return ("literal", token.literal)
        if token.tipo == "VERDADEIRO":
            return ("literal", True)
        if token.tipo == "FALSO":
            return ("literal", False)
        if token.tipo == "NULO":
            return ("literal", None)
        if token.tipo == "IDENTIFICADOR":
            return ("nome", token.lexema)
        if token.tipo == "ABRE_PAREN":
            expressao = self.expressao()
            self.exigir("FECHA_PAREN", "Esperava ')'.")
            return expressao
        if token.tipo == "ABRE_COL":
            valores: list[Any] = []
            if not self.verificar("FECHA_COL"):
                while True:
                    valores.append(self.expressao())
                    if not self.aceitar("VIRGULA"):
                        break
            self.exigir("FECHA_COL", "Esperava ']'.")
            return ("lista", valores)
        if token.tipo == "ABRE_CHAVE":
            pares: list[tuple[str, Any]] = []
            if not self.verificar("FECHA_CHAVE"):
                while True:
                    chave = self.avancar()
                    if chave.tipo not in ("IDENTIFICADOR", "TEXTO"):
                        raise HzhonErro(
                            f"Linha {chave.linha}: a chave do mapa deve ser texto ou identificador."
                        )
                    self.exigir("DOIS_PONTOS", "Esperava ':' depois da chave.")
                    pares.append((str(chave.literal or chave.lexema), self.expressao()))
                    if not self.aceitar("VIRGULA"):
                        break
            self.exigir("FECHA_CHAVE", "Esperava '}'.")
            return ("mapa", pares)
        raise HzhonErro(f"Linha {token.linha}: esperava uma expressão, encontrei {token.lexema!r}.")


class Ambiente:
    def __init__(self, pai: "Ambiente | None" = None):
        self.valores: dict[str, list[Any]] = {}
        self.pai = pai

    def definir(self, nome: str, valor: Any, constante: bool = False) -> None:
        self.valores[nome] = [valor, constante]

    def encontrar(self, nome: str) -> "Ambiente":
        if nome in self.valores:
            return self
        if self.pai:
            return self.pai.encontrar(nome)
        raise HzhonErro(f"Nome '{nome}' não foi definido.")

    def obter(self, nome: str) -> Any:
        return self.encontrar(nome).valores[nome][0]

    def atribuir(self, nome: str, valor: Any) -> None:
        ambiente = self.encontrar(nome)
        if ambiente.valores[nome][1]:
            raise HzhonErro(f"'{nome}' é fixo e não pode ser alterado.")
        ambiente.valores[nome][0] = valor


@dataclass
class Funcao:
    nome: str
    params: list[str]
    corpo: list[Any]
    fechamento: Ambiente
    nativa: Callable[..., Any] | None = None

    def chamar(self, interpretador: "Interpretador", args: list[Any]) -> Any:
        if self.nativa:
            try:
                return self.nativa(*args)
            except HzhonErro:
                raise
            except Exception as exc:
                raise HzhonErro(f"Falha em '{self.nome}': {exc}") from exc
        if len(args) != len(self.params):
            raise HzhonErro(
                f"A função '{self.nome}' esperava {len(self.params)} argumento(s), "
                f"recebeu {len(args)}."
            )
        ambiente = Ambiente(self.fechamento)
        for nome, valor in zip(self.params, args):
            ambiente.definir(nome, valor)
        try:
            interpretador.executar_bloco(self.corpo, ambiente)
        except Retorno as retorno:
            return retorno.valor
        return None


class Interpretador:
    def __init__(self):
        self.global_ = Ambiente()
        self.ambiente = self.global_
        self.arquivo_atual: Path | None = None
        self.importados: set[Path] = set()
        self.registrar_nativas()

    def registrar_nativas(self) -> None:
        nativas: dict[str, tuple[list[str], Callable[..., Any]]] = {
            "tamanho": (["valor"], lambda valor: len(valor)),
            "texto": (["valor"], formatar),
            "numero": (["valor"], converter_numero),
            "faixa": (["fim"], lambda fim: list(range(int(fim)))),
            "juntar": (["lista", "separador"], lambda l, s: s.join(formatar(x) for x in l)),
            "chaves": (["mapa"], lambda mapa: list(mapa.keys())),
            "valores": (["mapa"], lambda mapa: list(mapa.values())),
            "contem": (["colecao", "valor"], lambda colecao, valor: valor in colecao),
            "maiusculas": (["valor"], lambda valor: str(valor).upper()),
            "minusculas": (["valor"], lambda valor: str(valor).lower()),
            "recortar": (["valor", "inicio", "fim"], lambda v, i, f: str(v)[int(i) : int(f)]),
            "arredondar": (["valor", "casas"], lambda v, c: round(float(v), int(c))),
            "tipo": (["valor"], tipo_hzhon),
            "ler_arquivo": (["caminho"], self.ler_arquivo),
            "escrever_arquivo": (["caminho", "conteudo"], self.escrever_arquivo),
        }
        for nome, (params, funcao) in nativas.items():
            self.global_.definir(nome, Funcao(nome, params, [], self.global_, funcao))

    def ler_arquivo(self, caminho: Any) -> str:
        return self.resolver_caminho(str(caminho)).read_text(encoding="utf-8")

    def escrever_arquivo(self, caminho: Any, conteudo: Any) -> Any:
        destino = self.resolver_caminho(str(caminho))
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(str(conteudo), encoding="utf-8")
        return True

    def resolver_caminho(self, caminho: str) -> Path:
        destino = Path(caminho).expanduser()
        if not destino.is_absolute() and self.arquivo_atual:
            destino = self.arquivo_atual.parent / destino
        return destino.resolve()

    def executar(self, programa: list[Any]) -> None:
        for declaracao in programa:
            self.executar_stmt(declaracao)

    def executar_bloco(self, bloco: list[Any], ambiente: Ambiente) -> None:
        anterior = self.ambiente
        self.ambiente = ambiente
        try:
            for declaracao in bloco:
                self.executar_stmt(declaracao)
        finally:
            self.ambiente = anterior

    def executar_stmt(self, declaracao: Any) -> None:
        tipo = declaracao[0]
        if tipo == "var":
            self.ambiente.definir(
                declaracao[1], self.avaliar(declaracao[3]), declaracao[2]
            )
        elif tipo == "expr":
            self.avaliar(declaracao[1])
        elif tipo == "imprimir":
            print(formatar(self.avaliar(declaracao[1])))
        elif tipo == "atribuir":
            self.avaliar(declaracao)
        elif tipo == "funcao":
            self.ambiente.definir(
                declaracao[1],
                Funcao(declaracao[1], declaracao[2], declaracao[3], self.ambiente),
            )
        elif tipo == "retorne":
            raise Retorno(self.avaliar(declaracao[1]))
        elif tipo == "pare":
            raise Pare()
        elif tipo == "continue":
            raise Continue()
        elif tipo == "lance":
            raise FalhaHzhon(self.avaliar(declaracao[1]))
        elif tipo == "importe":
            self.importar(str(declaracao[1]))
        elif tipo == "se":
            for condicao, corpo in declaracao[1]:
                if verdade(self.avaliar(condicao)):
                    self.executar_bloco(corpo, Ambiente(self.ambiente))
                    break
            else:
                if declaracao[2]:
                    self.executar_bloco(declaracao[2], Ambiente(self.ambiente))
        elif tipo == "enquanto":
            while verdade(self.avaliar(declaracao[1])):
                try:
                    self.executar_bloco(declaracao[2], Ambiente(self.ambiente))
                except Continue:
                    continue
                except Pare:
                    break
        elif tipo == "para":
            colecao = self.avaliar(declaracao[2])
            for item in colecao:
                ambiente = Ambiente(self.ambiente)
                ambiente.definir(declaracao[1], item)
                try:
                    self.executar_bloco(declaracao[3], ambiente)
                except Continue:
                    continue
                except Pare:
                    break
        elif tipo == "tente":
            try:
                self.executar_bloco(declaracao[1], Ambiente(self.ambiente))
            except (HzhonErro, FalhaHzhon, ZeroDivisionError, TypeError, ValueError) as erro:
                ambiente = Ambiente(self.ambiente)
                valor = erro.valor if isinstance(erro, FalhaHzhon) else str(erro)
                ambiente.definir(declaracao[2], valor)
                self.executar_bloco(declaracao[3], ambiente)

    def importar(self, caminho: str) -> None:
        destino = self.resolver_caminho(caminho)
        if destino.suffix == "":
            destino = destino.with_suffix(".hz")
        if not destino.exists():
            raise HzhonErro(f"Módulo '{caminho}' não encontrado em {destino}.")
        destino = destino.resolve()
        if destino in self.importados:
            return
        self.importados.add(destino)
        antigo = self.arquivo_atual
        self.arquivo_atual = destino
        try:
            self.executar(Parser(Lexer(destino.read_text(encoding="utf-8")).analisar()).analisar())
        finally:
            self.arquivo_atual = antigo

    def avaliar(self, expressao: Any) -> Any:
        tipo = expressao[0]
        if tipo == "literal":
            return expressao[1]
        if tipo == "nome":
            return self.ambiente.obter(expressao[1])
        if tipo == "lista":
            return [self.avaliar(item) for item in expressao[1]]
        if tipo == "mapa":
            return {chave: self.avaliar(valor) for chave, valor in expressao[1]}
        if tipo == "atribuir":
            valor = self.avaliar(expressao[2])
            alvo = expressao[1]
            if alvo[0] == "nome":
                self.ambiente.atribuir(alvo[1], valor)
            elif alvo[0] == "indice":
                colecao = self.avaliar(alvo[1])
                indice = self.avaliar(alvo[2])
                self.definir_indice(colecao, indice, valor)
            else:
                objeto = self.avaliar(alvo[1])
                definir_propriedade(objeto, alvo[2], valor)
            return valor
        if tipo == "indice":
            colecao = self.avaliar(expressao[1])
            indice = self.avaliar(expressao[2])
            try:
                return colecao[indice]
            except (KeyError, IndexError, TypeError) as exc:
                raise HzhonErro(f"Índice ou chave inválida: {indice!r}.") from exc
        if tipo == "propriedade":
            return obter_propriedade(self.avaliar(expressao[1]), expressao[2])
        if tipo == "un":
            valor = self.avaliar(expressao[2])
            return (not verdade(valor)) if expressao[1] == "nao" else -valor
        if tipo == "bin":
            return self.binario(expressao[1], expressao[2], expressao[3])
        if tipo == "chamada":
            funcao = self.avaliar(expressao[1])
            argumentos = [self.avaliar(item) for item in expressao[2]]
            if not isinstance(funcao, Funcao):
                raise HzhonErro("O valor chamado não é uma função.")
            return funcao.chamar(self, argumentos)
        raise HzhonErro("Expressão interna desconhecida.")

    def definir_indice(self, colecao: Any, indice: Any, valor: Any) -> None:
        try:
            colecao[indice] = valor
        except (KeyError, IndexError, TypeError) as exc:
            raise HzhonErro(f"Não foi possível alterar o índice {indice!r}.") from exc

    def binario(self, operador: str, esquerda: Any, direita: Any) -> Any:
        a = self.avaliar(esquerda)
        if operador == "e" and not verdade(a):
            return False
        if operador == "ou" and verdade(a):
            return True
        b = self.avaliar(direita)
        operacoes = {
            "+": lambda: a + b,
            "-": lambda: a - b,
            "*": lambda: a * b,
            "/": lambda: a / b,
            "%": lambda: a % b,
            "==": lambda: a == b,
            "!=": lambda: a != b,
            "<": lambda: a < b,
            "<=": lambda: a <= b,
            ">": lambda: a > b,
            ">=": lambda: a >= b,
            "e": lambda: verdade(a) and verdade(b),
            "ou": lambda: verdade(a) or verdade(b),
        }
        try:
            return operacoes[operador]()
        except KeyError as exc:
            raise HzhonErro(f"Operador '{operador}' não suportado.") from exc
        except Exception as exc:
            raise HzhonErro(f"Não foi possível aplicar '{operador}': {exc}") from exc


def converter_numero(valor: Any) -> int | float:
    texto = str(valor).strip().replace(",", ".")
    numero = float(texto)
    return int(numero) if numero.is_integer() else numero


def tipo_hzhon(valor: Any) -> str:
    if valor is None:
        return "nulo"
    if isinstance(valor, bool):
        return "booleano"
    if isinstance(valor, (int, float)):
        return "numero"
    if isinstance(valor, str):
        return "texto"
    if isinstance(valor, list):
        return "lista"
    if isinstance(valor, dict):
        return "mapa"
    if isinstance(valor, Funcao):
        return "funcao"
    return "desconhecido"


def obter_propriedade(objeto: Any, nome: str) -> Any:
    if isinstance(objeto, dict):
        if nome not in objeto:
            raise HzhonErro(f"O mapa não possui a propriedade '{nome}'.")
        return objeto[nome]
    if nome == "tamanho" and isinstance(objeto, (str, list, tuple)):
        return len(objeto)
    raise HzhonErro(f"Não é possível acessar '.{nome}' nesse valor.")


def definir_propriedade(objeto: Any, nome: str, valor: Any) -> None:
    if not isinstance(objeto, dict):
        raise HzhonErro(f"Somente mapas podem receber propriedades; não '{nome}'.")
    objeto[nome] = valor


def verdade(valor: Any) -> bool:
    return bool(valor)


def formatar(valor: Any) -> str:
    if valor is None:
        return "nulo"
    if valor is True:
        return "verdadeiro"
    if valor is False:
        return "falso"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    if isinstance(valor, list):
        return "[" + ", ".join(formatar(item) for item in valor) + "]"
    if isinstance(valor, dict):
        pares = ", ".join(f"{chave}: {formatar(item)}" for chave, item in valor.items())
        return "{" + pares + "}"
    return str(valor)


def compilar(fonte: str) -> list[Any]:
    return Parser(Lexer(fonte).analisar()).analisar()


def executar_fonte(
    fonte: str, caminho: str | Path | None = None, interpretador: Interpretador | None = None
) -> Interpretador:
    runtime = interpretador or Interpretador()
    antigo = runtime.arquivo_atual
    if caminho:
        runtime.arquivo_atual = Path(caminho).resolve()
    try:
        runtime.executar(compilar(fonte))
    finally:
        runtime.arquivo_atual = antigo
    return runtime


def repl() -> int:
    runtime = Interpretador()
    print("Hzhon 0.7 beta — REPL em português. Use 'sair' para terminar.")
    while True:
        try:
            linha = input("hzhon> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if linha.strip() in {"sair", "saída", "exit", "quit"}:
            return 0
        if not linha.strip():
            continue
        try:
            executar_fonte(linha, interpretador=runtime)
        except (HzhonErro, ZeroDivisionError) as erro:
            print(f"erro: {erro}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    argumentos = argv or sys.argv[1:]
    if not argumentos:
        return repl()
    try:
        if argumentos[0] in {"--repl", "repl"}:
            return repl()
        caminho = Path(argumentos[0])
        executar_fonte(caminho.read_text(encoding="utf-8"), caminho)
    except (HzhonErro, ZeroDivisionError, FileNotFoundError, OSError) as erro:
        print(f"Erro Hzhon: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())