from PyQt6 import QtWidgets, uic
import sys

import bcrypt
from src.dashboard import TelaDashboard
from src.cadastro import TelaCadastro
from utils.cnn import conectar


class TelaLogin(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("views/login.ui", self)

        self.btn_entrar.clicked.connect(self.verificar_login)
        self.btn_tela_cadastro.clicked.connect(self.criar_conta)

    def criar_conta(self):

        self.nova_tela = TelaCadastro()
        self.nova_tela.show()
        self.close()

    def verificar_login(self):

        usuario_digitado = self.txt_usuario.text()
        senha_digitada = self.txt_senha.text()

        try:

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT senha FROM usuarios WHERE login=%s",
                (usuario_digitado,)
            )

            resultado = cursor.fetchone()

            if resultado is None:

                QtWidgets.QMessageBox.warning(
                    self,
                    "Erro",
                    "Usuário não encontrado"
                )
                return

            senha_banco = resultado[0]

            if bcrypt.checkpw(
                senha_digitada.encode("utf-8"),
                senha_banco.encode("utf-8")
            ):

                cursor.execute(
                    "SELECT nome FROM usuarios WHERE login=%s",
                    (usuario_digitado,)
                )

                usuario = cursor.fetchone()
                nome_usuario = usuario[0]

                self.nova_tela = TelaDashboard(nome_usuario)
                self.nova_tela.show()
                self.close()

            else:

                QtWidgets.QMessageBox.warning(
                    self,
                    "Erro",
                    "Senha incorreta"
                )

            cursor.close()
            conn.close()

        except Exception as erro:

            QtWidgets.QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    janela = TelaLogin()
    janela.show()

    sys.exit(app.exec())