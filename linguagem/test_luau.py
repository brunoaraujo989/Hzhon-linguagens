import unittest

from hzhon_luau import LuauErro, transpilar


class TesteLuau(unittest.TestCase):
    def test_funcoes_e_controle(self):
        fonte = 'funcao dobro(x)\n retorne x * 2\nfim\nvar numero = dobro(4)\nimprimir numero'
        luau = transpilar(fonte)
        self.assertIn('local function dobro(x)', luau)
        self.assertIn('return x * 2', luau)
        self.assertIn('local numero = dobro(4)', luau)

    def test_servico_evento_atributo(self):
        fonte = 'servico jogadores como Jogadores\natributo Jogadores, "Nome", "Hzhon"\nouvir Jogadores.PlayerAdded com funcao(jogador)\n imprimir jogador.Name\nfim'
        luau = transpilar(fonte)
        self.assertIn('game:GetService("Players")', luau)
        self.assertIn('Jogadores:SetAttribute("Nome", "Hzhon")', luau)
        self.assertIn('Jogadores.PlayerAdded:Connect(function(jogador)', luau)
        self.assertIn('end --#hzhon-linha', luau)

    def test_bloco_nao_fechado(self):
        with self.assertRaises(LuauErro):
            transpilar('se verdadeiro\n imprimir "x"')


if __name__ == "__main__":
    unittest.main()
