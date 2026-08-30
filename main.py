#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QMessageBox, QDialog, QCheckBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon

# Инициализация БД
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.init_db import (
    init_database, add_client, get_all_clients, get_client_by_id,
    delete_client, save_document, get_all_documents
)

# Данные исполнителя (отредактируйте под себя)
EXECUTOR_DATA = {
    'name': 'ИП Гимазов Венер Вагизович',
    'inn': '026501701480',
    'account': '40802810006000012416',
    'bank': 'ОТДЕЛЕНИЕ № 8598 СБЕРБАНКА РОССИИ Г. УФА',
    'bik': '048073601',
    'corr_account': '30101810300000000601'
}

class ClientManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_table()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Форма для добавления клиента
        form_layout = QFormLayout()
        
        self.client_name = QLineEdit()
        self.client_inn = QLineEdit()
        self.client_account = QLineEdit()
        self.client_bik = QLineEdit()
        self.client_address = QLineEdit()
        
        form_layout.addRow('Название организации:', self.client_name)
        form_layout.addRow('ИНН:', self.client_inn)
        form_layout.addRow('Расчетный счет:', self.client_account)
        form_layout.addRow('БИК:', self.client_bik)
        form_layout.addRow('Юридический адрес:', self.client_address)
        
        btn_add = QPushButton('Добавить заказчика')
        btn_add.clicked.connect(self.add_client)
        form_layout.addRow(btn_add)
        
        layout.addLayout(form_layout)
        
        # Таблица клиентов
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Название', 'ИНН', 'Счет', 'БИК', 'Адрес'])
        self.table.setColumnHidden(0, True)
        self.table.cellDoubleClicked.connect(self.delete_client)
        layout.addWidget(QLabel('Список заказчиков (двойной клик для удаления):'))
        layout.addWidget(self.table)
    
    def add_client(self):
        name = self.client_name.text().strip()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Введите название организации')
            return
        
        if add_client(
            name,
            self.client_inn.text().strip(),
            self.client_account.text().strip(),
            self.client_bik.text().strip(),
            self.client_address.text().strip()
        ):
            QMessageBox.information(self, 'Успех', 'Заказчик добавлен')
            self.client_name.clear()
            self.client_inn.clear()
            self.client_account.clear()
            self.client_bik.clear()
            self.client_address.clear()
            self.refresh_table()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Заказчик с таким названием уже существует')
    
    def refresh_table(self):
        self.table.setRowCount(0)
        clients = get_all_clients()
        for row, client in enumerate(clients):
            self.table.insertRow(row)
            for col, value in enumerate(client):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
    
    def delete_client(self, row, col):
        client_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, 'Подтверждение', 'Удалить заказчика?')
        if reply == QMessageBox.StandardButton.Yes:
            delete_client(client_id)
            self.refresh_table()

class DocumentGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Тип документа
        self.doc_type = QComboBox()
        self.doc_type.addItem('Счет на оплату', 'invoice')
        self.doc_type.addItem('Акт выполненных работ', 'act')
        form_layout.addRow('Тип документа:', self.doc_type)
        
        # Номер и дата
        self.doc_number = QLineEdit()
        self.doc_date = QLineEdit()
        self.doc_date.setText(datetime.now().strftime('%d.%m.%Y'))
        form_layout.addRow('Номер документа:', self.doc_number)
        form_layout.addRow('Дата документа:', self.doc_date)
        
        # Заказчик
        self.client_select = QComboBox()
        self.refresh_clients()
        form_layout.addRow('Заказчик:', self.client_select)
        
        # Маршрут
        self.route = QLineEdit()
        self.route.setPlaceholderText('Казань - Екатеринбург')
        form_layout.addRow('Маршрут:', self.route)
        
        # Даты
        self.start_date = QLineEdit()
        self.end_date = QLineEdit()
        form_layout.addRow('Дата начала:', self.start_date)
        form_layout.addRow('Дата окончания:', self.end_date)
        
        # Сумма и НДС
        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(999999999)
        form_layout.addRow('Сумма (руб.):', self.amount)
        
        self.use_nds = QCheckBox('Добавить НДС')
        self.use_nds.stateChanged.connect(self.toggle_nds)
        form_layout.addRow('', self.use_nds)
        
        self.nds_rate = QDoubleSpinBox()
        self.nds_rate.setValue(18)
        self.nds_rate.setMaximum(100)
        self.nds_rate.setEnabled(False)
        form_layout.addRow('Ставка НДС (%):', self.nds_rate)
        
        # Кнопка сохранить
        btn_save = QPushButton('Сохранить документ')
        btn_save.clicked.connect(self.save_document)
        form_layout.addRow(btn_save)
        
        layout.addLayout(form_layout)
        layout.addStretch()
    
    def refresh_clients(self):
        self.client_select.clear()
        clients = get_all_clients()
        for client in clients:
            self.client_select.addItem(client[1], client[0])
    
    def toggle_nds(self):
        self.nds_rate.setEnabled(self.use_nds.isChecked())
    
    def save_document(self):
        if not self.doc_number.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите номер документа')
            return
        
        if self.client_select.currentIndex() == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите заказчика')
            return
        
        if self.amount.value() == 0:
            QMessageBox.warning(self, 'Ош��бка', 'Введите сумму')
            return
        
        doc_type = self.doc_type.currentData()
        client_id = self.client_select.currentData()
        nds_rate = self.nds_rate.value() if self.use_nds.isChecked() else 0
        
        save_document(
            doc_type,
            self.doc_number.text(),
            self.doc_date.text(),
            client_id,
            self.route.text(),
            self.start_date.text(),
            self.end_date.text(),
            self.amount.value(),
            nds_rate
        )
        
        QMessageBox.information(self, 'Успех', 'Документ сохранен в базе данных')
        self.clear_form()
    
    def clear_form(self):
        self.doc_number.clear()
        self.route.clear()
        self.start_date.clear()
        self.end_date.clear()
        self.amount.setValue(0)
        self.use_nds.setChecked(False)

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_table()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        btn_refresh = QPushButton('Обновить')
        btn_refresh.clicked.connect(self.refresh_table)
        layout.addWidget(btn_refresh)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Тип', 'Номер', 'Дата', 'Заказчик', 'Сумма', 'Дата создания'])
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)
    
    def refresh_table(self):
        self.table.setRowCount(0)
        documents = get_all_documents()
        for row, doc in enumerate(documents):
            self.table.insertRow(row)
            for col, value in enumerate(doc):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Генератор счетов и актов')
        self.setGeometry(100, 100, 1000, 600)
        
        # Вкладки
        tabs = QTabWidget()
        
        self.client_manager = ClientManagerWidget()
        self.doc_generator = DocumentGeneratorWidget()
        self.history = HistoryWidget()
        
        tabs.addTab(self.doc_generator, '📄 Создать документ')
        tabs.addTab(self.client_manager, '👥 Заказчики')
        tabs.addTab(self.history, '📋 История')
        
        self.setCentralWidget(tabs)
    
    def closeEvent(self, event):
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
