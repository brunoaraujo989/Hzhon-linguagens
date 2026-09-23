# Hzhon

**Hzhon é uma linguagem de programação em português para aprender, criar e compartilhar software.**

Este repositório reúne o site oficial da linguagem e a implementação alpha. A proposta é transformar ideias escritas em português em programas executáveis, sites, automações e, futuramente, projetos Luau/Roblox.

## O que existe aqui

- **Site oficial:** aplicação Vite + React na raiz do repositório.
- **Playground:** editor interativo com exemplos Hzhon dentro do site.
- **DSL web alpha:** descreva páginas, seções, cartões e formulários em `.hz` sem escrever HTML diretamente.
- **CLI Hzhon:** criar projetos, executar programas, construir sites, formatar arquivos, rodar testes e servir a pasta `dist`.
- **Runtime:** interpretador inicial com variáveis, constantes, funções, listas, condicionais, laços, operadores e funções nativas.
- **Hzhon-Luau beta:** transpiler com alvos `server`, `local` e `module`, RemoteEvents, ModuleScripts, Attributes e DataStores.
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

O projeto já possui `vercel.json` configurado para Vercel com Vite. No Vercel, importe este repositório, mantenha o framework como **Vite** e publique.

## Usar a linguagem

Entre na implementação:

```bash
cd linguagem
python3 hzhon_cli.py --help
python3 -m unittest -v
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

## Roadmap

A evolução planejada inclui mapas e JSON, requisições HTTP, servidor de APIs, módulos e pacotes, tipagem gradual, bytecode, REPL, biblioteca padrão, ferramentas de editor e a integração Rojo para Hzhon-Luau.

## Licença

MIT. A Hzhon é um projeto aberto e experimental.
