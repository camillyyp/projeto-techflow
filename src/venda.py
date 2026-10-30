from decimal import Decimal

from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIntValidator
from PyQt6.QtWidgets import QMessageBox, QAbstractItemView

from utils.cnn import conectar


class GerenciadorVendas:
    """Controla o CRUD da tabela vendas na tela do dashboard."""

    def __init__(self, tela):
        self.tela = tela
        self.id_venda_selecionada = None
        self.precos_produtos = {}

        self.modelo = QStandardItemModel()
        self.modelo.setHorizontalHeaderLabels([
            "Código", "Cliente", "Produto", "Quantidade", "Valor total", "Data da venda"
        ])
        self.tela.tabela_vendas.setModel(self.modelo)
        self.tela.tabela_vendas.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tela.tabela_vendas.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tela.tabela_vendas.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tela.cnt_quant_vendas.setValidator(QIntValidator(1, 999999, self.tela))

        self.tela.btn_salvar_vendas.clicked.connect(self.salvar_venda)
        self.tela.btn_limpar_vendas.clicked.connect(self.limpar_campos)
        self.tela.btn_excluir_vendas.clicked.connect(self.excluir_venda)
        self.tela.tabela_vendas.doubleClicked.connect(
            self.carregar_campos_ao_duplo_clique
        )
        self.tela.cmb_produto_vendas.currentIndexChanged.connect(
            self.atualizar_valor_total
        )
        self.tela.cnt_quant_vendas.textChanged.connect(
            self.atualizar_valor_total
        )

        self.carregar_clientes()
        self.carregar_produtos()
        self.carregar_dados_na_tabela()

    @staticmethod
    def formatar_moeda(valor):
        valor = Decimal(str(valor or 0))
        return f"R$ {valor:.2f}".replace(".", ",")

    def carregar_clientes(self):
        self.tela.cmb_clientes_vendas.clear()
        self.tela.cmb_clientes_vendas.addItem("Selecione", None)
        conexao = None
        cursor = None
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id_clientes, nome FROM clientes ORDER BY nome"
            )
            for id_cliente, nome in cursor.fetchall():
                self.tela.cmb_clientes_vendas.addItem(
                    f"{id_cliente} - {nome}", id_cliente
                )
        except Exception as erro:
            QMessageBox.critical(
                self.tela, "Erro", f"Erro ao carregar clientes:\n{erro}"
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def carregar_produtos(self):
        self.tela.cmb_produto_vendas.clear()
        self.tela.cmb_produto_vendas.addItem("Selecione", None)
        self.precos_produtos.clear()
        conexao = None
        cursor = None
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id_produto, nome_produto, preco FROM produtos ORDER BY nome_produto"
            )
            for id_produto, nome, preco in cursor.fetchall():
                self.precos_produtos[int(id_produto)] = Decimal(str(preco or 0))
                self.tela.cmb_produto_vendas.addItem(
                    f"{id_produto} - {nome}", id_produto
                )
        except Exception as erro:
            QMessageBox.critical(
                self.tela, "Erro", f"Erro ao carregar produtos:\n{erro}"
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def atualizar_valor_total(self):
        id_produto = self.tela.cmb_produto_vendas.currentData()
        try:
            quantidade = int(self.tela.cnt_quant_vendas.text() or 0)
        except ValueError:
            quantidade = 0
        preco = self.precos_produtos.get(id_produto, Decimal("0"))
        self.tela.total_vendas.setText(
            self.formatar_moeda(preco * quantidade)
        )

    def carregar_dados_na_tabela(self):
        self.modelo.removeRows(0, self.modelo.rowCount())
        conexao = None
        cursor = None
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT v.id_venda, v.id_cliente, c.nome,
                       v.id_produto, p.nome_produto, v.quantidade,
                       v.valor_total, v.data_venda
                FROM vendas v
                INNER JOIN clientes c ON c.id_clientes = v.id_cliente
                INNER JOIN produtos p ON p.id_produto = v.id_produto
                ORDER BY v.id_venda DESC
            """)
            total_vendas = Decimal("0")
            total_itens = 0
            for venda in cursor.fetchall():
                valor = Decimal(str(venda[6] or 0))
                quantidade = int(venda[5] or 0)
                data = venda[7].strftime("%d/%m/%Y %H:%M") if hasattr(venda[7], "strftime") else str(venda[7])

                itens = [
                    QStandardItem(str(venda[0])),
                    QStandardItem(f"{venda[1]} - {venda[2]}"),
                    QStandardItem(f"{venda[3]} - {venda[4]}"),
                    QStandardItem(str(quantidade)),
                    QStandardItem(self.formatar_moeda(valor)),
                    QStandardItem(data),
                ]
                itens[0].setData(venda[1] if venda[1] is not None else None, 256)
                itens[0].setData(venda[3] if venda[3] is not None else None, 257)
                self.modelo.appendRow(itens)
                total_vendas += valor
                total_itens += quantidade

            self.tela.tabela_vendas.resizeColumnsToContents()
            self.tela.tabela_vendas.horizontalHeader().setStretchLastSection(True)
            self.tela.label_61.setText(self.formatar_moeda(total_vendas))
            self.tela.label_64.setText(str(total_itens))
        except Exception as erro:
            QMessageBox.critical(
                self.tela, "Erro", f"Erro ao carregar vendas:\n{erro}"
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def salvar_venda(self):
        id_cliente = self.tela.cmb_clientes_vendas.currentData()
        id_produto = self.tela.cmb_produto_vendas.currentData()
        quantidade_texto = self.tela.cnt_quant_vendas.text().strip()

        if id_cliente is None:
            QMessageBox.warning(self.tela, "Aviso", "Selecione um cliente.")
            return
        if id_produto is None:
            QMessageBox.warning(self.tela, "Aviso", "Selecione um produto.")
            return
        try:
            quantidade = int(quantidade_texto)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self.tela, "Aviso", "Digite uma quantidade inteira maior que zero."
            )
            return

        preco = self.precos_produtos.get(id_produto)
        if preco is None:
            QMessageBox.warning(self.tela, "Aviso", "Preço do produto não encontrado.")
            return
        valor_total = preco * quantidade

        conexao = None
        cursor = None
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            if self.id_venda_selecionada is None:
                cursor.execute("""
                    INSERT INTO vendas
                        (id_cliente, id_produto, quantidade, valor_total, data_venda)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (id_cliente, id_produto, quantidade, valor_total))
                mensagem = "Venda cadastrada com sucesso!"
            else:
                cursor.execute("""
                    UPDATE vendas
                    SET id_cliente = %s,
                        id_produto = %s,
                        quantidade = %s,
                        valor_total = %s
                    WHERE id_venda = %s
                """, (
                    id_cliente, id_produto, quantidade, valor_total,
                    self.id_venda_selecionada
                ))
                mensagem = "Venda atualizada com sucesso!"

            conexao.commit()
            QMessageBox.information(self.tela, "Sucesso", mensagem)
            self.limpar_campos()
            self.carregar_dados_na_tabela()
        except Exception as erro:
            if conexao is not None:
                conexao.rollback()
            QMessageBox.critical(
                self.tela, "Erro", f"Não foi possível salvar a venda:\n{erro}"
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def carregar_campos_ao_duplo_clique(self, index):
        linha = index.row()
        item_id = self.modelo.item(linha, 0)
        if item_id is None:
            return

        self.id_venda_selecionada = int(item_id.text())
        id_cliente = item_id.data(256)
        id_produto = item_id.data(257)
        quantidade = self.modelo.item(linha, 3)

        indice_cliente = self.tela.cmb_clientes_vendas.findData(id_cliente)
        indice_produto = self.tela.cmb_produto_vendas.findData(id_produto)
        if indice_cliente >= 0:
            self.tela.cmb_clientes_vendas.setCurrentIndex(indice_cliente)
        if indice_produto >= 0:
            self.tela.cmb_produto_vendas.setCurrentIndex(indice_produto)
        self.tela.cnt_quant_vendas.setText(
            quantidade.text() if quantidade else ""
        )
        self.tela.btn_salvar_vendas.setText("💾 Atualizar")
        self.atualizar_valor_total()

    def excluir_venda(self):
        id_venda = self.id_venda_selecionada
        if id_venda is None:
            linhas = self.tela.tabela_vendas.selectionModel().selectedRows()
            if not linhas:
                QMessageBox.warning(
                    self.tela, "Aviso", "Selecione uma venda na tabela."
                )
                return
            item_id = self.modelo.item(linhas[0].row(), 0)
            if item_id is None:
                return
            id_venda = int(item_id.text())

        resposta = QMessageBox.question(
            self.tela,
            "Confirmar exclusão",
            f"Deseja realmente excluir a venda de código {id_venda}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        conexao = None
        cursor = None
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM vendas WHERE id_venda = %s", (id_venda,))
            conexao.commit()
            if cursor.rowcount == 0:
                QMessageBox.warning(self.tela, "Aviso", "Venda não encontrada.")
            else:
                QMessageBox.information(
                    self.tela, "Sucesso", "Venda excluída com sucesso!"
                )
            self.limpar_campos()
            self.carregar_dados_na_tabela()
        except Exception as erro:
            if conexao is not None:
                conexao.rollback()
            QMessageBox.critical(
                self.tela, "Erro", f"Não foi possível excluir a venda:\n{erro}"
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def limpar_campos(self):
        self.id_venda_selecionada = None
        self.tela.cmb_clientes_vendas.setCurrentIndex(0)
        self.tela.cmb_produto_vendas.setCurrentIndex(0)
        self.tela.cnt_quant_vendas.clear()
        self.tela.total_vendas.setText("R$ 0,00")
        self.tela.tabela_vendas.clearSelection()
        self.tela.btn_salvar_vendas.setText("💾 Salvar")
