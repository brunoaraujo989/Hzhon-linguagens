import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from hzhon import HzhonErro, executar_fonte


class TesteHzhon(unittest.TestCase):
    def rodar(self, fonte):
        saida = io.StringIO()
        with redirect_stdout(saida):
            executar_fonte(fonte)
        return saida.getvalue().strip().splitlines()

    def test_variaveis_e_operadores(self):
        self.assertEqual(self.rodar('var x = 2 + 3 * 4\nimprimir x'), ['14'])

    def test_funcao_e_retorno(self):
        fonte = 'funcao dobro(x)\n retorne x * 2\nfim\nimprimir dobro(9)'
        self.assertEqual(self.rodar(fonte), ['18'])

    def test_lista_e_para_cada(self):
        fonte = 'var total = 0\npara_cada x em [1, 2, 3]\n total = total + x\nfim\nimprimir total'
        self.assertEqual(self.rodar(fonte), ['6'])

    def test_constante_nao_muda(self):
        with self.assertRaises(HzhonErro):
            executar_fonte('fixo x = 1\nx = 2')

    def test_condicional_e_enquanto(self):
        fonte = 'var i = 0\nenquanto i < 2\n imprimir i\n i = i + 1\nfim'
        self.assertEqual(self.rodar(fonte), ['0', '1'])

    def test_mapas_propriedades_e_nativas(self):
        fonte = '''var pessoa = {
    nome: "Ana",
    idade: 22
}
pessoa.idade = pessoa.idade + 1
imprimir pessoa.nome
imprimir pessoa.idade
imprimir tipo(pessoa)
imprimir tamanho(pessoa)
'''
        self.assertEqual(self.rodar(fonte), ["Ana", "23", "mapa", "2"])

    def test_tratamento_de_erros(self):
        fonte = '''tente
    lance "arquivo inválido"
capture problema
    imprimir problema
fim
'''
        self.assertEqual(self.rodar(fonte), ["arquivo inválido"])

    def test_importa_modulo_local(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            (raiz / "util.hz").write_text(
                "funcao dobro(valor)\n    retorne valor * 2\nfim\n",
                encoding="utf-8",
            )
            principal = raiz / "main.hz"
            principal.write_text(
                'importe "util.hz"\nimprimir dobro(7)\n',
                encoding="utf-8",
            )
            # O caminho também é exercitado para garantir resolução relativa.
            saida = io.StringIO()
            with redirect_stdout(saida):
                executar_fonte(principal.read_text(encoding="utf-8"), principal)
            self.assertEqual(saida.getvalue().strip(), "14")


if __name__ == '__main__':
    unittest.main()
