# Hzhon — Especificação técnica alpha

**Versão:** 0.2.0-alpha  
**Idioma de referência:** português brasileiro  
**Licença proposta:** MIT  
**Status:** linguagem experimental executável, com especificação de evolução

> Hzhon é uma linguagem de programação em português que reduz a distância entre a ideia de uma pessoa e o código que ela escreve. A alpha separa com clareza o que já funciona do que está especificado para os próximos marcos.

## Sumário

1. [Visão geral e filosofia](#1-visão-geral-e-filosofia)  
2. [Sintaxe fundamental](#2-sintaxe-fundamental)  
3. [Estruturas de controle](#3-estruturas-de-controle)  
4. [Funções](#4-funções)  
5. [Orientação a objetos](#5-orientação-a-objetos)  
6. [Programação funcional](#6-programação-funcional)  
7. [Tratamento de erros](#7-tratamento-de-erros)  
8. [Assincronismo e concorrência](#8-assincronismo-e-concorrência)  
9. [Módulos e ecossistema](#9-módulos-e-ecossistema)  
10. [Sistema de tipos](#10-sistema-de-tipos)  
11. [Performance e execução](#11-performance-e-execução)  
12. [Segurança](#12-segurança)  
13. [Interoperabilidade](#13-interoperabilidade)  
14. [Ferramentas](#14-ferramentas)  
15. [Exemplos práticos](#15-exemplos-práticos)  
16. [Variante para Luau](#16-variante-para-luau)  
17. [Roadmap e versionamento](#17-roadmap-e-versionamento)  
18. [Metaprogramação](#18-metaprogramação)  
19. [Interfaces e multiplataforma](#19-interfaces-e-multiplataforma)  
20. [Persistência e bancos](#20-persistência-e-bancos)  
21. [Observabilidade](#21-observabilidade)  
22. [Comunidade e governança](#22-comunidade-e-governança)  
23. [Casos de uso](#23-casos-de-uso)  
24. [Acessibilidade](#24-acessibilidade)  
25. [Casos extremos e português](#25-casos-extremos-e-português)  
26. [Formato de palavras-chave](#26-formato-de-palavras-chave)

## 1. Visão geral e filosofia

Hzhon resolve um problema de acesso: grande parte do material de programação, das mensagens de erro e das APIs usa inglês como camada obrigatória, mesmo quando a pessoa pensa, estuda e ensina em português. A linguagem não pretende substituir Python, JavaScript, Luau ou C. Ela oferece uma porta de entrada coerente e uma base de experimentação para a comunidade lusófona.

O público principal é formado por iniciantes brasileiros e lusófonos, estudantes, professores e desenvolvedores experientes que desejam uma sintaxe expressiva para prototipagem. O projeto adota cinco princípios: código deve se ler como português; símbolos devem aparecer quando aumentam precisão; erros devem explicar o problema e sugerir o próximo passo; a linguagem deve crescer por módulos; e recursos avançados só entram quando tiverem uma história de aprendizagem clara.

### Posicionamento

| Linguagem | Força principal | Limitação para este projeto | Onde Hzhon se posiciona |
|---|---|---|---|
| Python | Ecossistema e simplicidade | Palavras-chave e documentação majoritariamente em inglês | Hzhon mantém a simplicidade e localiza o núcleo |
| JavaScript | Presença na web | Semântica ampla e histórica, difícil de explicar no início | Hzhon prioriza consistência e mensagens didáticas |
| Node.js | I/O e aplicações de servidor | É um runtime do JavaScript, não uma nova sintaxe | Hzhon terá runtime próprio e APIs em português |
| Luau | Jogos e Roblox | Forte dependência do ambiente Roblox | Hzhon terá uma saída Luau opcional |

## 2. Sintaxe fundamental

Arquivos Hzhon usam a extensão `.hz` e UTF-8. Indentação é recomendada, mas o alpha fecha blocos com `fim` para manter o parser simples e os erros localizáveis.

```hzhon
var nome = "Ada"
fixo limite = 10
var ativo = verdadeiro
var itens = ["um", "dois", "três"]
```

Os tipos primitivos são `Inteiro`, `Decimal`, `Texto`, `Booleano` e `Nulo`. Os tipos compostos são `Lista<T>`, `Mapa<K, V>`, `Tupla`, `Conjunto` e `Registro`. A inferência é o padrão; uma anotação explícita usa dois-pontos: `var idade: Inteiro = 32`.

Operadores aritméticos são `+`, `-`, `*`, `/` e `%`. Comparações são `==`, `!=`, `<`, `<=`, `>` e `>=`. Operadores lógicos são `e`, `ou` e `nao`. A concatenação usa `+`; interpolação usa texto com chaves: `"Olá, {nome}"`. Coalescência nula será escrita `valor ?? substituto` e o ternário será `condicao ? quando_verdadeiro : quando_falso`.

Comentários de linha começam com `#`. Comentários de bloco usam `/*` e `*/`. Comentários de documentação começam com `##` e podem alimentar o gerador de documentação.

### EBNF simplificada

```ebnf
programa       = { declaracao } ;
declaracao     = variavel | funcao | condicional | enquanto | para_cada | retorno | expressao ;
variavel       = ("var" | "fixo") identificador [ ":" tipo ] [ "=" expressao ] ;
funcao         = "funcao" identificador "(" [ parametros ] ")" bloco "fim" ;
condicional    = "se" expressao bloco { "senao_se" expressao bloco } [ "senao" bloco ] "fim" ;
enquanto       = "enquanto" expressao bloco "fim" ;
para_cada      = "para_cada" identificador "em" expressao bloco "fim" ;
bloco          = { declaracao } ;
expressao      = atribuicao ;
atribuicao     = logico [ "=" atribuicao ] ;
logico         = comparacao { ("e" | "ou") comparacao } ;
chamada        = primario { "(" argumentos ")" | "[" expressao "]" } ;
primario       = literal | identificador | lista | "(" expressao ")" ;
```

## 3. Estruturas de controle

O alpha executável suporta `se`, `senao_se`, `senao`, `enquanto`, `para_cada`, `pare`, `continue` e `retorne`.

```hzhon
para_cada item em itens
    se item == "fim"
        pare
    senao
        imprimir item
    fim
fim
```

A forma `escolha` será adicionada na alpha estendida:

```hzhon
escolha status
    caso 200
        imprimir "ok"
    caso 404
        imprimir "não encontrado"
    padrao
        imprimir "outro status"
fim
```

Pattern matching usará `combine`, com literais, desestruturação de listas e guardas. O compilador deverá rejeitar padrões impossíveis quando a análise de tipos estiver ativada.

## 4. Funções

Funções são valores de primeira classe. O alpha inicial usa parâmetros posicionais; parâmetros padrão, nomeados e variádicos entram na alpha estendida.

```hzhon
funcao aplicar(valor, transformacao)
    retorne transformacao(valor)
fim

var dobrar = funcao(numero) numero * 2 fim
imprimir aplicar(4, dobrar)
```

A forma abreviada planejada é `dobrar = (numero) => numero * 2`. Closures capturam o ambiente léxico. Funções puras poderão receber a anotação `@pura`; a anotação é uma promessa verificada pelo linter, não uma permissão para o runtime quebrar código legítimo.

## 5. Orientação a objetos

A alpha define o modelo, mas não o torna obrigatório. Classes usam `classe`, atributos, `construtor` e `metodo`. Visibilidade pode ser `publico`, `privado` ou `protegido`. Herança usa `herda_de`; contratos usam `implementa`.

```hzhon
classe Pessoa
    privado nome

    construtor(nome)
        isto.nome = nome
    fim

    metodo apresentar()
        retorne "Meu nome é {isto.nome}"
    fim
fim
```

Classes abstratas, sobrescrita, métodos estáticos e propriedades computadas serão estabilizados antes da versão 1.0. A recomendação de design é preferir composição e traits a hierarquias profundas.

## 6. Programação funcional

A biblioteca padrão oferecerá `mapeie`, `filtre`, `reduza`, `ordene` e `compor`. Listas poderão ser imutáveis quando declaradas com `fixo`; estruturas persistentes ficam previstas para a biblioteca `colecoes`.

```hzhon
var pares = numeros
    |> filtre((n) => n % 2 == 0)
    |> mapeie((n) => n * 2)
```

O operador de pipeline é uma proposta alpha e só será aceito quando o parser produzir mensagens claras para erros de precedência.

## 7. Tratamento de erros

Exceções usam `tente`, `capture` e `finalmente`. Erros customizados são classes que herdam de `Erro`. Para código de domínio, `Resultado<Valor, Erro>` é preferível a exceções silenciosas.

```hzhon
tente
    var dados = ler_json("config.json")
capture erro
    imprimir "Não foi possível ler: " + erro.mensagem
finalmente
    imprimir "fim da operação"
fim
```

Toda mensagem deve informar linha, coluna, causa provável e uma sugestão. O compilador pode emitir avisos para variáveis sem uso, conversões implícitas ambíguas, sombra de nomes e captura genérica demais.

## 8. Assincronismo e concorrência

A proposta é um event loop cooperativo com tarefas leves. `assincrono` declara uma função que retorna `Promessa<T>`; `espere` suspende a tarefa sem bloquear o processo. Canais tipados permitem comunicação entre tarefas.

```hzhon
assincrono funcao buscar(url: Texto) -> Texto
    retorne espere http.obter(url).texto()
fim
```

Cancelamento usa um `SinalCancelamento` explícito. Toda API de rede deve aceitar timeout. Threads nativas ficam reservadas para tarefas de CPU e serão expostas depois de o runtime ter métricas de segurança.

## 9. Módulos e ecossistema

Importações usam `importar`, `exportar` e a forma `de "arquivo" importar nome`. O manifesto se chama `pacote.config`.

```toml
nome = "minha-api"
versao = "0.1.0"
entrada = "src/principal.hz"

[permissoes]
rede = true
arquivos = ["dados/"]
```

A CLI proposta é `hz iniciar`, `hz executar`, `hz testar`, `hz formatar`, `hz instalar`, `hz publicar` e `hz docs`. O repositório central provisório se chama **Hzhub**. A estrutura recomendada é `src/`, `testes/`, `docs/` e `bibliotecas/`.

A biblioteca padrão cobrirá texto, matemática, data/hora, arquivos, rede, JSON, expressões regulares, processos e coleções.

## 10. Sistema de tipos

Hzhon terá tipagem gradual. O código sem anotações usa inferência; o código anotado recebe verificação na compilação. Tipos genéricos usam `Lista<Texto>` e `Mapa<Texto, Numero>`. Aliases usam `tipo Idade = Numero`. Uniões usam `Numero ou Texto`; opcionais usam `Texto?`.

O alpha deve tratar `nulo` explicitamente quando o tipo não for anulável. A meta é emitir erros de tipo antes da execução sem exigir que iniciantes escrevam tipos em cada linha.

## 11. Performance e execução

A implementação de referência da alpha é um interpretador de AST escrito em Python. A arquitetura é lexer, parser, AST, análise semântica e runtime. O beta adicionará bytecode e uma VM pequena. Um JIT só será considerado depois de benchmarks reproduzíveis.

A coleta de lixo da implementação de referência é delegada ao runtime hospedeiro. A VM futura usará GC geracional. Otimizações previstas incluem eliminação de código morto, especialização de chamadas e inlining de funções pequenas.

Comparações de desempenho serão publicadas somente com metodologia, hardware, versão e carga especificados. A alpha não promete ser mais rápida que Python, Node.js ou Luau.

## 12. Segurança

O runtime deve evitar acesso direto à memória. Conversões numéricas devem detectar overflow quando o tipo exigir. Bibliotecas de rede, processos e arquivos ficam atrás de permissões declaradas no manifesto. Código de terceiros poderá ser executado em sandbox com limites de tempo, memória e chamadas.

A linguagem não elimina vulnerabilidades de aplicação. Ela fornece APIs que tornam validação, escaping e serialização explícitos.

## 13. Interoperabilidade

A versão 1.0 terá FFI para C e bindings gerados para Python e JavaScript. A compilação para WebAssembly será um alvo de biblioteca padrão, não uma promessa de que todas as APIs do sistema funcionarão no navegador.

A integração com Python começará com processos e módulos nativos; a integração com JavaScript usará bindings do runtime. O sentido inverso será feito por uma ABI documentada.

## 14. Ferramentas

O ecossistema oficial inclui `hz fmt` para formatação determinística, `hz lint` para mensagens em português, `hz debug` para breakpoints, inspeção e execução passo a passo, extensão VS Code, snippets, REPL e gerador de documentação.

O framework de testes usa `descreva`, `teste` e `afirme`:

```hzhon
descreva "soma"
    teste "soma dois números"
        afirme soma(2, 3) == 5
    fim
fim
```

## 15. Exemplos práticos

### Olá, mundo

```hzhon
imprimir "Olá, mundo!"
```

### CRUD em memória

```hzhon
var usuarios = []
funcao cadastrar(nome)
    usuarios.adicionar({ nome: nome })
    retorne tamanho(usuarios)
fim
```

### Servidor web

```hzhon
servidor = web.servidor()
servidor.rota("GET", "/", funcao(requisicao)
    retorne web.resposta("Hzhon está online")
fim)
servidor.iniciar(8080)
```

### JSON e arquivos

```hzhon
var texto = arquivos.ler("dados.json")
var dados = json.ler(texto)
imprimir dados["nome"]
```

### Teste

```hzhon
teste "texto converte número"
    afirme texto(42) == "42"
fim
```

Cada exemplo será publicado lado a lado com Python e JavaScript no portal de documentação, com contagem de linhas e observações sobre semântica, não apenas sobre tamanho.

### DSL web da alpha

A alpha já inclui uma DSL declarativa para páginas. O autor descreve `site`, `tema`, `pagina`, `cabecalho`, `secao`, `cartao`, `titulo`, `subtitulo`, `texto`, `botao`, `codigo` e `rodape`. O comando `hzhon construir arquivo.hz --saida dist` gera uma página HTML autocontida com CSS responsivo. O autor não precisa escrever HTML para usar o fluxo básico.

O gerador é deliberadamente pequeno: ele produz páginas estáticas e não substitui ainda um framework de componentes ou um servidor de aplicação. A próxima etapa é permitir dados, templates, rotas múltiplas, formulários e, depois, `hzhon servidor` para APIs escritas na linguagem.

## 16. Variante para Luau

A variante **Hzhon-Luau** transpila o subconjunto suportado para Luau válido. Variáveis tornam-se `local`; funções tornam-se `local function`; módulos tornam-se `ModuleScript` com `require`; classes usam tabelas e `__index`; herança encadeia metatables; tarefas usam `task.spawn`, `task.wait` e coroutines.

A variante reconhecerá `atributo`, `colecao`, `data_store`, `evento_remoto` e `servidor` como APIs de domínio, mas manterá a diferença entre cliente e servidor explícita. O gerador produzirá `--!strict` quando as anotações forem suficientes.

Rojo será suportado como fluxo de sincronização. Source maps guardarão a relação entre cada linha `.hz` e o trecho Luau gerado, permitindo que erros do Studio apontem de volta para o código original. DataStores exigirão chamadas no servidor e tratamento de falhas. RemoteEvents terão tipos e validações geradas para reduzir confiança indevida no cliente.

## 17. Roadmap e versionamento

- **0.1 experimental:** interpretador, variáveis, funções, listas, controle de fluxo e exemplos.
- **0.2 alpha:** mapas, tipos opcionais, `escolha`, erros estruturados, REPL e módulos locais.
- **0.5 beta:** bytecode, biblioteca padrão, testes, formatador, linter e extensão VS Code.
- **1.0 estável:** especificação congelada, pacotes, FFI, WebAssembly, documentação completa e política de compatibilidade.

Mudanças incompatíveis exigirão RFC, nota de migração e ferramenta de atualização. A licença proposta é MIT. O código será governado por mantenedores, um conselho técnico e RFCs públicas.

## 18. Metaprogramação, macros e anotações

Anotações como `@teste`, `@obsoleto` e `@exporta` fornecem metadados ao compilador e às ferramentas. Macros, se aprovadas, operarão sobre uma AST restrita em tempo de compilação. Elas não poderão acessar rede, relógio ou arquivos sem uma permissão explícita.

Reflexão permitirá consultar tipos, métodos e interfaces. Serialização automática será baseada em anotações e recusará campos não declarados por padrão.

## 19. Interfaces e multiplataforma

A visão de produto inclui a biblioteca `interface`, com janelas, botões e formulários, e uma camada reativa para web. Desktop usará um backend nativo; mobile e WebAssembly terão adaptadores. A linguagem não promete que um único layout será perfeito em todas as telas; promete compartilhar lógica e modelos.

Um app de tarefas servirá de exemplo oficial em desktop, mobile e web, usando o mesmo domínio e adaptadores de interface.

## 20. Persistência e bancos

O módulo `banco` terá drivers SQL e NoSQL. O ORM usará `modelo`, `consulta`, `onde`, `ordene_por`, migrações versionadas e parâmetros preparados.

```hzhon
modelo Usuario
    campo id: Id
    campo nome: Texto
fim

var ativos = Usuario.consulta().onde(ativo == verdadeiro).ordene_por(nome).lista()
```

Nenhuma string interpolada deve virar SQL sem parametrização. Migrações serão arquivos versionados, revisáveis e reversíveis quando possível.

## 21. Observabilidade

A biblioteca `log` terá níveis `info`, `aviso`, `erro` e `depurar`, com saída estruturada. O profiler medirá tempo e memória por função. Tracing distribuído usará IDs de correlação e exportadores compatíveis com OpenTelemetry. Métricas poderão ser expostas em formato Prometheus.

## 22. Comunidade, governança e cultura

O projeto manterá repositório Git, fórum, Discord e portal de documentação. O código de conduta deverá proteger iniciantes, pessoas lusófonas e colaboradores de origens diversas. Toda contribuição passará por revisão e checagem automatizada.

RFCs devem descrever problema, proposta, alternativas, impacto na aprendizagem, compatibilidade, implementação e plano de teste. O fundador pode iniciar o projeto, mas decisões de linguagem devem migrar para o conselho técnico conforme a comunidade crescer.

## 23. Casos de uso

Web e APIs usarão `web`, `http`, `json` e `banco`. Jogos usarão Hzhon-Luau. Automação usará arquivos, processos e agendamento. Ciência de dados terá tabelas e adaptadores para formatos comuns. IoT usará um runtime reduzido e permissões de hardware.

O material de lançamento deve conter um exemplo curto para cada setor, sem alegar que a alpha já possui todas as bibliotecas necessárias para produção.

## 24. Acessibilidade

Erros e tutoriais devem explicar termos técnicos na primeira ocorrência. A CLI terá saída compatível com leitores de tela, sem depender apenas de cor ou posição. O tutorial no navegador deverá oferecer foco por teclado, contraste suficiente, navegação por headings, cópia de código e redução de movimento.

## 25. Casos extremos e suporte ao português

O runtime deve definir o que ocorre com números grandes, divisão por zero, recursão sem fim, listas gigantes, emojis e caracteres combinados. Números inteiros devem ter comportamento documentado; recursão excedida deve produzir um erro recuperável com linha de origem.

Identificadores podem conter `ç`, `ã`, `é`, `ô` e demais caracteres Unicode válidos. A normalização recomendada é NFC. O compilador deve alertar sobre identificadores visualmente ambíguos e sobre colisões de normalização. Comportamento indefinido deve ser raro, documentado e acompanhado de aviso quando detectável.

## 26. Palavras-chave da alpha

| Hzhon | Papel | Equivalente aproximado |
|---|---|---|
| `var` | variável mutável | `let` / variável |
| `fixo` | constante | `const` |
| `se` | condicional | `if` |
| `senao_se` | ramo condicional | `elif` / `else if` |
| `senao` | ramo alternativo | `else` |
| `enquanto` | laço condicional | `while` |
| `para_cada` | iteração | `for ... in` |
| `em` | fonte da iteração | `in` |
| `pare` | interromper laço | `break` |
| `continue` | pular iteração | `continue` |
| `funcao` | declarar função | `def` / `function` |
| `retorne` | retornar valor | `return` |
| `classe` | declarar classe | `class` |
| `herda_de` | herança | `extends` |
| `implementa` | contrato | `implements` |
| `tente` | iniciar tratamento | `try` |
| `capture` | capturar erro | `except` / `catch` |
| `finalmente` | execução garantida | `finally` |
| `assincrono` | função assíncrona | `async` |
| `espere` | aguardar promessa | `await` |
| `importar` | importar módulo | `import` |
| `exportar` | exportar símbolo | `export` |
| `verdadeiro` | booleano verdadeiro | `True` / `true` |
| `falso` | booleano falso | `False` / `false` |
| `nulo` | ausência de valor | `None` / `null` |
| `e` | conjunção lógica | `and` / `&&` |
| `ou` | disjunção lógica | `or` / `||` |
| `nao` | negação lógica | `not` / `!` |

## Critérios de aceite da alpha

A alpha será considerada pronta quando uma pessoa conseguir instalar o runtime, executar um programa de exemplo, receber uma mensagem de erro compreensível, escrever uma função, trabalhar com uma coleção, importar um módulo local, rodar testes e encontrar a documentação correspondente sem depender de conhecimento prévio de inglês.

A versão atual já cumpre o núcleo executável de variáveis, constantes, funções, listas, condicionais, laços, operadores, comentários e runtime nativo. Os demais itens desta especificação são o contrato de evolução, não uma alegação de que todos já estão implementados.

## Referências

[1]: https://peps.python.org/pep-0008/ "PEP 8 — Style Guide for Python Code"

[2]: https://luau.org/ "Luau — linguagem de programação e documentação oficial"

[3]: https://webassembly.org/ "WebAssembly — documentação e visão geral"
