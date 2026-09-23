GUIA DE USO DE IA COM A HZHON
==============================

Este arquivo explica como usar ferramentas de inteligencia artificial para aprender e criar projetos com a Hzhon.

1. O que a IA pode fazer

A IA pode ajudar a:
- explicar a sintaxe Hzhon em portugues;
- criar exemplos de programas .hz;
- transformar uma ideia em um site Hzhon;
- criar scripts Hzhon-Luau para Roblox;
- revisar erros de sintaxe;
- sugerir funcoes, modulos, RemoteEvents e sistemas de inventario;
- explicar o codigo Luau gerado.

2. Como pedir ajuda

Seja especifico no pedido. Informe:
- o que voce quer construir;
- se o arquivo sera para server, local ou module;
- onde o codigo sera usado no Roblox;
- qual erro apareceu;
- o trecho de codigo relevante.

Exemplo de pedido:

"Crie um LocalScript Hzhon-Luau que detecte quando o jogador apertar E e envie um RemoteEvent chamado AbrirMenu. Explique onde colocar o arquivo no Roblox Studio."

3. Fluxo recomendado

1. Peça a primeira versao para a IA.
2. Salve o resultado em um arquivo .hz.
3. Gere o Luau:

   python3 hzhon_cli.py luau meu-script.roblox.hz --alvo local -o MeuScript.client.luau

4. Leia o codigo gerado antes de colar no Roblox Studio.
5. Teste em uma experiencia privada.
6. Corrija e versiona o arquivo .hz, nao somente o Luau gerado.

4. Seguranca

Nunca envie para uma IA:
- tokens, chaves de API ou senhas;
- cookies de conta;
- credenciais do Roblox;
- dados pessoais de jogadores;
- chaves ou permissoes de producao.

A IA pode errar. Nao copie automaticamente codigo que acessa DataStore, dinheiro do jogo, inventarios, RemoteEvents ou permissoes administrativas. Valide os dados no servidor e nunca confie em valores enviados pelo cliente.

5. Roblox e cliente/servidor

Use Script no servidor para regras importantes, persistencia, inventario e autoridade do jogo. Use LocalScript para interface, entrada do jogador e efeitos locais. Use ModuleScript para codigo compartilhado. RemoteEvents devem validar no servidor tudo que chega do cliente.

6. Hzhon e codigo gerado

A Hzhon beta gera Luau, mas a geracao nao substitui os testes no Roblox Studio. O arquivo .luau deve ser revisado, principalmente quando usa DataStoreService, RemoteEvents, compras, teleporte ou dados de jogadores.

7. Exemplo de pedido de revisao

"Revise este arquivo Hzhon-Luau como um programador Roblox. Procure vulnerabilidades cliente-servidor, chamadas inseguras de DataStore e erros de tipo. Nao invente APIs; explique cada correcao."

A IA deve ser usada como assistente de aprendizado e revisao. A decisao final sobre publicar e executar o codigo e sempre do desenvolvedor.
