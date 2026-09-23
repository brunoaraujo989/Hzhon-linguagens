# Site pronto da Hzhon

Esta pasta contém a versão já compilada do site oficial e do playground.
Ela pode ser aberta por qualquer servidor HTTP estático.

Sem instalar Node.js:

```bash
cd ../linguagem
python3 hzhon_cli.py servir ../site --porta 8080
```

Depois abra `http://localhost:8080`.

Para alterar o site, use os arquivos-fonte em `../client/`, instale as
dependências com pnpm e execute `pnpm dev` ou `pnpm build`.