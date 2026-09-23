import tempfile
import unittest
from pathlib import Path

from hzhon_cli import construir_site


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


if __name__ == "__main__":
    unittest.main()
