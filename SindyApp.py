import os
import sys
import datetime
from sindy import distribution, get_data, log_transformation, standardization, polynomialorder, thresholdvalue, result, visualization, calculate_env_data
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel, QTextEdit, QInputDialog, QDialog, QTableWidgetItem, QTableWidget, QLineEdit, QHBoxLayout, QGridLayout, QSizePolicy, QMainWindow, QAction
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QPixmap, QIcon

class Communicate(QObject):
    selected_columns_signal = pyqtSignal(str)
    selected_drop_signal = pyqtSignal(str)
    selected_ordernum_signal = pyqtSignal(str)
    thres_order_signal = pyqtSignal(str)
    thres_start_signal = pyqtSignal(str)
    thres_end_signal = pyqtSignal(str)
    result_lambda_signal = pyqtSignal(str)

communicator = Communicate()

class ImageWindow(QDialog):
    def __init__(self, plot_path):
        super(ImageWindow, self).__init__()
        self.plot_path = plot_path
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Environmental Factor Plot')
        #self.setGeometry(100, 100, 1500, 600)
        layout = QVBoxLayout()

        pixmap = QPixmap(self.plot_path)
        label = QLabel()
        label.setPixmap(pixmap)
        layout.addWidget(label)

        self.setLayout(layout)

class LambdaWindow(QDialog):
    def __init__(self, parent=None):
        super(LambdaWindow, self).__init__(parent)

        self.setWindowTitle('Insert Lambda')
        layout = QVBoxLayout()

        lamb_label = QLabel('Insert Lambda value (then, press Enter)')
        self.input_lamb = QLineEdit(self)
        self.input_lamb.returnPressed.connect(self.handle_lamb)
        self.show_lamb = QLabel("Lambda: ")
        self.done = QLabel("Not Ready")

        layout.addWidget(lamb_label)
        layout.addWidget(self.input_lamb)
        layout.addWidget(self.show_lamb)
        layout.addWidget(self.done)

        self.setLayout(layout)

    def handle_lamb(self):
        lamb_input = self.input_lamb.text()
        print(lamb_input)
        self.show_lamb.setText(f"Lambda: {lamb_input}")
        communicator.result_lambda_signal.emit(lamb_input)
        self.done.setText("Done. Go to 'Get Result'")

class ThresWindow(QDialog):
    def __init__(self, parent=None):
        super(ThresWindow, self).__init__(parent)

        self.setWindowTitle('Insert parameters')
        layout = QVBoxLayout()

        order_label = QLabel('Insert Order Number (then, press Enter)')
        self.input_order = QLineEdit(self)
        self.input_order.returnPressed.connect(self.handle_order)
        self.show_order = QLabel("Order: ")

        start_label = QLabel('Insert Start Number (then, press Enter)')
        self.input_start = QLineEdit(self)
        self.input_start.returnPressed.connect(self.handle_start)
        self.show_start = QLabel("Start: ")

        end_label = QLabel('Insert End Number (then, press Enter)')
        self.input_end = QLineEdit(self)
        self.input_end.returnPressed.connect(self.handle_end)
        self.show_end = QLabel("End: ")
        self.done = QLabel("Not Ready")

        layout.addWidget(order_label)
        layout.addWidget(self.input_order)
        layout.addWidget(self.show_order)

        layout.addWidget(start_label)
        layout.addWidget(self.input_start)
        layout.addWidget(self.show_start)

        layout.addWidget(end_label)
        layout.addWidget(self.input_end)
        layout.addWidget(self.show_end)
        layout.addWidget(self.done)

        self.setLayout(layout)

    def handle_order(self):
        order_input = self.input_order.text()
        print(order_input)
        self.show_order.setText(f"Order: {order_input}")
        communicator.thres_order_signal.emit(order_input)

    def handle_start(self):
        start_input = self.input_start.text()
        print(start_input)
        self.show_start.setText(f"Start: {start_input}")
        communicator.thres_start_signal.emit(start_input)

    def handle_end(self):
        end_input = self.input_end.text()
        print(end_input)
        self.show_end.setText(f"End: {end_input}")
        communicator.thres_end_signal.emit(end_input)
        self.done.setText("Done. Go to 'Plot Threshold'")

class TargetWindow(QDialog):
    def __init__(self, data, parent=None):
        super(TargetWindow, self).__init__(parent)
        self.data = data
        self.target = "No Target"
        self.order = "No Order"
        self.drop_list = []
        self.setWindowTitle('Choose Target Column and Input Data')
        layout = QVBoxLayout()
        label = QLabel('Data:')

        self.table_widget = QTableWidget(self)
        self.update_table_widget()

        target_btn = QPushButton('Choose Target Column', self)
        target_btn.clicked.connect(self.choose_target)

        drop_btn = QPushButton('Drop Columns', self)
        drop_btn.clicked.connect(self.choose_drop)

        order_btn = QPushButton('Choose Order Number', self)
        order_btn.clicked.connect(self.choose_ordernum)

        self.status = QLabel(f'Target: {self.target} | Order: {self.order}')
        self.status.setAlignment(Qt.AlignCenter)
        self.drop_status = QLabel(f'Dropped Columns: {self.drop_list}')
        self.drop_status.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(self.table_widget)
        layout.addWidget(target_btn)
        layout.addWidget(drop_btn)
        layout.addWidget(order_btn)
        layout.addWidget(self.status)
        layout.addWidget(self.drop_status)

        self.setLayout(layout)
        self.resize(1500, 600)

    def update_table_widget(self):
        self.table_widget.clear()

        self.table_widget.setColumnCount(len(self.data.columns))
        self.table_widget.setHorizontalHeaderLabels(self.data.columns)

        for col_index, column in enumerate(self.data.columns):
            self.table_widget.setColumnWidth(col_index, 100)

        for row_index, row in self.data.iterrows():
            self.table_widget.insertRow(row_index)
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(f'{value:.6f}')
                self.table_widget.setItem(row_index, col_index, item)

    def choose_target(self):
        selected, ok = QInputDialog.getItem(self, 'Choose Columns', 'Select target column:', self.data.columns, 0, False)
        if ok:
            self.target = selected
            self.drop_list.append(self.target)

            self.data = self.data.drop(columns=self.target)

            self.update_table_widget()
            print(f'Selected Columns: {self.target}')
            self.status.setText(f"Target: {self.target} | Order: {self.order}")
            self.drop_status.setText(f"Dropped Columns: {self.drop_list}")

            communicator.selected_columns_signal.emit(self.target)

    def choose_drop(self):
        selected, ok = QInputDialog.getItem(self, 'Choose Column', 'Select column to drop:', self.data.columns, 0, False)
        if ok:
            self.drop_column = selected
            self.drop_list.append(self.drop_column)

            self.data = self.data.drop(columns=self.drop_column)

            self.update_table_widget()
            print(f'Selected Columns: {self.drop_column}')
            self.drop_status.setText(f"Dropped Columns: {self.drop_list}")

            communicator.selected_drop_signal.emit(self.drop_column)

    def choose_ordernum(self):
        number_list = [f'{i}' for i in range(0,11)]
        selected, ok = QInputDialog.getItem(self, 'Choose Order Number', 'Select Order Number (Suggestion:6)', number_list, 0, False)
        if ok:
            self.order = selected

            print(f'Selected Order Number: {self.order}')
            self.status.setText(f"Target: {self.target} | Order: {self.order}")

            communicator.selected_ordernum_signal.emit(self.order)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data = None
        self.target = None
        self.input_data = None
        self.order_num = None
        self.thres_order = None
        self.start = None
        self.end = None
        self.lamb = None
        self.variable_list = None
        self.date_str = None
        self.folder_dir = None
        self.folder_path = None

        self.result_coeff = None
        self.result_lamb = None
        self.result_term = None
        self.result_expression = None
        self.env_file_name = None
        self.plot_path = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setWindowIcon(QIcon('icon.png'))
        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exit_program)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)

        main_layout = QHBoxLayout(central_widget)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        btn_select_file = QPushButton('Select Data File', self)
        btn_select_file.setToolTip('Choose the <b>CSV Data File</b>')
        btn_select_file.setStyleSheet('background-color: #336600; color: white;')
        btn_select_file.clicked.connect(self.show_file_dialog)

        self.lbl_selected_file = QLabel("Selected File: None")
        self.lbl_selected_file.setAlignment(Qt.AlignCenter)
        self.lbl_selected_file.setWordWrap(True)

        btn_folder_dir = QPushButton('Select Saving Directory (Mandatory)', self)
        btn_folder_dir.setToolTip('Choose the <b>Project Directory</b>')
        btn_folder_dir.setStyleSheet('background-color: #336600; color: white;')
        btn_folder_dir.clicked.connect(self.show_dir_dialog)

        self.lbl_selected_dir = QLabel("Saving Directory: None")
        self.lbl_selected_dir.setAlignment(Qt.AlignCenter)
        self.lbl_selected_dir.setWordWrap(True)

        btn_select_env = QPushButton('Select Environmental Factor File', self)
        btn_select_env.setToolTip('Choose the <b>Environmental Factor File</b>')
        btn_select_env.setStyleSheet('background-color: #006690; color: white;')
        btn_select_env.clicked.connect(self.show_env_dialog)

        self.lbl_selected_env = QLabel("Selected Env File: None")
        self.lbl_selected_env.setAlignment(Qt.AlignCenter)
        self.lbl_selected_env.setWordWrap(True)

        self.lbl_selected_env2 = QLabel("Not Available (Select Environmental Factor File First)")
        self.lbl_selected_env2.setAlignment(Qt.AlignCenter)
        self.lbl_selected_env2.setWordWrap(True)

        self.table_widget = QTableWidget(self)
        self.table_widget.setStyleSheet("border-style: solid;")
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_widget.setMaximumSize(1200, 600)

        btn_run = QPushButton('Display Data', self)
        btn_run.setToolTip('Click to display the data on the left')
        btn_run.setStyleSheet('background-color: #808080; color: white;')
        btn_run.clicked.connect(self.run_sindy)

        '''btn_exit = QPushButton('Exit', self)
        btn_exit.setToolTip('Click to exit the program')
        btn_exit.clicked.connect(self.exit_program)
        btn_exit.setStyleSheet('background-color: #808080; color: white;')'''

        env_btn = QPushButton('Environmental Factor', self)
        env_btn.setToolTip('Click to see the environmental factor plot')
        env_btn.setStyleSheet('background-color: #006690; color: white;')
        env_btn.clicked.connect(self.env_window)

        distribution_btn = QPushButton('1. Get Distribution', self)
        distribution_btn.setStyleSheet('background-color: #000099; color: white;')
        distribution_btn.clicked.connect(lambda: self.run_distribution(self.input_data, self.variable_list, self.folder_path))

        log_btn = QPushButton('2. Log Transformation', self)
        log_btn.setToolTip('Click to apply <b>Log Transformation</b>')
        log_btn.setStyleSheet('background-color: #6666FF; color: white;')
        log_btn.clicked.connect(lambda: self.apply_log(self.input_data))

        stand_btn = QPushButton('2.1. Standardization', self)
        stand_btn.setToolTip('Click to apply <b>Standardization</b>')
        stand_btn.setStyleSheet('background-color: #6666FF; color: white;')
        stand_btn.clicked.connect(lambda: self.apply_standarization(self.input_data))

        target_btn = QPushButton('3. Choose Target, Input data, and Order Number', self)
        target_btn.setToolTip('Click to open <b>Target Option Window</b>')
        target_btn.setStyleSheet('background-color: #006666; color: white;')
        target_btn.clicked.connect(lambda: self.target_input(self.input_data))

        poly_btn = QPushButton('3.1. Plot Polynomial', self)
        poly_btn.setToolTip('Click to plot <b>Polynomial</b> (Make sure you did Step 3)')
        poly_btn.setStyleSheet('background-color: #006666; color: white;')
        poly_btn.clicked.connect(lambda: self.polynomial_order(self.input_data, self.target, self.order_num, self.folder_path))

        thres_input_btn = QPushButton('4. Insert Threshold Parameter', self)
        thres_input_btn.setToolTip('Click to open <b>Threshold Parameter Window</b>')
        thres_input_btn.setStyleSheet('background-color: #CC6600; color: white;')
        thres_input_btn.clicked.connect(self.thres_input)

        thres_btn = QPushButton('4.1. Plot Threshold', self)
        thres_btn.setToolTip('Click to plot <b>Threshold</b> (Make sure you did Step 4)')
        thres_btn.setStyleSheet('background-color: #CC6600; color: white;')
        thres_btn.clicked.connect(lambda: self.threshold_value(self.input_data, self.target, self.thres_order, self.start, self.end, self.folder_path))

        result_input_btn = QPushButton('5. Insert Lambda', self)
        result_input_btn.setToolTip('Click to open <b>Lambda Window</b>')
        result_input_btn.setStyleSheet('background-color: #990000; color: white;')
        result_input_btn.clicked.connect(self.result_input)

        result_btn = QPushButton('6. Get Result', self)
        result_btn.setToolTip('Make sure to click this button at the end')
        result_btn.setStyleSheet('background-color: #990000; color: white;')
        result_btn.clicked.connect(lambda: self.result(self.input_data, self.target, self.thres_order, self.lamb, self.folder_path))

        self.statusBar().showMessage('')

        self.plot = QLabel('')
        self.plot.setTextInteractionFlags(self.plot.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.plot.setAlignment(Qt.AlignCenter)
        self.plot.setWordWrap(True)

        self.result_output_coeff_label = QLabel('')
        self.result_output_coeff_label.setTextInteractionFlags(self.result_output_coeff_label.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.result_output_coeff_label.setAlignment(Qt.AlignCenter)

        self.result_output_lamb_label = QLabel('')
        self.result_output_lamb_label.setTextInteractionFlags(self.result_output_lamb_label.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.result_output_lamb_label.setAlignment(Qt.AlignCenter)

        self.result_output_term_label = QLabel('')
        self.result_output_term_label.setTextInteractionFlags(self.result_output_term_label.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.result_output_term_label.setAlignment(Qt.AlignCenter)

        self.result_output_expression_label = QLabel('')
        self.result_output_expression_label.setTextInteractionFlags(self.result_output_expression_label.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.result_output_expression_label.setAlignment(Qt.AlignCenter)
        self.result_output_expression_label.setWordWrap(True)


        right_layout.addWidget(btn_folder_dir)
        right_layout.addWidget(self.lbl_selected_dir)
        right_layout.addWidget(btn_select_file)
        right_layout.addWidget(self.lbl_selected_file)
        right_layout.addWidget(btn_select_env)
        right_layout.addWidget(self.lbl_selected_env)
        left_layout.addWidget(self.table_widget)
        right_layout.addWidget(btn_run)
        right_layout.addSpacing(10)
        right_layout.addWidget(distribution_btn)
        right_layout.addSpacing(10)
        right_layout.addWidget(log_btn)
        right_layout.addWidget(stand_btn)
        right_layout.addSpacing(10)
        right_layout.addWidget(target_btn)
        right_layout.addWidget(poly_btn)
        right_layout.addSpacing(10)
        right_layout.addWidget(thres_input_btn)
        right_layout.addWidget(thres_btn)
        right_layout.addSpacing(10)
        right_layout.addWidget(result_input_btn)
        right_layout.addWidget(result_btn)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.plot)
        right_layout.addWidget(self.result_output_coeff_label)
        right_layout.addWidget(self.result_output_lamb_label)
        right_layout.addWidget(self.result_output_term_label)
        right_layout.addWidget(self.result_output_expression_label)
        right_layout.addWidget(self.lbl_selected_env2)
        right_layout.addWidget(env_btn)
        right_layout.addSpacing(10)
        #right_layout.addWidget(btn_exit)


        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        self.setGeometry(300, 300, 1800, 1200)
        self.setWindowTitle('Sindy')

    def show_dir_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        self.folder_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Plots", options=options)

        if self.folder_dir:
            print("Selected Directory:", self.folder_dir)
            self.lbl_selected_dir.setText(f"Saving Directory: {self.folder_dir}")
            self.create_plt_folder()

    def create_plt_folder(self):
        current_datetime = datetime.datetime.now()
        self.date_str = current_datetime.strftime("%Y-%m-%d_%H-%M")
        self.folder_path = os.path.join(self.folder_dir, self.date_str)
        os.makedirs(self.folder_path, exist_ok=True)

    def update_table_widget(self):
        self.table_widget.clear()

        self.table_widget.setColumnCount(len(self.input_data.columns))
        self.table_widget.setHorizontalHeaderLabels(self.input_data.columns)

        for col_index, column in enumerate(self.input_data.columns):
            self.table_widget.setColumnWidth(col_index, 100)

        for row_index, row in self.input_data.iterrows():
            self.table_widget.insertRow(row_index)
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(f'{value:.6f}')
                self.table_widget.setItem(row_index, col_index, item)

    def show_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.csv)", options=options)

        if file_name:
            print("Selected File:", file_name)
            self.lbl_selected_file.setText(f"Selected Data File: {file_name}")

    def show_env_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        self.env_file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.csv)", options=options)

        if self.env_file_name:
            print("Selected File:", self.env_file_name)
            self.lbl_selected_env.setText(f"Selected Env File: {self.env_file_name}")
            self.lbl_selected_env2.setText("Available")
            header, in_dict, out_dict, in_cal, out_cal = calculate_env_data(self.env_file_name)
            self.plot_path = visualization(header, in_dict, out_dict, in_cal, out_cal, self.folder_path)

    def env_window(self):
        print(self.plot_path)
        if os.path.exists(self.plot_path):
            imagewindow = ImageWindow(self.plot_path)
            imagewindow.exec_()

    def run_sindy(self):
        file_name = self.lbl_selected_file.text().replace("Selected Data File: ", "")
        if file_name != "None":
            print(f"Running Sindy with file: {file_name}")

            self.data = get_data(file_name)
            self.input_data = self.data
            self.update_table_widget()
            print(self.input_data)
            self.variable_list = self.input_data.columns.tolist()
            print("Columns:", self.input_data.columns)

            #layout = self.layout()

    def run_distribution(self, data, variable_list, folder_path):
        distribution(data.copy(), variable_list, folder_path)
        self.statusBar().showMessage(f"Distribution plots are saved. ({self.folder_path})")
        #self.plot.setText(f"Distribution plots are saved. ({self.folder_path})")

    def apply_log(self, input_data):
        self.input_data = log_transformation(input_data)
        self.update_table_widget()
        print(self.input_data)

    def apply_standarization(self, input_data):
        self.input_data = standardization(input_data)
        self.update_table_widget()
        print(self.input_data)

    def polynomial_order(self, input_data, target, order_num, folder_path):
        print(self.input_data)
        print(self.target)
        print(self.order_num)
        polynomialorder(input_data, target, order_num, folder_path)
        print("Plotted the polynomial.")
        self.statusBar().showMessage(f"Polynomial order plot is saved. ({self.folder_path})")
        #self.plot.setText(f"Polynomial order plot is saved. ({self.folder_path})")

    def result_input(self):
        lambda_window = LambdaWindow(self)
        communicator.result_lambda_signal.connect(self.handle_lambda)
        lambda_window.exec_()
        communicator.result_lambda_signal.disconnect(self.handle_lambda)

    def handle_lambda(self, lamb_input):
        print(f'Main Window received lambda number for result: {lamb_input}')
        self.lamb = float(lamb_input)

    def result(self, input_data, target, thres_order, lamb, folder_path):
        _, self.result_coeff, self.result_lamb, self.result_term, self.result_expression = result(input_data, target, thres_order, lamb, folder_path)
        print("Received result.")
        self.plot.setText(f"Result plot is saved. ({self.folder_path})")
        self.result_output_coeff_label.setText(f"Correlation Coefficient: {self.result_coeff}")
        self.result_output_lamb_label.setText(f"Threshold Value: {self.result_lamb}")
        self.result_output_term_label.setText(f"Term: {self.result_term}")
        self.result_output_expression_label.setText(f"Expression: {self.result_expression}")

    def thres_input(self):
        thres_window = ThresWindow(self)
        communicator.thres_order_signal.connect(self.handle_thres_order)
        communicator.thres_start_signal.connect(self.handle_thres_start)
        communicator.thres_end_signal.connect(self.handle_thres_end)
        thres_window.exec_()
        communicator.thres_order_signal.disconnect(self.handle_thres_order)
        communicator.thres_start_signal.disconnect(self.handle_thres_start)
        communicator.thres_end_signal.disconnect(self.handle_thres_end)

    def handle_thres_order(self, order_input):
        print(f'Main Window received order number for threshold value: {order_input}')
        self.thres_order = int(order_input)

    def handle_thres_start(self, start_input):
        print(f'Main Window received start number for threshold value: {start_input}')
        self.start = int(start_input)

    def handle_thres_end(self, end_input):
        print(f'Main Window received end number for threshold value: {end_input}')
        self.end = int(end_input)

    def threshold_value(self, input_data, target, order_num, start, end, folder_path):
        print(f'Order number: {order_num}, Start: {start}, End: {end}')
        thresholdvalue(input_data, target, order_num, start, end, folder_path)
        print("Plotted threshold plot.")
        self.statusBar().showMessage(f"Threshold value plot is saved. ({self.folder_path})")
        #self.plot.setText(f"Threshold value plot is saved. ({self.folder_path})")

    def target_input(self, data):
        target_window = TargetWindow(data, self)
        communicator.selected_columns_signal.connect(self.handle_target_columns)
        communicator.selected_drop_signal.connect(self.handle_drop)
        communicator.selected_ordernum_signal.connect(self.handle_ordernum)
        target_window.exec_()
        communicator.selected_columns_signal.disconnect(self.handle_target_columns)
        communicator.selected_drop_signal.disconnect(self.handle_drop)
        communicator.selected_ordernum_signal.disconnect(self.handle_ordernum)
        self.update_table_widget()

    def handle_target_columns(self, target_column):
        print(f'Main Window received target column: {target_column}')
        self.target = self.input_data[[target_column]]
        print(self.target)
        self.input_data = self.input_data.drop([target_column], axis=1)
        self.update_table_widget()
        print(self.input_data)

    def handle_drop(self, drop_column):
        print(f'Main Window received selected column to drop: {drop_column}')
        self.input_data = self.input_data.drop([drop_column], axis=1)
        self.update_table_widget()
        print(self.input_data)

    def handle_ordernum(self, order_num):
        print(f'Main Window received selected order number: {int(order_num)}')
        self.order_num = int(order_num)


    def exit_program(self):
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

