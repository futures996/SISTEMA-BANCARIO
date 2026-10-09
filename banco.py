import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json
import os


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
        extrato = f"{'='*60}\n"
        extrato += f"  EXTRATO DA CONTA {self.numero}\n"
        extrato += f"{'='*60}\n\n"
        extrato += f"  Titular: {self.titular}\n"
        extrato += f"  Saldo Atual: R$ {self.saldo:.2f}\n"
        extrato += f"{'='*60}\n\n"
        extrato += "  HISTÓRICO DE TRANSAÇÕES:\n"
        extrato += f"{'-'*60}\n"

        if not self.transacoes:
            extrato += "  Nenhuma transação realizada.\n"
        else:
            for i, transacao in enumerate(self.transacoes, 1):
                if len(transacao) == 4:
                    tipo, valor, data, conta_ref = transacao
                    extrato += f"  {i}. {data} | {tipo}: R$ {valor:.2f} (Conta: {conta_ref})\n"
                else:
                    tipo, valor, data = transacao
                    extrato += f"  {i}. {data} | {tipo}: R$ {valor:.2f}\n"

        extrato += f"{'-'*60}\n"
        return extrato

    def to_dict(self):
        return {
            "numero": self.numero,
            "titular": self.titular,
            "saldo": self.saldo,
            "transacoes": self.transacoes
        }

    @staticmethod
    def from_dict(data):
        conta = Conta(data["numero"], data["titular"], data["saldo"])
        conta.transacoes = data["transacoes"]
        return conta


class Banco:
    def __init__(self):
        self.contas = {}
        self.arquivo_dados = "banco_dados.json"
        self.carregar_contas()

    def criar_conta(self, numero, titular, saldo_inicial=0):
        if numero in self.contas:
            return False, "Conta já existente!"

        conta = Conta(numero, titular, saldo_inicial)
        self.contas[numero] = conta
        self.salvar_contas()
        return True, "Conta criada com sucesso!"

    def buscar_conta(self, numero):
        return self.contas.get(numero)

    def listar_contas(self):
        if not self.contas:
            return "Nenhuma conta cadastrada."

        lista = f"{'='*60}\n"
        lista += "  CONTAS CADASTRADAS\n"
        lista += f"{'='*60}\n\n"
        for numero, conta in self.contas.items():
            lista += f"  Conta: {numero} | Titular: {conta.titular}\n"
            lista += f"  Saldo: R$ {conta.saldo:.2f}\n"
            lista += f"{'-'*60}\n"
        return lista

    def salvar_contas(self):
        dados = {numero: conta.to_dict() for numero, conta in self.contas.items()}
        with open(self.arquivo_dados, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    def carregar_contas(self):
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.contas = {numero: Conta.from_dict(conta) for numero, conta in dados.items()}
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")


class InterfaceBancaria:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Bancário Profissional")
        self.root.geometry("900x700")
        
        # Configurar tema profissional
        self.setup_tema()
        
        self.banco = Banco()
        self.conta_atual = None
        
        self.setup_ui()
        self.atualizar_combo_contas()

    def setup_tema(self):
        """Configura o tema profissional da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores do tema profissional
        cor_primaria = "#1e3a8a"      # Azul escuro profissional
        cor_secundaria = "#3b82f6"    # Azul mais claro
        cor_destaque = "#10b981"      # Verde para sucesso
        cor_fundo = "#f8fafc"         # Fundo claro
        cor_texto = "#1e293b"         # Texto escuro
        cor_borda = "#cbd5e1"         # Borda cinzenta
        
        # Configurar cores globais
        self.root.configure(bg=cor_fundo)
        
        # Estilo para Labels
        style.configure("TLabel", background=cor_fundo, foreground=cor_texto, font=("Segoe UI", 9))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=cor_primaria)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11, "bold"), foreground=cor_primaria)
        
        # Estilo para LabelFrame
        style.configure("TLabelframe", background=cor_fundo, foreground=cor_primaria, font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background=cor_fundo, foreground=cor_primaria, font=("Segoe UI", 10, "bold"))
        
        # Estilo para Buttons
        style.configure("TButton", font=("Segoe UI", 9, "bold"), relief="raised")
        style.map("TButton",
                 foreground=[('pressed', 'white'), ('active', 'white')],
                 background=[('pressed', cor_primaria), ('active', cor_secundaria)])
        
        # Estilo para Buttons de ação (verde)
        style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), foreground="white", background=cor_destaque)
        style.map("Action.TButton",
                 background=[('pressed', "#059669"), ('active', "#10b981")])
        
        # Estilo para Entry
        style.configure("TEntry", font=("Segoe UI", 9), relief="solid", borderwidth=1)
        
        # Estilo para Combobox
        style.configure("TCombobox", font=("Segoe UI", 9), relief="solid", borderwidth=1)
        
        # Estilo para Frame
        style.configure("TFrame", background=cor_fundo)

    def setup_ui(self):
        """Configura a interface de usuário"""
        # Container principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(header_frame, text="🏦 SISTEMA BANCÁRIO PROFISSIONAL", style="Title.TLabel")
        title.pack(anchor=tk.W)
        
        subtitle = ttk.Label(header_frame, text="Gerenciar contas e transações de forma segura", 
                           style="Subtitle.TLabel", foreground="#64748b")
        subtitle.pack(anchor=tk.W, pady=(5, 0))
        
        # Separador
        separator = ttk.Frame(main_container, height=2)
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # Frame de conteúdo (duas colunas)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Coluna esquerda - Formulários
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Seção: Criar Conta
        self.criar_conta_frame = ttk.LabelFrame(left_frame, text="📝 Criar Nova Conta", padding="15")
        self.criar_conta_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(self.criar_conta_frame, text="Número da Conta:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.entry_numero = ttk.Entry(self.criar_conta_frame, width=25)
        self.entry_numero.grid(row=0, column=1, padx=(10, 0), sticky=tk.EW)
        
        ttk.Label(self.criar_conta_frame, text="Nome do Titular:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.entry_titular = ttk.Entry(self.criar_conta_frame, width=25)
        self.entry_titular.grid(row=1, column=1, padx=(10, 0), sticky=tk.EW)
        
        ttk.Label(self.criar_conta_frame, text="Saldo Inicial (R$):").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.entry_saldo = ttk.Entry(self.criar_conta_frame, width=25)
        self.entry_saldo.grid(row=2, column=1, padx=(10, 0), sticky=tk.EW)
        self.entry_saldo.insert(0, "0.00")
        
        btn_criar = ttk.Button(self.criar_conta_frame, text="✓ Criar Conta", command=self.criar_conta)
        btn_criar.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(15, 0))
        
        self.criar_conta_frame.columnconfigure(1, weight=1)
        
        # Seção: Operações
        self.operacoes_frame = ttk.LabelFrame(left_frame, text="💰 Operações Bancárias", padding="15")
        self.operacoes_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.operacoes_frame, text="Selecione uma Conta:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.combo_contas = ttk.Combobox(self.operacoes_frame, width=23, state="readonly")
        self.combo_contas.grid(row=0, column=1, padx=(10, 0), sticky=tk.EW, pady=8)
        self.combo_contas.bind("<<ComboboxSelected>>", self.selecionar_conta)
        
        # Mostrar saldo atual
        saldo_frame = ttk.Frame(self.operacoes_frame)
        saldo_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(saldo_frame, text="Saldo Atual:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.label_saldo = ttk.Label(saldo_frame, text="R$ 0.00", font=("Segoe UI", 11, "bold"), foreground="#10b981")
        self.label_saldo.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(self.operacoes_frame, text="Valor da Operação (R$):").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.entry_valor = ttk.Entry(self.operacoes_frame, width=25)
        self.entry_valor.grid(row=2, column=1, padx=(10, 0), sticky=tk.EW)
        
        # Botões de operações
        btn_frame = ttk.Frame(self.operacoes_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(15, 0))
        
        ttk.Button(btn_frame, text="📥 Depositar", command=self.depositar).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="📤 Sacar", command=self.sacar).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="↔️  Transferir", command=self.transferir).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        self.operacoes_frame.columnconfigure(1, weight=1)
        
        # Coluna direita - Extrato
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.vis_frame = ttk.LabelFrame(right_frame, text="📄 Extrato / Informações", padding="15")
        self.vis_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar frame com scrollbar
        scrollbar_frame = ttk.Frame(self.vis_frame)
        scrollbar_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scrollbar_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_extrato = tk.Text(scrollbar_frame, height=25, width=50, bg="white", 
                                    font=("Courier", 8), yscrollcommand=scrollbar.set)
        self.text_extrato.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_extrato.yview)
        
        # Botões inferiores
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(bottom_frame, text="👁️  Ver Extrato", command=self.exibir_extrato).pack(side=tk.LEFT, padx=3)
        ttk.Button(bottom_frame, text="📋 Listar Contas", command=self.listar_contas).pack(side=tk.LEFT, padx=3)
        ttk.Button(bottom_frame, text="🗑️  Limpar", command=self.limpar_texto).pack(side=tk.LEFT, padx=3)
        ttk.Button(bottom_frame, text="❌ Sair", command=self.sair).pack(side=tk.RIGHT, padx=3)
        
        # Mostrar mensagem inicial
        self.limpar_texto()
        self.text_extrato.insert(tk.END, 
            "Bem-vindo ao Sistema Bancário Profissional!\n\n"
            "• Crie uma nova conta preenchendo os dados à esquerda\n"
            "• Selecione uma conta para realizar operações\n"
            "• Seus dados são salvos automaticamente\n\n"
            "Clique em 'Listar Contas' para ver todas as contas cadastradas."
        )

    def atualizar_combo_contas(self):
        contas = [f"{numero} - {conta.titular}" for numero, conta in self.banco.contas.items()]
        self.combo_contas["values"] = contas

    def atualizar_saldo(self):
        if self.conta_atual:
            self.label_saldo.config(text=f"R$ {self.conta_atual.saldo:.2f}")

    def criar_conta(self):
        numero = self.entry_numero.get().strip()
        titular = self.entry_titular.get().strip()

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
            self.entry_saldo.insert(0, "0.00")
            self.atualizar_combo_contas()
        else:
            messagebox.showerror("Erro", mensagem)

    def selecionar_conta(self, event=None):
        selecionada = self.combo_contas.get()
        if selecionada:
            numero = selecionada.split(" - ")[0]
            self.conta_atual = self.banco.buscar_conta(numero)
            self.atualizar_saldo()

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
            self.atualizar_saldo()
            self.banco.salvar_contas()
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
            self.atualizar_saldo()
            self.banco.salvar_contas()
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
            self.atualizar_saldo()
            self.banco.salvar_contas()
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

    def sair(self):
        if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?"):
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceBancaria(root)
    root.mainloop()
