import sqlite3
import json
from datetime import datetime
from pathlib import Path


class BancoDados:
    """Gerenciador de banco de dados SQLite para o sistema bancário"""
    
    def __init__(self, nome_db="banco.db"):
        self.caminho_db = Path(nome_db)
        self.conexao = None
        self.inicializar()
    
    def conectar(self):
        """Conecta ao banco de dados"""
        self.conexao = sqlite3.connect(str(self.caminho_db))
        self.conexao.row_factory = sqlite3.Row
        return self.conexao
    
    def desconectar(self):
        """Desconecta do banco de dados"""
        if self.conexao:
            self.conexao.close()
    
    def inicializar(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        self.conectar()
        cursor = self.conexao.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                email TEXT,
                data_criacao TEXT NOT NULL,
                foto_perfil BLOB,
                ativo INTEGER DEFAULT 1
            )
        ''')
        
        # Tabela de contas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                titular TEXT NOT NULL,
                saldo REAL DEFAULT 0,
                data_criacao TEXT NOT NULL,
                usuario_criador TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                FOREIGN KEY(usuario_criador) REFERENCES usuarios(nome_usuario)
            )
        ''')
        
        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conta_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                data_hora TEXT NOT NULL,
                conta_referencia TEXT,
                descricao TEXT,
                FOREIGN KEY(conta_id) REFERENCES contas(id)
            )
        ''')
        
        self.conexao.commit()
        self.desconectar()
    
    def registrar_usuario(self, nome_usuario, senha_hash, email="", foto_perfil=None):
        """Registra um novo usuário"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('''
                INSERT INTO usuarios (nome_usuario, senha, email, data_criacao, foto_perfil)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome_usuario, senha_hash, email, datetime.now().isoformat(), foto_perfil))
            
            self.conexao.commit()
            return True, "Usuário registrado com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Usuário já existe!"
        except Exception as e:
            return False, f"Erro ao registrar: {str(e)}"
        finally:
            self.desconectar()
    
    def buscar_usuario(self, nome_usuario):
        """Busca um usuário pelo nome"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('''
                SELECT * FROM usuarios WHERE nome_usuario = ? AND ativo = 1
            ''', (nome_usuario,))
            
            resultado = cursor.fetchone()
            return resultado
        except Exception as e:
            print(f"Erro ao buscar usuário: {str(e)}")
            return None
        finally:
            self.desconectar()
    
    def alterar_senha(self, nome_usuario, senha_hash):
        """Altera a senha do usuário"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('''
                UPDATE usuarios SET senha = ? WHERE nome_usuario = ?
            ''', (senha_hash, nome_usuario))
            
            self.conexao.commit()
            return True, "Senha alterada com sucesso!"
        except Exception as e:
            return False, f"Erro ao alterar senha: {str(e)}"
        finally:
            self.desconectar()
    
    def atualizar_foto_perfil(self, nome_usuario, foto_dados):
        """Atualiza a foto de perfil do usuário"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('''
                UPDATE usuarios SET foto_perfil = ? WHERE nome_usuario = ?
            ''', (foto_dados, nome_usuario))
            
            self.conexao.commit()
            return True, "Foto atualizada com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar foto: {str(e)}"
        finally:
            self.desconectar()
    
    def criar_conta(self, numero, titular, saldo_inicial, usuario_criador):
        """Cria uma nova conta bancária"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('''
                INSERT INTO contas (numero, titular, saldo, data_criacao, usuario_criador)
                VALUES (?, ?, ?, ?, ?)
            ''', (numero, titular, saldo_inicial, datetime.now().isoformat(), usuario_criador))
            
            self.conexao.commit()
            return True, "Conta criada com sucesso!", cursor.lastrowid
        except sqlite3.IntegrityError:
            return False, "Número de conta já existe!", None
        except Exception as e:
            return False, f"Erro ao criar conta: {str(e)}", None
        finally:
            self.desconectar()
    
    def buscar_conta(self, numero):
        """Busca uma conta pelo número"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('''
                SELECT * FROM contas WHERE numero = ? AND ativo = 1
            ''', (numero,))
            
            resultado = cursor.fetchone()
            return resultado
        except Exception as e:
            print(f"Erro ao buscar conta: {str(e)}")
            return None
        finally:
            self.desconectar()
    
    def listar_contas(self, usuario=None):
        """Lista todas as contas ou as de um usuário específico"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            if usuario:
                cursor.execute('''
                    SELECT * FROM contas WHERE usuario_criador = ? AND ativo = 1
                ''', (usuario,))
            else:
                cursor.execute('''
                    SELECT * FROM contas WHERE ativo = 1
                ''')
            
            resultados = cursor.fetchall()
            return resultados
        except Exception as e:
            print(f"Erro ao listar contas: {str(e)}")
            return []
        finally:
            self.desconectar()
    
    def depositar(self, numero_conta, valor):
        """Registra um depósito"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            # Busca a conta
            cursor.execute('SELECT id, saldo FROM contas WHERE numero = ? AND ativo = 1', (numero_conta,))
            conta = cursor.fetchone()
            
            if not conta:
                return False, "Conta não encontrada!"
            
            novo_saldo = conta['saldo'] + valor
            
            # Atualiza o saldo
            cursor.execute('''
                UPDATE contas SET saldo = ? WHERE id = ?
            ''', (novo_saldo, conta['id']))
            
            # Registra a transação
            cursor.execute('''
                INSERT INTO transacoes (conta_id, tipo, valor, data_hora, descricao)
                VALUES (?, ?, ?, ?, ?)
            ''', (conta['id'], 'Depósito', valor, datetime.now().isoformat(), 'Depósito realizado'))
            
            self.conexao.commit()
            return True, f"Depósito de R$ {valor:.2f} realizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao depositar: {str(e)}"
        finally:
            self.desconectar()
    
    def sacar(self, numero_conta, valor):
        """Registra um saque"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('SELECT id, saldo FROM contas WHERE numero = ? AND ativo = 1', (numero_conta,))
            conta = cursor.fetchone()
            
            if not conta:
                return False, "Conta não encontrada!"
            
            if conta['saldo'] < valor:
                return False, "Saldo insuficiente!"
            
            novo_saldo = conta['saldo'] - valor
            
            cursor.execute('''
                UPDATE contas SET saldo = ? WHERE id = ?
            ''', (novo_saldo, conta['id']))
            
            cursor.execute('''
                INSERT INTO transacoes (conta_id, tipo, valor, data_hora, descricao)
                VALUES (?, ?, ?, ?, ?)
            ''', (conta['id'], 'Saque', valor, datetime.now().isoformat(), 'Saque realizado'))
            
            self.conexao.commit()
            return True, f"Saque de R$ {valor:.2f} realizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao sacar: {str(e)}"
        finally:
            self.desconectar()
    
    def transferir(self, numero_origem, numero_destino, valor):
        """Realiza uma transferência entre contas"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            # Busca as contas
            cursor.execute('SELECT id, saldo FROM contas WHERE numero = ? AND ativo = 1', (numero_origem,))
            conta_origem = cursor.fetchone()
            
            cursor.execute('SELECT id, saldo FROM contas WHERE numero = ? AND ativo = 1', (numero_destino,))
            conta_destino = cursor.fetchone()
            
            if not conta_origem or not conta_destino:
                return False, "Uma ou ambas as contas não foram encontradas!"
            
            if conta_origem['saldo'] < valor:
                return False, "Saldo insuficiente!"
            
            # Atualiza os saldos
            novo_saldo_origem = conta_origem['saldo'] - valor
            novo_saldo_destino = conta_destino['saldo'] + valor
            
            cursor.execute('UPDATE contas SET saldo = ? WHERE id = ?', (novo_saldo_origem, conta_origem['id']))
            cursor.execute('UPDATE contas SET saldo = ? WHERE id = ?', (novo_saldo_destino, conta_destino['id']))
            
            # Registra as transações
            cursor.execute('''
                INSERT INTO transacoes (conta_id, tipo, valor, data_hora, conta_referencia, descricao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conta_origem['id'], 'Transferência Enviada', valor, datetime.now().isoformat(), numero_destino, f'Transferência para {numero_destino}'))
            
            cursor.execute('''
                INSERT INTO transacoes (conta_id, tipo, valor, data_hora, conta_referencia, descricao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conta_destino['id'], 'Transferência Recebida', valor, datetime.now().isoformat(), numero_origem, f'Transferência de {numero_origem}'))
            
            self.conexao.commit()
            return True, f"Transferência de R$ {valor:.2f} realizada com sucesso!"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao transferir: {str(e)}"
        finally:
            self.desconectar()
    
    def obter_extrato(self, numero_conta, pagina=1, itens_por_pagina=10):
        """Obtém o extrato de uma conta com paginação"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            # Busca a conta
            cursor.execute('SELECT * FROM contas WHERE numero = ? AND ativo = 1', (numero_conta,))
            conta = cursor.fetchone()
            
            if not conta:
                return None, None, 0
            
            # Conta total de transações
            cursor.execute('SELECT COUNT(*) as total FROM transacoes WHERE conta_id = ?', (conta['id'],))
            total = cursor.fetchone()['total']
            total_paginas = (total + itens_por_pagina - 1) // itens_por_pagina
            
            if pagina < 1:
                pagina = 1
            if pagina > total_paginas and total_paginas > 0:
                pagina = total_paginas
            
            # Busca as transações da página
            offset = (pagina - 1) * itens_por_pagina
            cursor.execute('''
                SELECT * FROM transacoes WHERE conta_id = ? ORDER BY data_hora DESC LIMIT ? OFFSET ?
            ''', (conta['id'], itens_por_pagina, offset))
            
            transacoes = cursor.fetchall()
            return conta, transacoes, total_paginas
        except Exception as e:
            print(f"Erro ao obter extrato: {str(e)}")
            return None, None, 0
        finally:
            self.desconectar()
    
    def obter_saldo(self, numero_conta):
        """Obtém o saldo atual de uma conta"""
        try:
            self.conectar()
            cursor = self.conexao.cursor()
            
            cursor.execute('SELECT saldo FROM contas WHERE numero = ? AND ativo = 1', (numero_conta,))
            resultado = cursor.fetchone()
            
            if resultado:
                return resultado['saldo']
            return 0
        except Exception as e:
            print(f"Erro ao obter saldo: {str(e)}")
            return 0
        finally:
            self.desconectar()
