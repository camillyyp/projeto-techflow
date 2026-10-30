from decimal import Decimal, InvalidOperation

from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMessageBox, QAbstractItemView

from utils.cnn import conectar


class GerenciadorProdutos:
    def __init__(self, tela):
        self.tela = tela

        self.modelo = QStandardItemModel()
        self.modelo.setHorizontalHeaderLabels(
            ["Código", "Nome", "Categoria", "Preço", "Quantidade"]
        )
        self.tela.tableView_3.setModel(self.modelo)

        self.tela.tableView_3.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tela.tableView_3.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tela.tableView_3.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tela.btn_salvar_3.clicked.connect(self.salvar_produto)
        self.tela.btn_limpar_3.clicked.connect(self.limpar_campos)
        self.tela.btn_excluir_3.clicked.connect(self.excluir_produto)
        self.tela.tableView_3.doubleClicked.connect(
            self.carregar_campos_ao_duplo_clique
        )

        self.carregar_dados_na_tabela()

    def carregar_dados_na_tabela(self):
        """Carrega os produtos cadastrados no banco de dados."""
        self.modelo.removeRows(0, self.modelo.rowCount())
        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute(
                """
                SELECT id_produto, nome_produto, categoria, preco, quantidade
                FROM produtos
                ORDER BY id_produto
                """
            )

            for produto in cursor.fetchall():
                preco = Decimal(str(produto[3] or 0))
                linha = [
                    QStandardItem(str(produto[0] or "")),
                    QStandardItem(str(produto[1] or "")),
                    QStandardItem(str(produto[2] or "")),
                    QStandardItem(f"{preco:.2f}".replace(".", ",")),
                    QStandardItem(str(produto[4] or 0)),
                ]
                self.modelo.appendRow(linha)

            self.tela.tableView_3.resizeColumnsToContents()
            self.tela.tableView_3.horizontalHeader().setStretchLastSection(True)

        except Exception as erro:
            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao carregar produtos do banco:\n{erro}",
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def salvar_produto(self):
        """Cadastra um produto novo ou atualiza um produto existente."""
        codigo_texto = self.tela.codigo_produto.text().strip()
        nome = self.tela.nome_produto.text().strip()
        categoria = self.tela.categoria_produto.currentText().strip()
        preco_texto = self.tela.edit_email_3.text().strip()
        quantidade_texto = self.tela.edit_cidade_3.text().strip()

        if not nome:
            QMessageBox.warning(self.tela, "Aviso", "Preencha o nome do produto.")
            return
        if not categoria:
            QMessageBox.warning(self.tela, "Aviso", "Selecione a categoria.")
            return
        if not preco_texto:
            QMessageBox.warning(self.tela, "Aviso", "Preencha o preço do produto.")
            return
        if not quantidade_texto:
            QMessageBox.warning(self.tela, "Aviso", "Preencha a quantidade.")
            return

        try:
            preco = Decimal(preco_texto.replace("R$", "").replace(" ", "").replace(",", "."))
            if preco < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            QMessageBox.warning(
                self.tela, "Aviso", "Digite um preço válido. Exemplo: 59,90."
            )
            return

        try:
            quantidade = int(quantidade_texto)
            if quantidade < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Digite uma quantidade inteira igual ou maior que zero.",
            )
            return

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            if codigo_texto:
                cursor.execute(
                    """
                    UPDATE produtos
                    SET nome_produto = %s,
                        categoria = %s,
                        preco = %s,
                        quantidade = %s
                    WHERE id_produto = %s
                    """,
                    (nome, categoria, preco, quantidade, int(codigo_texto)),
                )
                mensagem = (
                    "Produto atualizado com sucesso!"
                    if cursor.rowcount > 0
                    else "Nenhuma alteração foi realizada."
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO produtos
                        (nome_produto, categoria, preco, quantidade)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nome, categoria, preco, quantidade),
                )
                mensagem = "Produto cadastrado com sucesso!"

            conexao.commit()
            QMessageBox.information(self.tela, "Sucesso", mensagem)
            self.limpar_campos()
            self.carregar_dados_na_tabela()

        except Exception as erro:
            if conexao is not None:
                conexao.rollback()
            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível salvar o produto:\n{erro}",
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def carregar_campos_ao_duplo_clique(self, index):
        """Carrega a linha selecionada nos campos para edição."""
        linha = index.row()

        codigo = self.modelo.item(linha, 0)
        nome = self.modelo.item(linha, 1)
        categoria = self.modelo.item(linha, 2)
        preco = self.modelo.item(linha, 3)
        quantidade = self.modelo.item(linha, 4)

        self.tela.codigo_produto.setText(codigo.text() if codigo else "")
        self.tela.nome_produto.setText(nome.text() if nome else "")

        categoria_texto = categoria.text() if categoria else ""
        indice_categoria = self.tela.categoria_produto.findText(categoria_texto)
        if indice_categoria >= 0:
            self.tela.categoria_produto.setCurrentIndex(indice_categoria)
        else:
            self.tela.categoria_produto.setCurrentText(categoria_texto)

        self.tela.edit_email_3.setText(preco.text() if preco else "")
        self.tela.edit_cidade_3.setText(quantidade.text() if quantidade else "")

    def excluir_produto(self):
        """Exclui o produto selecionado do banco de dados."""
        codigo_texto = self.tela.codigo_produto.text().strip()

        if not codigo_texto:
            linhas = self.tela.tableView_3.selectionModel().selectedRows()
            if not linhas:
                QMessageBox.warning(
                    self.tela, "Aviso", "Selecione um produto na tabela."
                )
                return

            item_id = self.modelo.item(linhas[0].row(), 0)
            if item_id is None:
                QMessageBox.warning(
                    self.tela, "Aviso", "Não foi possível identificar o produto."
                )
                return
            codigo_texto = item_id.text()

        try:
            id_produto = int(codigo_texto)
        except ValueError:
            QMessageBox.warning(self.tela, "Aviso", "O código do produto é inválido.")
            return

        resposta = QMessageBox.question(
            self.tela,
            "Confirmar exclusão",
            f"Deseja realmente excluir o produto de código {id_produto}?",
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
            cursor.execute(
                "DELETE FROM produtos WHERE id_produto = %s", (id_produto,)
            )
            conexao.commit()

            if cursor.rowcount == 0:
                QMessageBox.warning(
                    self.tela, "Aviso", "Produto não encontrado no banco."
                )
            else:
                QMessageBox.information(
                    self.tela, "Sucesso", "Produto excluído com sucesso!"
                )

            self.limpar_campos()
            self.carregar_dados_na_tabela()

        except Exception as erro:
            if conexao is not None:
                conexao.rollback()
            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível excluir o produto:\n{erro}",
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None:
                conexao.close()

    def limpar_campos(self):
        """Limpa os campos do formulário e a seleção da tabela."""
        self.tela.codigo_produto.clear()
        self.tela.nome_produto.clear()
        self.tela.categoria_produto.setCurrentIndex(0)
        self.tela.edit_email_3.clear()
        self.tela.edit_cidade_3.clear()
        self.tela.tableView_3.clearSelection()
        self.tela.nome_produto.setFocus()
