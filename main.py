import sys
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QHeaderView, QDialog, \
    QAbstractItemView
import sqlite3

from PyQt5.uic.properties import QtCore


class Dialog(QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi('dialog.ui', self)
        self.setModal(True)


class MyWidget(QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi('main.ui', self)

        self.loadTable()
        
        self.search_btn.clicked.connect(self.search)
        self.save_btn.clicked.connect(self.saveTable)
        self.add_teacherbtn.clicked.connect(self.addTeacher)
        self.delete_teacherbtn.clicked.connect(self.delete)
        self.add_rowbtn.clicked.connect(self.addRow)
        self.refreshbtn.clicked.connect(self.refresh)
        self.editbtn.clicked.connect(self.edit)
        self.refreshbtn.setIcon(QIcon('image/refresh2.png'))
        self.save_btn.setIcon(QIcon('image/save.png'))
        self.editbtn.setIcon(QIcon('image/edit.png'))
        self.add_teacherbtn.setIcon(QIcon('image/add_teacher.png'))
        self.delete_teacherbtn.setIcon(QIcon('image/delete.png'))

    def edit(self):
        self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

    def refresh(self):
        self.loadTable()
        self.linerequest.setText('')
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def delete(self):
        response = Dialog()
        response.exec_()
        if response.result() == 1:
            try:
                row = self.tableWidget.currentRow()
                id = int(self.tableWidget.item(row, 0).text())
                cur = self.con.cursor()

                cur.execute(f"""DELETE FROM users WHERE user_ID={id};
                                            """)
                cur.execute(f"""DELETE FROM goals WHERE user_ID={id};
                                                            """)

                self.tableWidget.removeRow(row)
                self.con.commit()
            except:
                print('Delete error')
                pass

    def search(self):
        request = self.linerequest.text()
        users = [f"""Where user_fname LIKE '%{request}%' or user_sname LIKE '%{request}%'""",
                 f"""Where goals.goals_theme LIKE '%{request}%' and goals.user_ID = users.user_ID"""]
        self.loadTable(users)
        self.linerequest.setText('')

    def addRow(self):
        self.loadTable()
        self.tableWidget.setRowCount(self.row_count + 1)
        self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

    def addTeacher(self):
        try:
            cur = self.con.cursor()
            row = self.row_count

            data = [self.tableWidget.item(row, 1).text(),
                    self.tableWidget.item(row, 2).text(), self.tableWidget.item(row, 3).text(),
                    self.tableWidget.item(row, 4).text(), self.tableWidget.item(row, 5).text()]
            print(data)
            cur.execute(f"""INSERT INTO users (user_fname, user_sname, user_category)
    VALUES('{data[0]}', '{data[1]}', '{data[2]}');""")

            self.con.commit()
            id = cur.execute(
                f"""SELECT user_ID FROM users WHERE user_fname='{data[0]}' and user_sname='{data[1]}';""").fetchall()[
                0][0]

            cur.execute(f"""INSERT INTO goals (goals_theme, goal_aproved, user_ID)
                    VALUES('{data[3]}', '{data[4]}', '{id}');""")
            self.con.commit()
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        except:
            try:
                cur = self.con.cursor()
                row = self.row_count

                data = [self.tableWidget.item(row, 1).text(),
                        self.tableWidget.item(row, 2).text(), self.tableWidget.item(row, 3).text()]

                cur.execute(f"""INSERT INTO users (user_fname, user_sname, user_category)
                    VALUES('{data[0]}', '{data[1]}', '{data[2]}');""")

                self.con.commit()
                id = cur.execute(
                    f"""SELECT user_ID FROM users WHERE user_fname='{data[0]}' and user_sname='{data[1]}';""").fetchall()[
                    0][0]

                cur.execute(f"""INSERT INTO goals (goals_theme, goal_aproved, user_ID)
                                    VALUES('', '', '{id}');""")
                self.con.commit()
                self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            except:
                pass

    def loadTable(self, request=None):

        if request is None:
            request = ['', '']
        self.con = sqlite3.connect('database/pdg.db')
        cur = self.con.cursor()

        users = cur.execute("""SELECT * FROM users 
                            """ + request[0]).fetchall()

        if len(users) == 0:
            users = cur.execute("""SELECT users.user_ID, users.user_fname, users.user_sname, users.user_category FROM goals, users 
                                        """ + request[1]).fetchall()
        
        self.row_count = len(users)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(self.row_count)
        self.tableWidget.setHorizontalHeaderLabels(
            ('ID', 'Имя', 'Фамилия', 'Уровень', 'Тема ЦПР', 'Утверждено')
        )
        self.tableWidget.hideColumn(0)
        row = 0
        for tup in users:

            col = 0
            goal = cur.execute(f"""SELECT goals_theme, goal_aproved FROM goals Where user_ID = {tup[0]}
                                        """).fetchall()
            try:
                tup += goal[0]
            except IndexError:
                pass

            for item in tup:
                cellinfo = QTableWidgetItem(str(item))
                self.tableWidget.setItem(row, col, cellinfo)
                col += 1

            row += 1
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

    def saveTable(self):
        response = Dialog()
        response.exec_()
        if response.result() == 1:
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for i in range(self.row_count):
                user_table = []
                goal_table = []
                user_table = [self.tableWidget.item(i, 0).text(), self.tableWidget.item(i, 1).text(),
                              self.tableWidget.item(i, 2).text(), self.tableWidget.item(i, 3).text(), ]

                try:
                    goal_table = [self.tableWidget.item(i, 4).text(), self.tableWidget.item(i, 5).text()]
                except:
                    pass

                con = sqlite3.connect('database/pdg.db')
                con.execute(f"""UPDATE users
    SET user_fname = '{user_table[1]}', user_sname = '{user_table[2]}', user_category = '{user_table[3]}'
    WHERE user_ID={int(user_table[0])};""")
                if goal_table:

                    con.execute(f"""UPDATE goals
                    SET goals_theme = '{goal_table[0]}', goal_aproved = '{goal_table[1]}'
                    WHERE user_ID={int(user_table[0])};""")
                con.commit()


"""SELECT users.user_ID, users.user_fname, users.user_sname, goals.goals_theme 
FROM users
INNER JOIN goals ON goals.user_ID =users.user_ID;"""

if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = MyWidget()

    ex.show()

    sys.exit(app.exec())
