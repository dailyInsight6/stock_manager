#####################################################
# MyStocker: A program showing my stock portfolio   #
#####################################################
# 2018-07-03 / Koreattle / Created					#
#####################################################

import sys
import sqlite3
import os

from datetime import datetime, date

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui
from PyQt5.QtCore import pyqtSlot

from iexfinance import Stock

from ConfirmDialog import ConfirmDialog

sys.setrecursionlimit(1500)

path = os.path.dirname(os.path.abspath(__file__))
qt_file = os.path.join(path, "UI/MyStocker.ui")  # Enter UI file here.
form_class = uic.loadUiType(qt_file)[0]


class MainForm(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.init_widget()

    def init_widget(self):
        """
        Initialize
        :param: N/A
        :return: N/A
        """
        today = datetime.today()

        this_date = date(today.year, today.month, today.day)
        start_date = date(2018, 2, 26)  # Start date of my investment
        difference = str((this_date - start_date).days) + " days"
        self.investPeriod.setText(difference)

        update_time = "updated " + datetime.strftime(today, "%Y-%m-%d %H:%M:%S")
        self.updateTime.setText(update_time)

        self.renew_portfolio()
        self.set_signal()

    def set_signal(self):

        self.portfolioTreeWidget.itemChanged.connect(self.portfolio_item_changed)
        self.portfolioTreeWidget.itemDoubleClicked.connect(self.portfolio_item_doubleclick)

        self.currentTableWidget.itemChanged.connect(self.current_item_changed)

        self.currentInsertBtn.clicked.connect(lambda: self.row_insert(self.currentTableWidget))
        self.currentDelBtn.clicked.connect(lambda: self.row_delete(self.currentTableWidget))
        self.currentSaveBtn.clicked.connect(lambda: self.row_save(self.currentTableWidget))
        self.currentCancelBtn.clicked.connect(lambda: self.row_cancel(self.currentTableWidget))

        self.historyInsertBtn.clicked.connect(lambda: self.row_insert(self.historyTableWidget))
        self.historyDelBtn.clicked.connect(lambda: self.row_delete(self.historyTableWidget))
        self.historySaveBtn.clicked.connect(lambda: self.row_save(self.historyTableWidget))
        self.historyCancelBtn.clicked.connect(lambda: self.row_cancel(self.historyTableWidget))

    def renew_portfolio(self):
        """
        Update my portfolio data
        :param: N/A
        :return:
        """
        my_portfolio = DataHandler()
        con = my_portfolio.connect()

        # Variables List
        # Used for Current Section
        self.current_price = 0
        self.total_value = 0
        self.profit_cash = 0
        self.profit_percentage = 0
        self.update_list = list()
        # Used for My Portfolio section
        self.my_stock = 0
        self.my_profit_cash = 0

        # History Section
        query_statement = "SELECT * FROM history_stock ORDER BY date"
        data = my_portfolio.execute(con, query_statement).fetchall()

        if len(data) > 0:
            history_table_widget = self.historyTableWidget
            row_cnt = len(data)
            col_cnt = history_table_widget.columnCount()
            history_table_widget.setRowCount(row_cnt)
            history_table_widget.setColumnCount(col_cnt)

            for i in range(row_cnt):
                for j in range(col_cnt):
                    if j < 5:
                        history_table_widget.setItem(i, j, QTableWidgetItem(str(data[i][j])))
                    else:
                        if j == 5:
                            self.history_profit_cash = round((data[i][3] - data[i][2]) * data[i][4], 2)
                            history_table_widget.setItem(i, j, QTableWidgetItem(str(self.history_profit_cash)))
                        elif j == 6:
                            self.history_profit_percentage = round(
                                (self.history_profit_cash / (data[i][2] * data[i][4])) * 100, 2)
                            history_table_widget.setItem(i, j, QTableWidgetItem(str(self.history_profit_percentage)))

            self.history_row_cnt = row_cnt

        # Current Section
        query_statement = "SELECT * FROM current_stock"
        data = my_portfolio.execute(con, query_statement).fetchall()
        if len(data) > 0:
            current_table_widget = self.currentTableWidget
            row_cnt = len(data)
            col_cnt = current_table_widget.columnCount()
            current_table_widget.setRowCount(row_cnt)
            current_table_widget.setColumnCount(col_cnt)

            current_table_widget.blockSignals(True)

            for i in range(row_cnt):
                for j in range(col_cnt):
                    if j < 3:
                        current_table_widget.setItem(i, j, QTableWidgetItem(str(data[i][j])))
                        if j in (1, 2):
                            item = current_table_widget.item(i, j)
                            item.setBackground(QtGui.QColor(230, 230, 230))
                    else:
                        stock_info = Stock(str(data[i][0]))
                        self.current_price = round(stock_info.get_price(), 2)

                        if j == 3:
                            current_table_widget.setItem(i, j, QTableWidgetItem(str(self.current_price)))
                        elif j == 4:
                            self.total_value = round(float(self.current_price) * int(data[i][1]), 2)
                            current_table_widget.setItem(i, j, QTableWidgetItem(str(self.total_value)))
                            self.my_stock = self.my_stock + self.total_value
                        elif j == 5:
                            self.profit_cash = round(
                                (float(self.current_price) * int(data[i][1])) - (float(data[i][2]) * int(data[i][1])), 2)
                            current_table_widget.setItem(i, j, QTableWidgetItem(str(self.profit_cash)))
                            self.my_profit_cash = self.my_profit_cash + self.profit_cash
                        elif j == 6:
                            input = float(data[i][2]) * int(data[i][1])
                            self.profit_percentage = round(
                                (((float(self.current_price) * int(data[i][1])) - input) * 100) / input, 2)
                            current_table_widget.setItem(i, j, QTableWidgetItem(str(self.profit_percentage)))

                update_statement = "UPDATE current_stock SET current_price = '%0.2f', total_value = '%0.2f', profit_cash = '%0.2f', profit_percentage = '%0.2f' WHERE item = '%s'" % (
                self.current_price, self.total_value, self.profit_cash, self.profit_percentage, data[i][0])
                self.update_list.append(update_statement)

            current_table_widget.blockSignals(False)

        # Portfolio Section
        query_statement = "SELECT * FROM my_portfolio"
        data = my_portfolio.execute(con, query_statement).fetchone()
        if data and len(data) > 0:
            data_idx = 0
            portfolio_widget = self.portfolioTreeWidget
            portfolio_widget.setColumnWidth(0, 150)

            self.current_row_cnt = row_cnt
            self.add_row_num = 0

            # It prevents a tree widget from emitting signals according to its changes
            self.portfolioTreeWidget.blockSignals(True)

            # Fill my portfolio section with data
            for i in range(portfolio_widget.topLevelItemCount()):
                child_cnt = portfolio_widget.topLevelItem(i).childCount()

                # sub-trees exists
                if child_cnt > 0:
                    portfolio_widget.topLevelItem(i).setExpanded(True)
                    current_value = "$ " + str(round(self.my_stock + float(data[3][2:]), 2))
                    portfolio_widget.topLevelItem(i).setText(1, current_value)
                    data_idx = data_idx + 1

                    update_statement = "UPDATE my_portfolio SET current_value = '%s'" % (current_value)
                    self.update_list.append(update_statement)

                    for j in range(child_cnt):
                        if j == 0:
                            self.my_stock = "$ " + str(round(self.my_stock, 2))
                            portfolio_widget.topLevelItem(i).child(j).setText(1, self.my_stock)
                        elif j == 1:
                            portfolio_widget.topLevelItem(i).child(j).setText(1, str(data[data_idx]))
                        elif j == 2:
                            if float(self.my_profit_cash) > 0:
                                portfolio_widget.topLevelItem(i).child(j).setForeground(1, QtGui.QColor("red"))
                            else:
                                portfolio_widget.topLevelItem(i).child(j).setForeground(1, QtGui.QColor("blue"))

                            self.my_profit_cash = "$ " + str(round(self.my_profit_cash, 2))
                            portfolio_widget.topLevelItem(i).child(j).setText(1, str(self.my_profit_cash))

                        data_idx = data_idx + 1

                    update_statement = "UPDATE my_portfolio SET current_stock = '%s', current_profit = '%s'" % (
                    self.my_stock, self.my_profit_cash)
                    self.update_list.append(update_statement)
                else:
                    portfolio_widget.topLevelItem(i).setText(1, str(data[data_idx]))
                    data_idx = data_idx + 1

            self.portfolioTreeWidget.blockSignals(False)

        # Data update in DB
        for i in range(len(self.update_list)):
            my_portfolio.execute(con, self.update_list[i])

        my_portfolio.disconnect(con)

    @pyqtSlot()
    def portfolio_item_doubleclick(self):
        self.previous_current_cash = self.portfolioTreeWidget.currentItem().text(1)

    @pyqtSlot()
    def portfolio_item_changed(self):

        item = self.portfolioTreeWidget.currentItem()

        update_statement = ""

        # self.setUpdatesEnabled(False)
        self.portfolioTreeWidget.blockSignals(True)

        if item.text(0) == "Total Input":
            update_statement = "UPDATE my_portfolio SET total_input = '{:s}'".format(item.text(1))
        elif item.text(0) == "Cash":
            previous_total_value = float(self.portfolioTreeWidget.topLevelItem(1).text(1)[2:])
            previous_current_cash = float(self.previous_current_cash[2:])
            new_current_cash = float(self.portfolioTreeWidget.currentItem().text(1)[2:])

            new_total_value = "$ " + str(round(previous_total_value + (new_current_cash - previous_current_cash), 2))

            self.portfolioTreeWidget.topLevelItem(1).setText(1, new_total_value)

            update_statement = "UPDATE my_portfolio SET current_value = '{:s}', current_cash = '{:s}'".format(
                new_total_value, self.portfolioTreeWidget.currentItem().text(1))

        self.portfolioTreeWidget.blockSignals(False)

        my_portfolio = DataHandler()
        con = my_portfolio.connect()
        my_portfolio.execute(con, update_statement)
        my_portfolio.disconnect(con)

    @pyqtSlot()
    def current_item_changed(self):
        if self.currentTableWidget.currentRow() < self.current_row_cnt:
            self.currentTableWidget.blockSignals(True)

            target = self.currentTableWidget.currentItem()
            item = self.currentTableWidget.item(target.row(), 0).text()

            update_statement = ""

            if target.column() == 1:
                update_statement = "UPDATE current_stock SET quantity = '{:d}' WHERE item = '{:s}'".format(int(target.text()), item)
            elif target.column() == 2:
                update_statement = "UPDATE current_stock SET purchase_price = '{:s}' WHERE item = '{:s}'".format(
                    target.text(), item)

            my_current = DataHandler()
            con = my_current.connect()
            my_current.execute(con, update_statement)
            my_current.disconnect(con)

            self.currentTableWidget.blockSignals(False)

            self.renew_portfolio()

    @pyqtSlot()
    def update_data(self):
        self.renew_portfolio()

        update_time = "updated " + datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        self.updateTime.setText(update_time)

    @pyqtSlot(QTableWidget)
    def row_insert(self, table_widget: QTableWidget):

        if table_widget.objectName() == "currentTableWidget":
            self.currentSaveBtn.setEnabled(True)
            self.currentCancelBtn.setEnabled(True)
            self.currentDelBtn.setEnabled(False)

            table_widget.insertRow(self.current_row_cnt)

        elif table_widget.objectName() == "historyTableWidget":
            self.historySaveBtn.setEnabled(True)
            self.historyCancelBtn.setEnabled(True)
            self.historyDelBtn.setEnabled(False)

            table_widget.insertRow(self.history_row_cnt)

            table_widget.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)

        self.add_row_num = self.add_row_num + 1

    @pyqtSlot(QTableWidget)
    def row_delete(self, table_widget: QTableWidget):

        self.main_dialog = QDialog()
        self.confirm_dialog = ConfirmDialog()
        self.confirm_dialog.setupUi(self.main_dialog)

        self.main_dialog.show()

        selected_row = table_widget.currentRow()

        self.confirm_dialog.buttonBox.accepted.connect(lambda: self.del_accepted(table_widget, selected_row))
        self.confirm_dialog.buttonBox.rejected.connect(self.del_rejected)

    @pyqtSlot(QTableWidget, int)
    def del_accepted(self, table_widget: QTableWidget, selected_row):

        if table_widget.objectName() == "currentTableWidget":
            del_item = table_widget.item(selected_row, 0).text()
            delete_statement = "DELETE FROM current_stock WHERE item = '{:s}'".format(del_item)
        elif table_widget.objectName() == "historyTableWidget":

            del_date = table_widget.item(selected_row, 0).text()
            del_item = table_widget.item(selected_row, 1).text()
            del_sell_price = float(table_widget.item(selected_row, 3).text())
            del_sell_qnt = int(table_widget.item(selected_row, 4).text())

            delete_statement = "DELETE FROM history_stock WHERE date = '{:s}' AND item = '{:s}' AND sell_price = '{:f}' AND sell_quantity = '{:d}'".format(
                del_date, del_item, del_sell_price, del_sell_qnt)

        # Data delete in DB
        my_data = DataHandler()
        con = my_data.connect()
        my_data.execute(con, delete_statement)

        table_widget.removeRow(selected_row)

        if table_widget.objectName() == "historyTableWidget":

            history_row_cnt = table_widget.rowCount()
            self.history_total_profit_cash = 0
            self.history_total_profit_percentage = 0

            for i in range(history_row_cnt):
                self.history_total_profit_cash = self.history_total_profit_cash + float(table_widget.item(i, 5).text())
                self.history_total_profit_percentage = self.history_total_profit_percentage + float(
                    table_widget.item(i, 6).text())

                culm_profit_cash = "$ " + str(round(self.history_total_profit_cash, 2))
                culm_profit_percentage = str(round(self.history_total_profit_percentage / history_row_cnt, 2)) + "%"

            update_statement = "UPDATE my_portfolio SET culm_profit_cash = '{:s}', culm_profit_percentage = '{:s}'".format(
                culm_profit_cash, culm_profit_percentage)
            my_data.execute(con, update_statement)

        my_data.disconnect(con)
        self.main_dialog.close()
        self.renew_portfolio()

    @pyqtSlot()
    def del_rejected(self):
        self.main_dialog.close()

    @pyqtSlot(QTableWidget)
    def row_save(self, table_widget: QTableWidget):

        self.p_cash = 0
        self.p_percentage = 0
        self.insert_list = list()
        self.update_statement = ""

        if table_widget.objectName() == "currentTableWidget":

            self.item = ""
            self.qnt = 0
            self.p_price = 0
            self.c_price = 0
            self.t_value = 0

            self.portfolioTreeWidget.blockSignals(True)

            for i in range(self.current_row_cnt, self.current_row_cnt + self.add_row_num):
                for j in range(table_widget.columnCount()):
                    if j == 0:
                        self.item = table_widget.item(i, j).text()
                    elif j == 1:
                        self.qnt = table_widget.item(i, j).text()
                        table_widget.item(i, j).setBackground(QtGui.QColor(230, 230, 230))
                    elif j == 2:
                        self.p_price = table_widget.item(i, j).text()
                        table_widget.item(i, j).setBackground(QtGui.QColor(230, 230, 230))
                    elif j == 3:
                        stock_info = Stock(str(table_widget.item(i, 0).text()))
                        self.c_price = round(stock_info.get_price(), 2)
                    elif j == 4:
                        self.t_value = round(float(self.c_price) * int(self.qnt), 2)
                        table_widget.setItem(i, j, QTableWidgetItem(str(self.t_value)))
                    elif j == 5:
                        self.p_cash = round(
                            (float(self.c_price) * int(self.qnt)) - (float(self.p_price) * int(self.qnt)), 2)
                        table_widget.setItem(i, j, QTableWidgetItem(str(self.p_cash)))
                    elif j == 6:
                        input = float(self.p_price) * int(self.qnt)
                        self.p_percentage = round((((float(self.c_price) * int(self.qnt)) - input) * 100) / input, 2)
                        table_widget.setItem(i, j, QTableWidgetItem(str(self.p_percentage)))

                insert_statement = "INSERT INTO current_stock VALUES ('{:s}', '{:s}', '{:s}', '{:0.2f}', '{:0.2f}', '{:0.2f}', '{:0.2f}')".format(
                    self.item, self.qnt, self.p_price, self.c_price, self.t_value, self.p_cash, self.p_percentage)

                self.insert_list.append(insert_statement)

            self.portfolioTreeWidget.blockSignals(False)

            self.currentSaveBtn.setEnabled(False)
            self.currentCancelBtn.setEnabled(False)
            self.currentDelBtn.setEnabled(True)

        elif table_widget.objectName() == "historyTableWidget":

            self.date = ""
            self.item = ""
            self.b_price = 0
            self.s_price = 0
            self.s_qnt = 0

            self.history_total_profit_cash = 0
            self.history_total_profit_percentage = 0

            for i in range(self.history_row_cnt + self.add_row_num):
                if i < self.history_row_cnt:
                    self.history_total_profit_cash = self.history_total_profit_cash + float(
                        table_widget.item(i, 5).text())
                    self.history_total_profit_percentage = self.history_total_profit_percentage + float(
                        table_widget.item(i, 6).text())
                else:
                    for j in range(table_widget.columnCount()):
                        if j == 0:
                            self.date = table_widget.item(i, j).text()
                        elif j == 1:
                            self.item = table_widget.item(i, j).text()
                        elif j == 2:
                            self.b_price = float(table_widget.item(i, j).text())
                        elif j == 3:
                            self.s_price = float(table_widget.item(i, j).text())
                        elif j == 4:
                            self.s_qnt = int(table_widget.item(i, j).text())
                        elif j == 5:
                            self.p_cash = round((self.s_price - self.b_price) * self.s_qnt, 2)
                            table_widget.setItem(i, j, QTableWidgetItem(str(self.p_cash)))
                            self.history_total_profit_cash = self.history_total_profit_cash + self.p_cash
                        elif j == 6:
                            self.p_percentage = round((self.p_cash / (self.b_price * self.s_qnt)) * 100, 2)
                            table_widget.setItem(i, j, QTableWidgetItem(str(self.p_percentage)))
                            self.history_total_profit_percentage = self.history_total_profit_percentage + self.p_percentage

                    insert_statement = "INSERT INTO history_stock VALUES ('{:s}', '{:s}', '{:0.2f}', '{:0.2f}', '{:d}', '{:0.2f}', '{:0.2f}')".format(
                        self.date, self.item, self.b_price, self.s_price, self.s_qnt, self.p_cash, self.p_percentage)

                    self.insert_list.append(insert_statement)

            culm_profit_cash = "$ " + str(round(self.history_total_profit_cash, 2))
            culm_profit_percentage = str(round(self.history_total_profit_percentage / table_widget.rowCount(), 2)) + "%"

            self.update_statement = "UPDATE my_portfolio SET culm_profit_cash = '{:s}', culm_profit_percentage = '{:s}'".format(
                culm_profit_cash, culm_profit_percentage)

            self.historySaveBtn.setEnabled(False)
            self.historyCancelBtn.setEnabled(False)
            self.historyDelBtn.setEnabled(True)

            table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Data update in DB
        my_data = DataHandler()
        con = my_data.connect()

        for i in range(len(self.insert_list)):
            my_data.execute(con, self.insert_list[i])

        if self.update_statement != "":
            my_data.execute(con, self.update_statement)

        my_data.disconnect(con)

        self.renew_portfolio()

    @pyqtSlot(QTableWidget)
    def row_cancel(self, table_widget: QTableWidget):

        for i in range(self.add_row_num):
            idx = table_widget.rowCount() - 1
            table_widget.removeRow(idx)

        self.add_row_num = 0

        if table_widget.objectName() == "currentTableWidget":
            self.currentSaveBtn.setEnabled(False)
            self.currentCancelBtn.setEnabled(False)
            self.currentDelBtn.setEnabled(True)
        elif table_widget.objectName() == "historyTableWidget":
            self.historySaveBtn.setEnabled(False)
            self.historyCancelBtn.setEnabled(False)
            self.historyDelBtn.setEnabled(True)
            table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)


class DataHandler():
    def connect(self):
        con = sqlite3.connect(os.path.join(path, "Data/MyStocker.db"))
        return con

    def disconnect(self, con):
        con.commit()
        con.close()

    def execute(self, con, text):
        cursor = con.cursor()
        cursor.execute(text)
        return cursor


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()
    sys.exit(app.exec())
