import io
import unittest
from contextlib import redirect_stdout

from hzhon import executar_fonte, HzhonErro


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


if __name__ == '__main__':
    unittest.main()
