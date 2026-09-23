# Hzhon

**Hzhon** é uma linguagem de programação experimental em português. A implementação de referência é um interpretador escrito em Python, com lexer, parser, AST implícita e ambiente de execução.

> O runtime atual é o núcleo executável da Hzhon 0.1. A especificação de evolução alpha está em [ESPECIFICACAO_ALPHA.md](ESPECIFICACAO_ALPHA.md).

## Executar

Requer Python 3.10 ou mais recente.

```bash
python3 hzhon.py exemplo.hz
```

Saída esperada:

```text
Hzhon — resultado: 12
Soma da lista: 15
A linguagem está funcionando!
contagem 0
contagem 1
contagem 2
```

## Sintaxe disponível

O interpretador reconhece `var` para variáveis mutáveis e `fixo` para constantes. Os tipos básicos são inferidos a partir dos valores: números inteiros e decimais, textos, booleanos (`verdadeiro` e `falso`), `nulo` e listas.

As estruturas de controle são `se`, `senao_se`, `senao`, `enquanto` e `para_cada ... em`. Funções são declaradas com `funcao`, recebem parâmetros posicionais e podem devolver valores com `retorne`. Os comandos `pare` e `continue` funcionam dentro dos laços.

Os operadores disponíveis incluem `+`, `-`, `*`, `/`, `%`, comparações, `e`, `ou` e `nao`. O operador `+` também concatena textos. Comentários de linha começam com `#`; comentários de bloco usam `/* ... */`.

## Funções nativas

| Função | Finalidade |
|---|---|
| `tamanho(valor)` | Retorna o tamanho de texto ou lista. |
| `texto(valor)` | Converte um valor para texto. |
| `numero(valor)` | Converte um valor para número. |
| `faixa(fim)` | Cria uma lista de inteiros de zero até `fim - 1`. |
| `juntar(lista, separador)` | Junta os itens de uma lista em um texto. |

## Arquitetura

O fluxo de execução é simples e foi mantido explícito para facilitar a evolução da linguagem:

1. O **lexer** converte o texto em tokens e informa a linha de erros.
2. O **parser** converte tokens em uma árvore de expressões e comandos.
3. O **interpretador** avalia expressões e executa comandos em ambientes encadeados.
4. `Funcao` representa funções Hzhon e também funções nativas do runtime.

## Estado da alpha

A especificação alpha cobre tipagem gradual, mapas, `escolha`, erros estruturados, módulos, REPL, biblioteca padrão, testes, ferramentas, interoperabilidade, Hzhon-Luau, Roblox, interfaces e persistência. O núcleo executável será expandido por marcos verificáveis, sem fingir que uma funcionalidade planejada já está pronta.

- **0.1 experimental:** implementado neste repositório.
- **0.2 alpha:** mapas, tipos opcionais, `escolha`, erros estruturados, REPL e módulos locais.
- **0.5 beta:** bytecode, biblioteca padrão, testes nativos, formatador, linter e extensão VS Code.
- **1.0 estável:** pacotes, FFI, WebAssembly, backend Luau e compatibilidade retroativa.

## Testes

```bash
python3 -m unittest -v
```

## Criar sites com Hzhon

A CLI alpha permite descrever uma página em Hzhon e gerar os arquivos finais sem escrever HTML diretamente:

```bash
./bin/hzhon novo site meu-site
./bin/hzhon construir meu-site/site.hz --saida meu-site/dist
./bin/hzhon servir meu-site/dist --porta 8080
```

Um arquivo web usa blocos em português:

```hzhon
site "Meu site"
tema "escuro"
pagina inicio "/"
    cabecalho "PORTFÓLIO"
        titulo "Olá, web"
        subtitulo "Esta página nasceu em Hzhon."
        botao "Conhecer" "#recursos"
    fim
    secao "Recursos"
        cartao "Simples"
            texto "O gerador cria HTML e CSS responsivos."
        fim
    fim
    rodape "Criado com Hzhon."
fim
fim
```

O comando `construir` gera `index.html` e o comando `servir` inicia um servidor local compatível com Linux e Termux. O arquivo `site-demo.hz` deste repositório é um exemplo real usado nos testes da alpha.

### Comandos multifuncionais

Além da web, a CLI reúne operações de desenvolvimento:

```bash
hzhon executar programa.hz
hzhon testar .
hzhon formatar site.hz
hzhon servir dist --porta 8080
```

O instalador para Termux cria um wrapper em `$PREFIX/bin`, dentro da área executável do Termux. Isso evita o erro de permissão que pode ocorrer quando um link aponta diretamente para um arquivo guardado em `storage/downloads`.

## Licença

Protótipo inicial disponibilizado sob licença MIT.

## Roblox e Luau

A variante Hzhon-Luau transpila scripts Roblox escritos em português para Luau. Use `python3 hzhon_cli.py luau inventario.roblox.hz -o inventario.server.luau`. Consulte `ROBLOX.md` para os recursos alpha, limites e fluxo com Rojo/Roblox Studio.
