import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from hzhon_cli import construir_jogo, construir_site, main


class TesteCLIWeb(unittest.TestCase):
    def test_gera_formulario_e_pagina(self):
        fonte = '''site "Teste"\ntema "escuro"\npagina inicio "/"\n    titulo "Olá"\n    formulario "Contato" "/contato"\n        campo "email" "E-mail" "email"\n    fim\nfim\nfim\n'''
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            entrada = raiz / "site.hz"
            saida = raiz / "dist"
            entrada.write_text(fonte, encoding="utf-8")
            arquivos = construir_site(entrada, saida)
            html = arquivos[0].read_text(encoding="utf-8")
            self.assertIn("<title>Teste</title>", html)
            self.assertIn('name="email"', html)
            self.assertIn('type="email"', html)

    def test_versao_e_diagnostico(self):
        versao = StringIO()
        with redirect_stdout(versao):
            self.assertEqual(main(["versao"]), 0)
        self.assertIn("Hzhon 0.7.0 beta", versao.getvalue())

        diagnostico = StringIO()
        with redirect_stdout(diagnostico):
            self.assertEqual(main(["diagnostico"]), 0)
        self.assertIn("OK runtime", diagnostico.getvalue())

    def test_gera_jogo_canvas(self):
        linhas = [
            'jogo "Teste"',
            'tela 640 360',
            'fundo "#000000"',
            'jogador heroi 20 20 24 "#ffffff"',
            'plataforma 0 320 640 40 "#333333"',
            'objetivo 580 280 24 "#ffcc00"',
            'fim',
        ]
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            entrada = raiz / "teste.jogo.hz"
            entrada.write_text("\n".join(linhas) + "\n", encoding="utf-8")
            html = construir_jogo(entrada, raiz / "dist").read_text(encoding="utf-8")
            self.assertIn('<canvas id="jogo"', html)
            self.assertIn("requestAnimationFrame(atualizar)", html)
            self.assertIn("Teste", html)


if __name__ == "__main__":
    unittest.main()
