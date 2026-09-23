import unittest

from hzhon_luau import LuauErro, transpilar


class TesteLuauBeta(unittest.TestCase):
    def test_remote_e_datastore(self):
        fonte = '''servico replicado como Replicado
servico dados como Dados
evento_remoto Atualizar em Replicado
abrir_dados Banco como "TesteV1"
receber Atualizar com funcao(jogador, valor)
 salvar Banco chave texto(jogador.UserId) valor valor
 enviar Atualizar para jogador com valor
fim
'''
        luau = transpilar(fonte, alvo="server")
        self.assertIn('WaitForChild("Atualizar")', luau)
        self.assertIn('GetDataStore("TesteV1")', luau)
        self.assertIn('OnServerEvent:Connect(function(jogador, valor)', luau)
        self.assertIn(':SetAsync(tostring(jogador.UserId), valor)', luau)
        self.assertIn(':FireClient(jogador, valor)', luau)

    def test_module_script(self):
        fonte = '''modulo Inventario
funcao criar()
 retorne {}
fim
exportar criar
fim
'''
        luau = transpilar(fonte, alvo="module")
        self.assertIn('local Inventario = {}', luau)
        self.assertIn('Inventario.criar = criar', luau)
        self.assertIn('return Inventario', luau)

    def test_alvo_invalido(self):
        with self.assertRaises(LuauErro):
            transpilar('imprimir "x"', alvo="desktop")


if __name__ == "__main__":
    unittest.main()
