import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QDialog


class Coffee(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.select_data)
        self.pushButton_add.clicked.connect(self.open_add_form)
        self.pushButton_edit.clicked.connect(self.open_edit_form)
        self.textEdit.setPlainText("SELECT * FROM coffee")
        self.select_data()

    def select_data(self):
        query = self.textEdit.toPlainText()
        res = self.connection.cursor().execute(query).fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        self.connection.close()

    def open_edit_form(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        if not rows:
            return
        coffee_id = min(self.tableWidget.item(i, 0).text() for i in rows)

        selected_row_data = self.get_coffee_data(coffee_id)

        edit_form = AddEditForm(data=selected_row_data)
        edit_form.setWindowTitle("Edit Coffee")
        edit_form.exec_()

    def get_coffee_data(self, coffee_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM coffee WHERE id=?", (coffee_id,))
        return cursor.fetchone()

    def open_add_form(self):
        add_form = AddEditForm()
        add_form.setWindowTitle("Add Coffee")
        add_form.exec_()


class AddEditForm(QDialog):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.pushButton_save.clicked.connect(self.save_data)
        self.pushButton_cancel.clicked.connect(self.hide)

        if data:
            self.fill_form(data)
        else:
            self.lineEdit1.setText("AUTO")

    def fill_form(self, data):
        self.lineEdit1.setText(str(data[0]))
        self.lineEdit2.setText(data[1])
        self.lineEdit3.setText(str(data[2]))
        self.comboBox.setCurrentText(str(data[3]))
        self.lineEdit4.setText(data[4])
        self.spinBox_price.setValue(data[5])
        self.spinBox_pack_size.setValue(data[6])

    def save_data(self):
        sort = self.lineEdit2.text()
        roasting = self.lineEdit3.text()
        in_grains = self.comboBox.currentText()
        description = self.lineEdit4.text()
        price = self.spinBox_price.value()
        pack_size = self.spinBox_pack_size.value()
        coffee_id = self.lineEdit1.text()

        connection = sqlite3.connect("coffee.sqlite")
        cursor = connection.cursor()
        if coffee_id != "AUTO":
            cursor.execute("""UPDATE coffee 
                                 SET type_of_coffee=?, roast_degree=?, beans=?, description=?, price=?, size=?
                                 WHERE id=?""",
                           (sort, roasting, in_grains, description, price, pack_size, coffee_id))
        else:
            cursor.execute("""INSERT INTO coffee (type_of_coffee, roast_degree, beans, description, price, size) 
                                 VALUES (?, ?, ?, ?, ?, ?)""",
                           (sort, roasting, in_grains, description, price, pack_size))

        connection.commit()
        connection.close()

        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.exit(app.exec())