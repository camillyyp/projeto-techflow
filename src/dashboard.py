from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)
import sys

from src.cliente import GerenciadorClientes
from src.produto import GerenciadorProdutos
from src.venda import GerenciadorVendas


class TelaDashboard(QtWidgets.QWidget):
    def __init__(self, nome_usuario):
        super().__init__()
        uic.loadUi("views/dashboard.ui", self)

        self.lbl_usuario = QtWidgets.QLabel(self)
        self.lbl_usuario.setText(f"👤 {nome_usuario}")
        self.lbl_usuario.setGeometry(760, 10, 220, 30)
        self.lbl_usuario.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        self.largura_menu_aberto = 200
        self.largura_menu_fechado = 0
        self.menu_lateral.setMinimumWidth(self.largura_menu_aberto)
        self.menu_lateral.setMaximumWidth(self.largura_menu_aberto)
        self.menu_aberto = True

        self.drop_button.clicked.connect(self.alternar_menu)

        self.conteudo_principal.setCurrentIndex(0)

        self.button_home.clicked.connect(
            lambda: self.conteudo_principal.setCurrentIndex(0)
        )
        self.cadastro_cliente.clicked.connect(
            lambda: self.conteudo_principal.setCurrentIndex(3)
        )
        self.cadastro_produto.clicked.connect(
            lambda: self.conteudo_principal.setCurrentIndex(1)
        )
        self.cadastro_vendas.clicked.connect(
            lambda: self.conteudo_principal.setCurrentIndex(2)
        )


        self.gerenciador_clientes = GerenciadorClientes(self)
        self.gerenciador_produtos = GerenciadorProdutos(self)
        self.gerenciador_vendas = GerenciadorVendas(self)

    def alternar_menu(self):
        anim_min = QPropertyAnimation(
            self.menu_lateral,
            b"minimumWidth"
        )
        anim_max = QPropertyAnimation(
            self.menu_lateral,
            b"maximumWidth"
        )

        for animacao in (anim_min, anim_max):
            animacao.setDuration(300)
            animacao.setEasingCurve(
                QEasingCurve.Type.InOutCubic
            )

        if self.menu_aberto:
            anim_min.setStartValue(self.largura_menu_aberto)
            anim_min.setEndValue(self.largura_menu_fechado)
            anim_max.setStartValue(self.largura_menu_aberto)
            anim_max.setEndValue(self.largura_menu_fechado)
        else:
            anim_min.setStartValue(self.largura_menu_fechado)
            anim_min.setEndValue(self.largura_menu_aberto)
            anim_max.setStartValue(self.largura_menu_fechado)
            anim_max.setEndValue(self.largura_menu_aberto)

        self.menu_aberto = not self.menu_aberto

        self.animacao = QParallelAnimationGroup(self)
        self.animacao.addAnimation(anim_min)
        self.animacao.addAnimation(anim_max)
        self.animacao.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    janela = TelaDashboard("Usuário")
    janela.show()
    sys.exit(app.exec())
