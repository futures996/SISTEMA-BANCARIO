# SISTEMA-BANCARIO
CRIANDO UM SISTEMA BANCARIO
lass Conta:
    def _init_(self, numero, titular, saldo=0):
        self.numero = numero
        self.titular = titular
        self.saldo = saldo
        self.transacoes = []  # Lista para registrar operações

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.transacoes.append(('Depósito', valor))
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            return True
        else:
            print("Valor inválido para depósito.")
            return False

    def sacar(self, valor):
        if valor <= 0:
            print("Valor inválido para saque.")
            return False
        if valor > self.saldo:
            print("Saldo insuficiente.")
            return False
        self.saldo -= valor
        self.transacoes.append(('Saque', valor))
        print(f"Saque de R$ {valor:.2f} realizado com sucesso.")
        return True

    def transferir(self, valor, conta_destino):
        if self.sacar(valor):  # Se o saque for bem-sucedido, prossegue com o depósito
            conta_destino.depositar(valor)
            self.transacoes.append(('Transferência', valor, conta_destino.numero))
            print(f"Transferência de R$ {valor:.2f} para a conta {conta_destino.numero} realizada com sucesso.")
            return True
        return False

    def extrato(self):
        print(f"\nExtrato da conta {self.numero} - Titular: {self.titular}")
        print(f"Saldo Atual: R$ {self.saldo:.2f}")
        if not self.transacoes:
            print("Nenhuma transação realizada.")
        else:
            for operacao in self.transacoes:
                print(operacao)


class Banco:
    def _init_(self):
        self.contas = {}

    def criar_conta(self, numero, titular, saldo_inicial=0):
        if numero in self.contas:
            print("Conta já existente!")
            return None
        conta = Conta(numero, titular, saldo_inicial)
        self.contas[numero] = conta
        print("Conta criada com sucesso!")
        return conta

    def buscar_conta(self, numero):
        return self.contas.get(numero, None)

    def operar(self):
        while True:
            print("\n--- Menu do Banco ---")
            print("1 - Criar Conta")
            print("2 - Depositar")
            print("3 - Sacar")
            print("4 - Transferir")
            print("5 - Extrato")
            print("6 - Sair")
            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                numero = input("Digite o número da conta: ")
                titular = input("Digite o nome do titular: ")
                try:
                    saldo = float(input("Digite o saldo inicial: "))
                except ValueError:
                    print("Saldo inválido, iniciando com R$ 0.00")
                    saldo = 0
                self.criar_conta(numero, titular, saldo)

            elif opcao == "2":
                numero = input("Digite o número da conta: ")
                conta = self.buscar_conta(numero)
                if conta:
                    try:
                        valor = float(input("Digite o valor para depósito: "))
                    except ValueError:
                        print("Valor inválido.")
                        continue
                    conta.depositar(valor)
                else:
                    print("Conta não encontrada.")

            elif opcao == "3":
                numero = input("Digite o número da conta: ")
                conta = self.buscar_conta(numero)
                if conta:
                    try:
                        valor = float(input("Digite o valor para saque: "))
                    except ValueError:
                        print("Valor inválido.")
                        continue
                    conta.sacar(valor)
 …
