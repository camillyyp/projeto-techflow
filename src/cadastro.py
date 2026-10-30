import sys
import bcrypt
from pathlib import Path
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox

from utils.cnn import conectar


class TelaCadastro(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi("views/cadastro.ui", self)

        # Campos de senha ocultos
        self.entry_senha.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.entry_conf_senha.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # Botão cadastrar
        self.btn_cadastrar.clicked.connect(self.cadastrar)

    def cadastrar(self):
        nome = self.entry_nome.text().strip()
        login = self.entry_login.text().strip()
        senha = self.entry_senha.text()
        conf_senha = self.entry_conf_senha.text()

        # Validação dos campos
        if not nome or not login or not senha or not conf_senha:
            QMessageBox.warning(
                self,
                "Atenção",
                "Preencha todos os campos."
            )
            return

        # Confirmação da senha
        if senha != conf_senha:
            QMessageBox.warning(
                self,
                "Senha",
                "As senhas não conferem."
            )
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            # Verifica login existente
            sql = "SELECT id_usuarios FROM usuarios WHERE login=%s"
            cursor.execute(sql, (login,))

            if cursor.fetchone():
                QMessageBox.warning(
                    self,
                    "Cadastro",
                    "Login já cadastrado."
                )
                return

            # Hash da senha
            senha_hash = bcrypt.hashpw(
                senha.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            sql = """
                INSERT INTO usuarios
                (nome, login, senha)
                VALUES (%s, %s, %s)
            """

            valores = (
                nome,
                login,
                senha_hash
            )

            cursor.execute(sql, valores)
            conn.commit()

            QMessageBox.information(
                self,
                "Sucesso",
                "Usuário cadastrado com sucesso!"
            )

            self.entry_nome.clear()
            self.entry_login.clear()
            self.entry_senha.clear()
            self.entry_conf_senha.clear()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao cadastrar:\n{e}"
            )

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

