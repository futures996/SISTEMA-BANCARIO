# Sistema Bancário

Um projeto simples em Python para simular operações básicas de um banco, com foco em conceitos de programação orientada a objetos.

## Sobre o projeto

Este sistema permite:

- criar contas bancárias;
- realizar depósitos;
- realizar saques;
- transferir valores entre contas;
- consultar o extrato;
- interagir por meio de um menu no terminal.

## Funcionalidades

- Cadastro de clientes com número da conta e titular;
- Validação de saldo para saque;
- Registro de transações;
- Transferência entre contas;
- Extrato com histórico de operações;
- Interface simples em linha de comando.

## Requisitos

- Python 3.10 ou superior

## Como executar

1. Salve o código em um arquivo chamado `banco.py`.
2. Execute o programa no terminal:

```bash
python banco.py
```

## Exemplo de implementação

```python
class Conta:
    def __init__(self, numero, titular, saldo=0):
        self.numero = numero
        self.titular = titular
        self.saldo = saldo
        self.transacoes = []

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.transacoes.append(('Depósito', valor))
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            return True
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
        if self.sacar(valor):
            conta_destino.depositar(valor)
            self.transacoes.append(('Transferência', valor, conta_destino.numero))
            print(
                f"Transferência de R$ {valor:.2f} para a conta "
                f"{conta_destino.numero} realizada com sucesso."
            )
            return True
        return False

    def extrato(self):
        print(f"\nExtrato da conta {self.numero} - Titular: {self.titular}")
        print(f"Saldo atual: R$ {self.saldo:.2f}")

        if not self.transacoes:
            print("Nenhuma transação realizada.")
            return

        for operacao in self.transacoes:
            print(operacao)


class Banco:
    def __init__(self):
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
        return self.contas.get(numero)

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
                else:
                    print("Conta não encontrada.")

            elif opcao == "4":
                numero_origem = input("Digite o número da conta de origem: ")
                conta_origem = self.buscar_conta(numero_origem)
                numero_destino = input("Digite o número da conta de destino: ")
                conta_destino = self.buscar_conta(numero_destino)

                if not conta_origem or not conta_destino:
                    print("Conta de origem ou destino não encontrada.")
                    continue

                try:
                    valor = float(input("Digite o valor da transferência: "))
                except ValueError:
                    print("Valor inválido.")
                    continue

                conta_origem.transferir(valor, conta_destino)

            elif opcao == "5":
                numero = input("Digite o número da conta: ")
                conta = self.buscar_conta(numero)
                if conta:
                    conta.extrato()
                else:
                    print("Conta não encontrada.")

            elif opcao == "6":
                print("Encerrando o sistema bancário...")
                break

            else:
                print("Opção inválida.")


if __name__ == "__main__":
    banco = Banco()
    banco.operar()
```

## Observações

- O código foi pensado para fins didáticos e de estudo.
- É uma base para expandir funcionalidades como autenticação, juros, histórico completo e persistência em banco de dados.
- Você pode adaptar esse projeto para incluir uma interface gráfica ou uma API web no futuro.

## Contribuição

Sinta-se à vontade para melhorar o projeto, corrigir bugs e adicionar novas funcionalidades.

## Licença

Este projeto está disponível para uso educacional e personalização livre.
