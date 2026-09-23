import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from hzhon_cli import construir_site, main


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


if __name__ == "__main__":
    unittest.main()
