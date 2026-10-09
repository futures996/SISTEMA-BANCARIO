import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


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
        extrato += f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
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


class SistemaAutenticacao:
    def __init__(self):
        self.usuarios = self.carregar_usuarios()
        self.usuario_logado = None

    def registrar_usuario(self, nome_usuario, senha):
        if nome_usuario in self.usuarios:
            return False, "Usuário já existe!"
        
        self.usuarios[nome_usuario] = senha
        self.salvar_usuarios()
        return True, "Usuário registrado com sucesso!"

    def autenticar(self, nome_usuario, senha):
        if nome_usuario not in self.usuarios:
            return False, "Usuário não encontrado!"
        
        if self.usuarios[nome_usuario] != senha:
            return False, "Senha incorreta!"
        
        self.usuario_logado = nome_usuario
        return True, "Autenticação bem-sucedida!"

    def salvar_usuarios(self):
        with open("usuarios.json", "w", encoding="utf-8") as f:
            json.dump(self.usuarios, f, indent=2, ensure_ascii=False)

    def carregar_usuarios(self):
        if os.path.exists("usuarios.json"):
            try:
                with open("usuarios.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def logout(self):
        self.usuario_logado = None


class TelaLogin:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.auth = SistemaAutenticacao()
        self.root.title("Login - Sistema Bancário")
        self.root.geometry("400x300")
        self.root.configure(bg="#0f172a")
        
        self.setup_tema()
        self.criar_interface_login()

    def setup_tema(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Login.TFrame", background="#0f172a")
        style.configure("Login.TLabel", background="#0f172a", foreground="#f1f5f9", font=("Segoe UI", 10))
        style.configure("Login.Title.TLabel", background="#0f172a", foreground="#60a5fa", font=("Segoe UI", 16, "bold"))
        style.configure("Login.TButton", font=("Segoe UI", 10, "bold"))

    def criar_interface_login(self):
        main_frame = ttk.Frame(self.root, style="Login.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        title = ttk.Label(main_frame, text="🏦 SISTEMA BANCÁRIO", style="Login.Title.TLabel")
        title.pack(pady=(0, 30))

        ttk.Label(main_frame, text="Usuário:", style="Login.TLabel").pack(anchor=tk.W, pady=(0, 5))
        self.entry_usuario = ttk.Entry(main_frame, width=30, font=("Segoe UI", 10))
        self.entry_usuario.pack(fill=tk.X, pady=(0, 15))
        self.entry_usuario.focus()

        ttk.Label(main_frame, text="Senha:", style="Login.TLabel").pack(anchor=tk.W, pady=(0, 5))
        self.entry_senha = ttk.Entry(main_frame, width=30, font=("Segoe UI", 10), show="*")
        self.entry_senha.pack(fill=tk.X, pady=(0, 20))
        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Entrar", command=self.fazer_login).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(button_frame, text="Registrar", command=self.registrar).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            messagebox.showerror("Erro", "Preencha usuário e senha!")
            return

        sucesso, mensagem = self.auth.autenticar(usuario, senha)
        
        if sucesso:
            self.callback(usuario)
        else:
            messagebox.showerror("Erro", mensagem)

    def registrar(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            messagebox.showerror("Erro", "Preencha usuário e senha!")
            return

        if len(senha) < 4:
            messagebox.showerror("Erro", "Senha deve ter pelo menos 4 caracteres!")
            return

        sucesso, mensagem = self.auth.registrar_usuario(usuario, senha)
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.entry_usuario.delete(0, tk.END)
            self.entry_senha.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", mensagem)


class InterfaceBancaria:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title("Sistema Bancário Profissional - Tema Escuro")
        self.root.geometry("1100x750")
        
        self.banco = Banco()
        self.conta_atual = None
        self.auth = SistemaAutenticacao()
        
        self.setup_tema_escuro()
        self.criar_interface()
        self.atualizar_combo_contas()

    def setup_tema_escuro(self):
        """Tema escuro completo profissional"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Paleta de cores escura
        cor_fundo_principal = "#0f172a"
        cor_fundo_secundario = "#1e293b"
        cor_menu = "#1a2332"
        cor_primaria = "#60a5fa"
        cor_destaque = "#10b981"
        cor_texto = "#f1f5f9"
        cor_texto_secundario = "#cbd5e1"
        
        self.root.configure(bg=cor_fundo_principal)
        
        # Configurar estilos
        style.configure("Dark.TFrame", background=cor_fundo_principal)
        style.configure("Menu.TFrame", background=cor_menu)
        style.configure("Dark.TLabel", background=cor_fundo_principal, foreground=cor_texto)
        style.configure("Dark.Title.TLabel", background=cor_fundo_principal, foreground=cor_primaria, font=("Segoe UI", 14, "bold"))
        style.configure("Dark.TLabelframe", background=cor_fundo_secundario, foreground=cor_primaria, font=("Segoe UI", 10, "bold"))
        style.configure("Dark.TLabelframe.Label", background=cor_fundo_secundario, foreground=cor_primaria, font=("Segoe UI", 10, "bold"))
        
        style.configure("Dark.TButton", font=("Segoe UI", 9, "bold"), background=cor_primaria, foreground="white")
        style.map("Dark.TButton", 
                 background=[('pressed', "#1e40af"), ('active', "#3b82f6")])
        
        style.configure("Action.Dark.TButton", font=("Segoe UI", 9, "bold"), background=cor_destaque, foreground="white")
        style.map("Action.Dark.TButton",
                 background=[('pressed', "#059669"), ('active', "#10b981")])
        
        style.configure("Dark.TEntry", font=("Segoe UI", 9), fieldbackground=cor_fundo_secundario, background=cor_fundo_secundario, foreground=cor_texto)
        style.configure("Dark.TCombobox", font=("Segoe UI", 9), fieldbackground=cor_fundo_secundario, background=cor_fundo_secundario, foreground=cor_texto)

    def criar_interface(self):
        """Cria interface com menu lateral"""
        container = ttk.Frame(self.root, style="Dark.TFrame")
        container.pack(fill=tk.BOTH, expand=True)

        # Menu Lateral
        self.sidebar = ttk.Frame(container, style="Menu.TFrame", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Header do menu
        header_sidebar = ttk.Frame(self.sidebar, style="Menu.TFrame")
        header_sidebar.pack(fill=tk.X, padx=10, pady=15)

        ttk.Label(header_sidebar, text="🏦", font=("Arial", 24), background="#1a2332", foreground="#60a5fa").pack()
        ttk.Label(header_sidebar, text="BANCÁRIO", font=("Segoe UI", 10, "bold"), background="#1a2332", foreground="#f1f5f9").pack()
        ttk.Label(header_sidebar, text=f"Usuário: {self.usuario}", font=("Segoe UI", 8), background="#1a2332", foreground="#cbd5e1").pack(pady=(10, 0))

        # Separador
        ttk.Frame(self.sidebar, height=2, style="Menu.TFrame").pack(fill=tk.X, padx=10, pady=10)

        # Botões do menu
        botoes_menu = [
            ("📝 Criar Conta", self.abrir_criar_conta),
            ("💰 Operações", self.abrir_operacoes),
            ("📄 Extrato", self.exibir_extrato),
            ("📋 Listar Contas", self.listar_contas),
            ("💾 Exportar PDF", self.exportar_pdf),
            ("📋 Exportar TXT", self.exportar_txt),
            ("🔓 Logout", self.fazer_logout),
        ]

        for texto, comando in botoes_menu:
            btn = tk.Button(self.sidebar, text=texto, command=comando, font=("Segoe UI", 9, "bold"),
                           bg="#1e293b", fg="#60a5fa", relief=tk.FLAT, bd=0, padx=15, pady=10,
                           activebackground="#293548", activeforeground="#93c5fd", cursor="hand2")
            btn.pack(fill=tk.X, padx=8, pady=5)

        # Área principal
        main_content = ttk.Frame(container, style="Dark.TFrame")
        main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Header da área principal
        header = ttk.Frame(main_content, style="Dark.TFrame")
        header.pack(fill=tk.X, padx=20, pady=15)

        ttk.Label(header, text="Sistema Bancário Profissional", style="Dark.Title.TLabel").pack(anchor=tk.W)
        ttk.Label(header, text="Gerenciar contas e transações com segurança", font=("Segoe UI", 9), background="#0f172a", foreground="#cbd5e1").pack(anchor=tk.W)

        # Frame para conteúdo
        self.content_frame = ttk.Frame(main_content, style="Dark.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Frame inicial - Dashboard
        self.criar_dashboard()

    def limpar_content(self):
        """Limpa o frame de conteúdo"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def criar_dashboard(self):
        """Cria o dashboard inicial"""
        self.limpar_content()

        info_frame = ttk.LabelFrame(self.content_frame, text="📊 Dashboard", style="Dark.TLabelframe", padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True)

        mensagem = f"""Bem-vindo ao Sistema Bancário Profissional!

Usuário logado: {self.usuario}

Funcionalidades disponíveis no menu lateral:
• Criar Conta - Abra uma nova conta bancária
• Operações - Realiza depósitos, saques e transferências
• Extrato - Consulte o extrato da sua conta
• Listar Contas - Veja todas as contas cadastradas
• Exportar - Exporte seus extratos em PDF ou TXT

Use o menu lateral para navegar entre as funcionalidades.
Seus dados são salvos automaticamente."""

        text_area = tk.Text(info_frame, bg="#1e293b", fg="#f1f5f9", font=("Segoe UI", 10),
                          relief=tk.FLAT, bd=0, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, mensagem)
        text_area.config(state=tk.DISABLED)

    def abrir_criar_conta(self):
        """Abre interface para criar conta"""
        self.limpar_content()

        form_frame = ttk.LabelFrame(self.content_frame, text="📝 Criar Nova Conta", style="Dark.TLabelframe", padding="20")
        form_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(form_frame, text="Número da Conta:", style="Dark.TLabel").grid(row=0, column=0, sticky=tk.W, pady=8)
        entry_numero = ttk.Entry(form_frame, width=30, style="Dark.TEntry")
        entry_numero.grid(row=0, column=1, padx=(10, 0), sticky=tk.EW)

        ttk.Label(form_frame, text="Nome do Titular:", style="Dark.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        entry_titular = ttk.Entry(form_frame, width=30, style="Dark.TEntry")
        entry_titular.grid(row=1, column=1, padx=(10, 0), sticky=tk.EW)

        ttk.Label(form_frame, text="Saldo Inicial (R$):", style="Dark.TLabel").grid(row=2, column=0, sticky=tk.W, pady=8)
        entry_saldo = ttk.Entry(form_frame, width=30, style="Dark.TEntry")
        entry_saldo.grid(row=2, column=1, padx=(10, 0), sticky=tk.EW)
        entry_saldo.insert(0, "0.00")

        def criar():
            numero = entry_numero.get().strip()
            titular = entry_titular.get().strip()

            if not numero or not titular:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return

            try:
                saldo = float(entry_saldo.get() or 0)
            except ValueError:
                messagebox.showerror("Erro", "Saldo inválido!")
                return

            sucesso, mensagem = self.banco.criar_conta(numero, titular, saldo)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.atualizar_combo_contas()
                self.criar_dashboard()
            else:
                messagebox.showerror("Erro", mensagem)

        ttk.Button(form_frame, text="✓ Criar Conta", command=criar, style="Action.Dark.TButton").grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(15, 0))
        form_frame.columnconfigure(1, weight=1)

    def abrir_operacoes(self):
        """Abre interface de operações"""
        self.limpar_content()

        ops_frame = ttk.LabelFrame(self.content_frame, text="💰 Operações Bancárias", style="Dark.TLabelframe", padding="20")
        ops_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(ops_frame, text="Selecione uma Conta:", style="Dark.TLabel").grid(row=0, column=0, sticky=tk.W, pady=8)
        combo_contas = ttk.Combobox(ops_frame, width=28, state="readonly", style="Dark.TCombobox")
        combo_contas.grid(row=0, column=1, padx=(10, 0), sticky=tk.EW)
        combo_contas["values"] = [f"{num} - {conta.titular}" for num, conta in self.banco.contas.items()]

        ttk.Label(ops_frame, text="Valor (R$):", style="Dark.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        entry_valor = ttk.Entry(ops_frame, width=30, style="Dark.TEntry")
        entry_valor.grid(row=1, column=1, padx=(10, 0), sticky=tk.EW)

        def selecionar_conta(event=None):
            selecionada = combo_contas.get()
            if selecionada:
                numero = selecionada.split(" - ")[0]
                self.conta_atual = self.banco.buscar_conta(numero)

        combo_contas.bind("<<ComboboxSelected>>", selecionar_conta)

        def depositar():
            if not self.conta_atual:
                messagebox.showerror("Erro", "Selecione uma conta!")
                return
            
            try:
                valor = float(entry_valor.get())
            except:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            sucesso, mensagem = self.conta_atual.depositar(valor)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.banco.salvar_contas()
                entry_valor.delete(0, tk.END)
            else:
                messagebox.showerror("Erro", mensagem)

        def sacar():
            if not self.conta_atual:
                messagebox.showerror("Erro", "Selecione uma conta!")
                return
            
            try:
                valor = float(entry_valor.get())
            except:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            sucesso, mensagem = self.conta_atual.sacar(valor)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.banco.salvar_contas()
                entry_valor.delete(0, tk.END)
            else:
                messagebox.showerror("Erro", mensagem)

        def transferir():
            if not self.conta_atual:
                messagebox.showerror("Erro", "Selecione uma conta!")
                return
            
            try:
                valor = float(entry_valor.get())
            except:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            numero_destino = simpledialog.askstring("Transferência", "Número da conta destino:")
            if not numero_destino:
                return
            
            conta_destino = self.banco.buscar_conta(numero_destino)
            if not conta_destino:
                messagebox.showerror("Erro", "Conta não encontrada!")
                return
            
            sucesso, mensagem = self.conta_atual.transferir(valor, conta_destino)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.banco.salvar_contas()
                entry_valor.delete(0, tk.END)
            else:
                messagebox.showerror("Erro", mensagem)

        btn_frame = ttk.Frame(ops_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(15, 0))

        ttk.Button(btn_frame, text="📥 Depositar", command=depositar, style="Action.Dark.TButton").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="📤 Sacar", command=sacar, style="Action.Dark.TButton").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="↔️  Transferir", command=transferir, style="Action.Dark.TButton").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)

        ops_frame.columnconfigure(1, weight=1)

    def exibir_extrato(self):
        """Exibe o extrato"""
        self.limpar_content()

        if not self.conta_atual:
            messagebox.showerror("Erro", "Selecione uma conta primeiro!")
            return

        frame = ttk.LabelFrame(self.content_frame, text="📄 Extrato", style="Dark.TLabelframe", padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        text_area = tk.Text(frame, bg="#1e293b", fg="#f1f5f9", font=("Courier", 9),
                          relief=tk.FLAT, bd=0)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, self.conta_atual.get_extrato())
        text_area.config(state=tk.DISABLED)

    def listar_contas(self):
        """Lista todas as contas"""
        self.limpar_content()

        frame = ttk.LabelFrame(self.content_frame, text="📋 Contas Cadastradas", style="Dark.TLabelframe", padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        text_area = tk.Text(frame, bg="#1e293b", fg="#f1f5f9", font=("Courier", 9),
                          relief=tk.FLAT, bd=0)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, self.banco.listar_contas())
        text_area.config(state=tk.DISABLED)

    def exportar_pdf(self):
        """Exporta extrato em PDF"""
        if not self.conta_atual:
            messagebox.showerror("Erro", "Selecione uma conta!")
            return

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"extrato_{self.conta_atual.numero}.pdf"
        )

        if not arquivo:
            return

        try:
            doc = SimpleDocTemplate(arquivo, pagesize=letter)
            story = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor("#1e3a8a"),
                spaceAfter=20,
                alignment=1
            )
            
            story.append(Paragraph("EXTRATO BANCÁRIO", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            info_data = [
                ["Campo", "Valor"],
                ["Número da Conta", self.conta_atual.numero],
                ["Titular", self.conta_atual.titular],
                ["Saldo Atual", f"R$ {self.conta_atual.saldo:.2f}"],
                ["Data", datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
            ]
            
            info_table = Table(info_data, colWidths=[3*inch, 2.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))
            
            story.append(Paragraph("HISTÓRICO DE TRANSAÇÕES", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            if self.conta_atual.transacoes:
                trans_data = [["Data", "Tipo", "Valor", "Detalhes"]]
                for transacao in self.conta_atual.transacoes:
                    if len(transacao) == 4:
                        tipo, valor, data, conta_ref = transacao
                        trans_data.append([data, tipo, f"R$ {valor:.2f}", f"Conta: {conta_ref}"])
                    else:
                        tipo, valor, data = transacao
                        trans_data.append([data, tipo, f"R$ {valor:.2f}", ""])
                
                trans_table = Table(trans_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                trans_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ]))
                story.append(trans_table)
            else:
                story.append(Paragraph("Nenhuma transação realizada.", styles['Normal']))
            
            doc.build(story)
            messagebox.showinfo("Sucesso", f"Extrato exportado com sucesso!\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")

    def exportar_txt(self):
        """Exporta extrato em TXT"""
        if not self.conta_atual:
            messagebox.showerror("Erro", "Selecione uma conta!")
            return

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"extrato_{self.conta_atual.numero}.txt"
        )

        if not arquivo:
            return

        try:
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(self.conta_atual.get_extrato())
            messagebox.showinfo("Sucesso", f"Extrato exportado com sucesso!\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar TXT: {str(e)}")

    def atualizar_combo_contas(self):
        pass

    def fazer_logout(self):
        if messagebox.askokcancel("Logout", "Deseja fazer logout?"):
            self.auth.logout()
            self.root.destroy()
            root = tk.Tk()
            TelaLogin(root, lambda usuario: InterfaceBancaria(root, usuario))
            root.mainloop()


def main():
    root = tk.Tk()
    tela_login = TelaLogin(root, lambda usuario: (
        root.destroy(),
        criar_interface_bancaria(usuario)
    ))
    root.mainloop()


def criar_interface_bancaria(usuario):
    root = tk.Tk()
    app = InterfaceBancaria(root, usuario)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    tela_login = TelaLogin(root, lambda usuario: (
        root.destroy(),
        criar_interface_bancaria(usuario)
    ))
    root.mainloop()
