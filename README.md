# Hzhon

**Hzhon é uma linguagem de programação em português para aprender, criar e compartilhar software.**

Este repositório reúne o site oficial da linguagem e a implementação beta. A proposta é transformar ideias escritas em português em programas executáveis, sites, automações e projetos Luau/Roblox.

## O que existe aqui

- **Site oficial:** aplicação Vite + React na raiz do repositório.
- **Site compilado:** a pasta `site/` já pode ser servida sem Node.js, usando a CLI Hzhon.
- **Playground:** editor interativo com exemplos Hzhon dentro do site.
- **DSL web beta:** descreva páginas, seções, cartões e formulários em `.hz` sem escrever HTML diretamente.
- **DSL de jogos:** crie jogos 2D com Canvas usando arquivos `.jogo.hz`; a CLI gera uma página jogável para abrir no navegador.
- **CLI Hzhon:** criar projetos, executar programas, construir sites, formatar arquivos, rodar testes e servir a pasta `dist`.
- **Runtime 0.7 beta:** interpretador com variáveis, constantes, funções, listas, mapas, propriedades, módulos locais, tratamento de erros, REPL e funções nativas.
- **Hzhon-Luau beta:** transpiler com alvos `server`, `local` e `module`, RemoteEvents, RemoteFunctions, eventos cliente, ModuleScripts, Attributes e DataStores.
- **Documentação:** especificação técnica e roadmap em `linguagem/ESPECIFICACAO_ALPHA.md`.

## Site oficial

O site é o projeto da raiz. Para executar localmente:

```bash
pnpm install
pnpm dev
```

Para gerar a versão de produção:

```bash
pnpm build
```

Também existe uma versão pronta em `site/`. Para servi-la sem instalar Node.js:

```bash
cd linguagem
python3 hzhon_cli.py servir ../site --porta 8080
```

O projeto já possui `vercel.json` configurado para Vercel com Vite. No Vercel, importe este repositório, mantenha o framework como **Vite** e publique.

## Usar a linguagem

Entre na implementação:

```bash
cd linguagem
python3 hzhon_cli.py --help
python3 hzhon_cli.py versao
python3 hzhon_cli.py diagnostico
python3 -m unittest -v
```

O runtime não usa bibliotecas externas e funciona com Python 3.10 ou mais recente.
Isso permite usar a Hzhon em Termux, Linux, macOS e Windows.

### Instalação em Termux, Linux e macOS

```bash
cd linguagem
bash instalar-termux.sh
hzhon --help
```

O instalador detecta `python3` ou `python`, usa `$PREFIX/bin` no Termux e
`$HOME/.local/bin` em Linux/macOS. Se o comando não entrar no PATH, ele mostra
a linha necessária.

No Windows PowerShell:

```powershell
cd linguagem
Set-ExecutionPolicy -Scope Process Bypass
.\instalar.ps1
```

Criar um site com Hzhon:

```bash
python3 hzhon_cli.py novo site meu-site
cd meu-site
python3 ../hzhon_cli.py construir site.hz --saida dist
python3 ../hzhon_cli.py servir dist --porta 8080
```

No Termux, use o instalador:

```bash
cd ~/storage/downloads/Hzhon/linguagem
bash instalar-termux.sh
hzhon --help
```

Criar um projeto Roblox com exemplos de servidor, cliente e módulo:

```bash
hzhon novo roblox meu-jogo
```

Criar um projeto comum:

```bash
hzhon novo projeto meu-app
hzhon verificar meu-app/src/main.hz
hzhon executar meu-app/src/main.hz
```

## Exemplo Hzhon

```hzhon
site "Meu primeiro site"
tema "escuro"
pagina inicio "/"
    cabecalho "HZHON"
        titulo "Um site escrito em português."
        subtitulo "A linguagem gera a página final para você."
        botao "Conhecer" "#recursos"
    fim
    secao "Recursos"
        cartao "Simples"
            texto "Blocos claros para construir experiências web."
        fim
    fim
fim
fim
```

A Hzhon 0.7 também aceita mapas, módulos e tratamento de erros:

```hzhon
importe "util.hz"

var jogador = {
    nome: "Ana",
    nivel: 10
}

tente
    lance "exemplo de erro"
capture erro
    imprimir "Falha: " + erro
fim
```

O REPL pode ser aberto com `hzhon repl`.

## Criar jogos no navegador

Você escreve Hzhon; a CLI gera o Canvas e o código de navegador por baixo. Não é preciso escrever HTML ou JavaScript:

```bash
hzhon jogo exemplo-jogo.jogo.hz --saida meu-jogo
hzhon servir meu-jogo --porta 8080
```

O formato beta inclui tela, fundo, jogador, inimigos que patrulham, plataformas, objetivo, gravidade, colisão, teclado e controles de toque no celular. O resultado é um `index.html` autocontido dentro da pasta de saída; HTML e JavaScript são detalhes gerados automaticamente.

## Roadmap

A evolução planejada inclui JSON, requisições HTTP, servidor de APIs, pacotes,
tipagem gradual, bytecode, biblioteca padrão, ferramentas de editor e a
integração Rojo para Hzhon-Luau. Mapas, módulos locais, REPL e erros estruturados
já fazem parte da beta 0.7.

## Licença

MIT. A Hzhon é um projeto aberto e experimental.
