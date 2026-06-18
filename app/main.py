import sys

def main():
    try:
        from PySide6.QtWidgets import QApplication
        from app.ui.main_window import MainWindow
    except ImportError as e:
        print('PySide6가 설치되어 있지 않습니다. `pip install -r requirements.txt` 후 다시 실행하세요.')
        raise SystemExit(1) from e
    app=QApplication(sys.argv); w=MainWindow(); w.show(); sys.exit(app.exec())
if __name__ == '__main__': main()
