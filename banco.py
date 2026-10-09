import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime


class Conta:
    def __init__(self, numero, titular, saldo=0):
        self.numero = numero
        self.titular = titular
        self.saldo = saldo
        self.transacoes = []

    def depositar(self, valor):
        if valor <= 0:
            return False, "Valor inválido para depósito."

        self.saldo += valor
        self.transacoes.append(
            ("Depósito", valor, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        )
        return True, f"Depósito de R$ {valor:.2f} realizado com sucesso."

    def sacar(self, valor):
        if valor <= 0:
            return False, "Valor inválido para saque."

        if valor > self.saldo:
            return False, "Saldo insuficiente."

        self.saldo -= valor
        self.transacoes.append(
            ("Saque", valor, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        )
        return True, f"Saque de R$ {valor:.2f} realizado com sucesso."

    def transferir(self, valor, conta_destino):
        sucesso, mensagem = self.sacar(valor)
        if not sucesso:
            return False, mensagem

        sucesso_deposito, mensagem_deposito = conta_destino.depositar(valor)
        if not sucesso_deposito:
            self.saldo += valor
            self.transacoes.pop()
            return False, mensagem_deposito

        self.transacoes.append(
            ("Transferência Enviada", valor, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), conta_destino.numero)
        )
        conta_destino.transacoes.append(
            ("Transferência Recebida", valor, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.numero)
        )

        return True, f"Transferência de R$ {valor:.2f} para {conta_destino.titular} realizada com sucesso."

    def get_extrato(self):
        extrato = f"Extrato da Conta {self.numero}\n"
        extrato += f"Titular: {self.titular}\n"
        extrato += f"Saldo Atual: R$ {self.saldo:.2f}\n"
        extrato += "-" * 50 + "\n"

        if not self.transacoes:
            extrato += "Nenhuma transação realizada.\n"
        else:
            for transacao in self.transacoes:
                if len(transacao) == 4:
                    tipo, valor, data, conta_ref = transacao
                    extrato += f"{data} - {tipo}: R$ {valor:.2f} (Conta: {conta_ref})\n"
                else:
                    tipo, valor, data = transacao
                    extrato += f"{data} - {tipo}: R$ {valor:.2f}\n"

        return extrato


class Banco:
    def __init__(self):
        self.contas = {}

    def criar_conta(self, numero, titular, saldo_inicial=0):
        if numero in self.contas:
            return False, "Conta já existente!"

        conta = Conta(numero, titular, saldo_inicial)
        self.contas[numero] = conta
        return True, "Conta criada com sucesso!"

    def buscar_conta(self, numero):
        return self.contas.get(numero)

    def listar_contas(self):
        if not self.contas:
            return "Nenhuma conta cadastrada."

        lista = "Contas Cadastradas:\n" + "-" * 40 + "\n"
        for numero, conta in self.contas.items():
            lista += f"Conta: {numero} | Titular: {conta.titular} | Saldo: R$ {conta.saldo:.2f}\n"
        return lista


class InterfaceBancaria:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Bancário")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f0f0")

        self.banco = Banco()
        self.conta_atual = None

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            self.main_frame,
            text="🏦 SISTEMA BANCÁRIO",
            font=("Arial", 16, "bold"),
        )
        title.pack(pady=10)

        self.info_frame = ttk.LabelFrame(self.main_frame, text="Informações da Conta", padding="10")
        self.info_frame.pack(fill=tk.X, pady=10)

        ttk.Label(self.info_frame, text="Número da Conta:").grid(row=0, column=0, sticky=tk.W)
        self.entry_numero = ttk.Entry(self.info_frame, width=20)
        self.entry_numero.grid(row=0, column=1, padx=5)

        ttk.Label(self.info_frame, text="Nome do Titular:").grid(row=1, column=0, sticky=tk.W)
        self.entry_titular = ttk.Entry(self.info_frame, width=20)
        self.entry_titular.grid(row=1, column=1, padx=5)

        ttk.Label(self.info_frame, text="Saldo Inicial:").grid(row=2, column=0, sticky=tk.W)
        self.entry_saldo = ttk.Entry(self.info_frame, width=20)
        self.entry_saldo.grid(row=2, column=1, padx=5)

        btn_criar = ttk.Button(self.info_frame, text="Criar Conta", command=self.criar_conta)
        btn_criar.grid(row=3, column=0, columnspan=2, pady=10)

        self.operacoes_frame = ttk.LabelFrame(self.main_frame, text="Operações", padding="10")
        self.operacoes_frame.pack(fill=tk.X, pady=10)

        ttk.Label(self.operacoes_frame, text="Selecione uma Conta:").grid(row=0, column=0, sticky=tk.W)
        self.combo_contas = ttk.Combobox(self.operacoes_frame, width=25, state="readonly")
        self.combo_contas.grid(row=0, column=1, padx=5)
        self.combo_contas.bind("<<ComboboxSelected>>", self.selecionar_conta)

        ttk.Label(self.operacoes_frame, text="Valor da Operação:").grid(row=1, column=0, sticky=tk.W)
        self.entry_valor = ttk.Entry(self.operacoes_frame, width=20)
        self.entry_valor.grid(row=1, column=1, padx=5)

        btn_frame = ttk.Frame(self.operacoes_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Depositar", command=self.depositar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Sacar", command=self.sacar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Transferir", command=self.transferir).pack(side=tk.LEFT, padx=5)

        self.vis_frame = ttk.LabelFrame(self.main_frame, text="Extrato", padding="10")
        self.vis_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.text_extrato = tk.Text(self.vis_frame, height=12, width=80, bg="white")
        self.text_extrato.pack(fill=tk.BOTH, expand=True)

        final_frame = ttk.Frame(self.main_frame)
        final_frame.pack(fill=tk.X, pady=10)

        ttk.Button(final_frame, text="Exibir Extrato", command=self.exibir_extrato).pack(side=tk.LEFT, padx=5)
        ttk.Button(final_frame, text="Listar Contas", command=self.listar_contas).pack(side=tk.LEFT, padx=5)
        ttk.Button(final_frame, text="Limpar", command=self.limpar_texto).pack(side=tk.LEFT, padx=5)
        ttk.Button(final_frame, text="Sair", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

    def atualizar_combo_contas(self):
        contas = [f"{numero} - {conta.titular}" for numero, conta in self.banco.contas.items()]
        self.combo_contas["values"] = contas

    def criar_conta(self):
        numero = self.entry_numero.get()
        titular = self.entry_titular.get()

        if not numero or not titular:
            messagebox.showerror("Erro", "Preencha número e titular da conta.")
            return

        try:
            saldo = float(self.entry_saldo.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Saldo deve ser um valor numérico.")
            return

        sucesso, mensagem = self.banco.criar_conta(numero, titular, saldo)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.entry_numero.delete(0, tk.END)
            self.entry_titular.delete(0, tk.END)
            self.entry_saldo.delete(0, tk.END)
            self.atualizar_combo_contas()
        else:
            messagebox.showerror("Erro", mensagem)

    def selecionar_conta(self, event=None):
        selecionada = self.combo_contas.get()
        if selecionada:
            numero = selecionada.split(" - ")[0]
            self.conta_atual = self.banco.buscar_conta(numero)

    def depositar(self):
        if not self.conta_atual:
            messagebox.showerror("Erro", "Selecione uma conta primeiro.")
            return

        try:
            valor = float(self.entry_valor.get())
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.")
            return

        sucesso, mensagem = self.conta_atual.depositar(valor)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.entry_valor.delete(0, tk.END)
            self.atualizar_combo_contas()
        else:
            messagebox.showerror("Erro", mensagem)

    def sacar(self):
        if not self.conta_atual:
            messagebox.showerror("Erro", "Selecione uma conta primeiro.")
            return

        try:
            valor = float(self.entry_valor.get())
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.")
            return

        sucesso, mensagem = self.conta_atual.sacar(valor)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.entry_valor.delete(0, tk.END)
            self.atualizar_combo_contas()
        else:
            messagebox.showerror("Erro", mensagem)

    def transferir(self):
        if not self.conta_atual:
            messagebox.showerror("Erro", "Selecione uma conta de origem.")
            return

        try:
            valor = float(self.entry_valor.get())
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.")
            return

        conta_destino_numero = simpledialog.askstring(
            "Transferência", "Digite o número da conta de destino:"
        )

        if not conta_destino_numero:
            return

        conta_destino = self.banco.buscar_conta(conta_destino_numero)

        if not conta_destino:
            messagebox.showerror("Erro", "Conta de destino não encontrada.")
            return

        sucesso, mensagem = self.conta_atual.transferir(valor, conta_destino)

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.entry_valor.delete(0, tk.END)
            self.atualizar_combo_contas()
        else:
            messagebox.showerror("Erro", mensagem)

    def exibir_extrato(self):
        if not self.conta_atual:
            messagebox.showerror("Erro", "Selecione uma conta primeiro.")
            return

        self.limpar_texto()
        self.text_extrato.insert(tk.END, self.conta_atual.get_extrato())

    def listar_contas(self):
        self.limpar_texto()
        self.text_extrato.insert(tk.END, self.banco.listar_contas())

    def limpar_texto(self):
        self.text_extrato.delete(1.0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceBancaria(root)
    root.mainloop()
