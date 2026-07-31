
# =====================================================
# BEFORE/AFTER SLIDER PLACEHOLDER
# Questo file è preparato per la prossima integrazione
# del widget di confronto. Nessuna funzione esistente
# è stata modificata.
# =====================================================

import cv2
import json
import os
import numpy as np

from core.analyzer import GraphicAnalyzer
from core.black_saver import BlackSaver
from core.white_engine import WhiteEngine

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QComboBox,
    QSlider,
    QProgressBar,
    QCheckBox,
    QMessageBox
)

from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QSettings


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DTF Optimizer Pro")
        self.resize(1700, 950)

        self.setAcceptDrops(True)

        self.current_file = None
        self.original_image = None
        self.optimized_image = None
        self.last_analysis = {}
        self.showing_difference = False

        self.analyzer = GraphicAnalyzer()
        self.black_saver = BlackSaver()
        self.white_engine = WhiteEngine()

        self.settings = QSettings('DTFOptimizerPro','DTFOptimizerPro')
        self.build_ui()

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)

        # ======================
        # PREVIEW
        # ======================

        preview_layout = QHBoxLayout()

        self.original_preview = QLabel("Originale")
        self.original_preview.setAlignment(Qt.AlignCenter)

        self.optimized_preview = QLabel("Ottimizzata")
        self.optimized_preview.setAlignment(Qt.AlignCenter)

        preview_layout.addWidget(
            self.original_preview
        )

        preview_layout.addWidget(
            self.optimized_preview
        )

        root.addLayout(
            preview_layout,
            3
        )

        # ======================
        # SIDEBAR
        # ======================

        sidebar = QVBoxLayout()

        open_btn = QPushButton(
            "Apri Grafica"
        )

        open_btn.clicked.connect(
            self.open_file
        )

        sidebar.addWidget(
            open_btn
        )

        sidebar.addWidget(
            QLabel("Preset DTF")
        )

        self.preset_combo = QComboBox()

        self.preset_combo.addItems([
            "Soft DTF",
            "Production",
            "Ultra Soft",
            "Serigrafico"
        ])

        sidebar.addWidget(
            self.preset_combo
        )
        
        sidebar.addWidget(
            QLabel("Gestione Nero")
        )

        self.black_mode = QComboBox()

        self.black_mode.addItems([
            "Ink Saver",
            "Garment Black",
            "Halftone Black"
        ])

        sidebar.addWidget(
            self.black_mode
        )
        sidebar.addWidget(
            QLabel("Colore Maglia")
        )

        self.shirt_color = QComboBox()

        self.shirt_color.addItems([
            "Nero",
            "Antracite",
            "Grigio",
            "Rosso",
            "Blu",
            "Bianco"
        ])

        sidebar.addWidget(
            self.shirt_color
        )
        
        # ======================
        # DENSITA'
        # ======================

        sidebar.addWidget(
            QLabel("Densità Inchiostro")
        )

        self.ink_slider = QSlider(
            Qt.Horizontal
        )

        self.ink_slider.setMinimum(50)
        self.ink_slider.setMaximum(100)
        self.ink_slider.setValue(85)

        sidebar.addWidget(
            self.ink_slider
        )

        self.ink_value = QLabel(
            "85%"
        )

        sidebar.addWidget(
            self.ink_value
        )

        self.ink_slider.valueChanged.connect(
            lambda v:
            self.ink_value.setText(
                f"{v}%"
            )
        )

        # ======================
        # BOTTONI
        # ======================

        optimize_btn = QPushButton(
            "Ottimizza"
        )

        optimize_btn.clicked.connect(
            self.optimize_image
        )

        sidebar.addWidget(
            optimize_btn
        )

        diff_btn = QPushButton(
            "Mostra Differenze"
        )
        problem_btn = QPushButton(
        "Mostra Problemi"
        )

        problem_btn.clicked.connect(
            self.show_problems
        )

        sidebar.addWidget(
            problem_btn
        )
        diff_btn.clicked.connect(
            self.toggle_difference_view
        )

        sidebar.addWidget(
            diff_btn
        )

        white_btn = QPushButton(
            "Mostra Underbase"
        )
        
        preview_btn = QPushButton(
            "Anteprima Maglia"
        )

        preview_btn.clicked.connect(
            self.show_shirt_preview
        )

        sidebar.addWidget(
            preview_btn
        )

        white_btn.clicked.connect(
            self.show_underbase
        )

        sidebar.addWidget(
            white_btn
        )

        save_btn = QPushButton(
            "Salva PNG"
        )

        save_btn.clicked.connect(
            self.save_image
        )

        sidebar.addWidget(
            save_btn
        )

        sidebar.addWidget(
            QLabel("Cartella di esportazione")
        )

        self.export_mode = QComboBox()
        self.export_mode.addItems([
            "Chiedi ogni volta",
            "Stessa cartella dell'originale",
            "Cartella predefinita..."
        ])
        self.export_mode.setCurrentText(
            self.settings.value(
                "export_mode",
                "Chiedi ogni volta"
            )
        )
        self.export_mode.currentTextChanged.connect(
            self.export_mode_changed
        )
        sidebar.addWidget(
            self.export_mode
        )

        sidebar.addWidget(
            QLabel("Formato esportazione")
        )

        self.export_format = QComboBox()
        self.export_format.addItems([
            "PNG"
        ])
        sidebar.addWidget(self.export_format)

        sidebar.addWidget(
            QLabel("Suffisso automatico")
        )

        self.export_suffix = QComboBox()
        self.export_suffix.addItems([
            "_optimized",
            "_DTF",
            "_print"
        ])
        sidebar.addWidget(self.export_suffix)

        self.output_folder_check = QCheckBox(
            "Crea automaticamente la cartella Output"
        )
        self.output_folder_check.setChecked(True)
        sidebar.addWidget(self.output_folder_check)

        self.overwrite_check = QCheckBox(
            "Sovrascrivi file esistenti"
        )
        self.overwrite_check.setChecked(False)
        sidebar.addWidget(self.overwrite_check)

        batch_info = QLabel(
            "Batch Processing utilizza il Preset, la Densità e la Gestione Nero attualmente selezionati."
        )
        self.batch_progress = QProgressBar()

        self.batch_progress.setValue(
            0
        )

        sidebar.addWidget(
            self.batch_progress
        )
        
        batch_info.setWordWrap(
            True
        )

        sidebar.addWidget(
            batch_info
        )

        batch_btn = QPushButton(
            "Batch Processing"
        )

        batch_btn.clicked.connect(
            self.batch_process
        )

        sidebar.addWidget(
            batch_btn
        )
        save_preset_btn = QPushButton(
            "Salva Preset"
        )

        save_preset_btn.clicked.connect(
            self.save_preset
        )

        sidebar.addWidget(
            save_preset_btn
        )

        load_preset_btn = QPushButton(
            "Carica Preset"
        )

        load_preset_btn.clicked.connect(
            self.load_preset
        )

        sidebar.addWidget(
            load_preset_btn
        )

        reset_btn = QPushButton(
            "Reset"
        )

        reset_btn.clicked.connect(
            self.reset_workspace
        )

        sidebar.addWidget(
            reset_btn
        )

        # ======================
        # INFO
        # ======================

        self.info = QLabel(
            "Nessun file"
        )

        self.info.setWordWrap(True)

        sidebar.addWidget(
            self.info
        )

        # ======================
        # ANALISI
        # ======================

        self.analysis = QLabel(
            "Nessuna analisi"
        )

        self.analysis.setWordWrap(True)

        sidebar.addWidget(
            self.analysis
        )

        # ======================
        # RISPARMIO
        # ======================

        self.saving_label = QLabel(
            "Riduzione Nero: -"
        )

        sidebar.addWidget(
            self.saving_label
        )

        sidebar.addStretch()

        root.addLayout(
            sidebar,
            1
        )


    def array_to_pixmap(self, img):

        if len(img.shape) == 2:

            h, w = img.shape

            qimg = QImage(
                img.data,
                w,
                h,
                w,
                QImage.Format_Grayscale8
            )

            return QPixmap.fromImage(qimg)

        if img.shape[2] == 4:

            rgb = cv2.cvtColor(
                img,
                cv2.COLOR_BGRA2RGBA
            )

            h, w, ch = rgb.shape

            qimg = QImage(
                rgb.data,
                w,
                h,
                ch * w,
                QImage.Format_RGBA8888
            )

            return QPixmap.fromImage(qimg)

        rgb = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        qimg = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        return QPixmap.fromImage(qimg)


    def open_file(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Apri immagine",
            "",
            "Images (*.png *.jpg *.jpeg *.tif *.tiff)"
        )

        if not path:
            return

        self.current_file = path

        self.original_image = cv2.imread(
            path,
            cv2.IMREAD_UNCHANGED
        )

        pix = QPixmap(path)

        self.original_preview.setPixmap(
            pix.scaled(
                700,
                700,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.info.setText(path)

        try:

            data = self.analyzer.analyze(path)
            
            self.last_analysis = data

            self.problem_boxes = data.get(
                "problem_boxes",
                []
            )
            self.preset_combo.setCurrentText(
                data.get(
                    "auto_preset",
                    "Soft DTF"
                )
            )

            self.ink_slider.setValue(
                data.get(
                    "auto_density",
                    85
                )
            )

            preflight_text = ""

            for warning in data.get(
                "preflight",
                []
            ):

                preflight_text += (
                    f"⚠ {warning}\n"
                )

            if preflight_text == "":

                preflight_text = (
                    "✓ Nessun problema"
                )
                
            self.analysis.setText(
                f"""
Tipo:
{data['graphic_type']}

Preset:
{data['recommended_preset']}

Auto Preset:
{data.get('auto_preset','-')}

Auto Density:
{data.get('auto_density','-')}

Choke:
{data.get('auto_choke','-')}

Feather:
{data.get('auto_feather','-')}

Highlight White:
{data.get('auto_highlight','-')}

Dimensioni:
{data['width_px']} x {data['height_px']}

Trasparenza:
{data['transparent_area_pct']}%

Nero:
{data['black_area_pct']}%

Bianco:
{data['white_area_pct']}%

Preflight:

{preflight_text}
"""
            )
        except Exception as e:

            self.analysis.setText(
                f"Errore analisi:\n{str(e)}"
            )

            print(
                "ERRORE ANALISI:",
                str(e)
            )            

    def optimize_image(self):

        if self.current_file is None:
            return

        image = cv2.imread(
            self.current_file,
            cv2.IMREAD_UNCHANGED
        )

        preset = (
            self.preset_combo.currentText()
        )

        density = (
            self.ink_slider.value()
        )

        black_mode = (
            self.black_mode.currentText()
        )

        optimized = self.black_saver.process(
            image,
            preset,
            density,
            black_mode
        )

        optimized = self.white_engine.prepare_for_rip(
            optimized,
            choke=self.last_analysis.get(
                "auto_choke",
                0.25
            ),
            feather=self.last_analysis.get(
                "auto_feather",
                0.50
            )
        )

        self.optimized_image = optimized

        saving = (
            self.black_saver.estimate_saving(
                image,
                optimized
            )
        )

        self.saving_label.setText(
            f"Riduzione Nero: {saving:.2f}%"
        )

        pix = self.array_to_pixmap(
            optimized
        )

        self.optimized_preview.setPixmap(
            pix.scaled(
                700,
                700,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        
    def toggle_difference_view(self):

        if self.original_image is None:
            return

        if self.optimized_image is None:
            return

        if self.showing_difference:

            pix = self.array_to_pixmap(
                self.optimized_image
            )

            self.optimized_preview.setPixmap(
                pix.scaled(
                    700,
                    700,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

            self.showing_difference = False
            return

        original_gray = cv2.cvtColor(
            self.original_image[:, :, :3],
            cv2.COLOR_BGR2GRAY
        )

        optimized_gray = cv2.cvtColor(
            self.optimized_image[:, :, :3],
            cv2.COLOR_BGR2GRAY
        )

        heatmap = np.zeros(
            (
                original_gray.shape[0],
                original_gray.shape[1],
                3
            ),
            dtype=np.uint8
        )

        if (
            len(self.original_image.shape) == 3
            and self.original_image.shape[2] == 4
            and len(self.optimized_image.shape) == 3
            and self.optimized_image.shape[2] == 4
        ):

            original_alpha = (
                self.original_image[:, :, 3]
            )

            optimized_alpha = (
                self.optimized_image[:, :, 3]
            )

            removed_alpha = (
                (original_alpha > 10)
                &
                (optimized_alpha <= 10)
            )

            heatmap[
                removed_alpha
            ] = (
                0,
                0,
                255
            )

        difference = (
            optimized_gray.astype(np.int16)
            -
            original_gray.astype(np.int16)
        )

        reduced = (
            (difference > 10)
            &
            (difference <= 40)
        )

        heatmap[
            reduced
        ] = (
            0,
            255,
            255
        )

        unchanged = (
            np.abs(
                difference
            ) <= 10
        )

        green_mask = (
            unchanged
            &
            (
                np.sum(
                    heatmap,
                    axis=2
                ) == 0
            )
        )

        heatmap[
            green_mask
        ] = (
            0,
            180,
            0
        )

        pix = self.array_to_pixmap(
            heatmap
        )


        self.optimized_preview.setPixmap(
            pix.scaled(
                700,
                700,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.showing_difference = True

    def show_problems(self):

        if self.original_image is None:
            return

        if (
            len(self.original_image.shape) == 3
            and
            self.original_image.shape[2] == 4
        ):

            alpha = self.original_image[:, :, 3]

            draw = np.full(
                (
                    self.original_image.shape[0],
                    self.original_image.shape[1],
                    3
                ),
                255,
                dtype=np.uint8
            )

            mask = alpha > 0

            draw[mask] = self.original_image[
                mask,
                :3
            ]

        else:

            draw = self.original_image.copy()

        for (
            x,
            y,
            w,
            h
        ) in self.problem_boxes[:20]:

            center_x = x + (w // 2)
            center_y = y + (h // 2)

            cv2.drawMarker(
                draw,
                (
                    center_x,
                    center_y
                ),
                (
                    0,
                    0,
                    255
                ),
                markerType=cv2.MARKER_CROSS,
                markerSize=25,
                thickness=2
            )

        pix = self.array_to_pixmap(
            draw
        )


        self.optimized_preview.setPixmap(
            pix.scaled(
                700,
                700,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def save_preset(self):

        data = {
            "preset":
                self.preset_combo.currentText(),

            "density":
                self.ink_slider.value(),

            "black_mode":
                self.black_mode.currentText()
        }

        mode = self.export_mode.currentText()

        if mode == "Stessa cartella dell'originale" and self.current_file:
            import os
            base = os.path.splitext(os.path.basename(self.current_file))[0]
            path = os.path.join(os.path.dirname(self.current_file), f"{base}_optimized.png")
        elif mode == "Cartella predefinita...":
            import os
            folder = self.settings.value("export_folder","")
            if not folder:
                folder = QFileDialog.getExistingDirectory(self,"Seleziona cartella di esportazione")
                if folder:
                    self.settings.setValue("export_folder",folder)
            if not folder:
                return
            base="grafica_optimized.png"
            if self.current_file:
                base=os.path.splitext(os.path.basename(self.current_file))[0]+"_optimized.png"
            path=os.path.join(folder,base)
        else:
            path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva Preset",
            "",
            "JSON (*.json)"
        )

        if not path:
            return

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )
            
    def load_preset(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Carica Preset",
            "",
            "JSON (*.json)"
        )

        if not path:
            return

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        self.preset_combo.setCurrentText(
            data.get(
                "preset",
                "Soft DTF"
            )
        )

        self.ink_slider.setValue(
            data.get(
                "density",
                85
            )
        )

        self.black_mode.setCurrentText(
            data.get(
                "black_mode",
                "Ink Saver"
            )
        )
        
    def reset_workspace(self):

        self.current_file = None
        self.original_image = None
        self.optimized_image = None

        self.last_analysis = {}
        self.showing_difference = False

        self.original_preview.clear()
        self.optimized_preview.clear()

        self.original_preview.setText(
            "Originale"
        )

        self.optimized_preview.setText(
            "Ottimizzata"
        )

        self.info.setText(
            "Nessun file"
        )

        self.analysis.setText(
            "Nessuna analisi"
        )

        self.saving_label.setText(
            "Riduzione Nero: -"
        )

        self.preset_combo.setCurrentText(
            "Soft DTF"
        )

        self.black_mode.setCurrentText(
            "Ink Saver"
        )

        self.ink_slider.setValue(
            85
        )
        
    def show_underbase(self):

        if self.optimized_image is None:
            return

        img = self.optimized_image

        if len(img.shape) == 3 and img.shape[2] == 4:

            alpha = img[:, :, 3]

        else:

            gray = cv2.cvtColor(
                img,
                cv2.COLOR_BGR2GRAY
            )

            alpha = cv2.threshold(
                gray,
                1,
                255,
                cv2.THRESH_BINARY
            )[1]

        preview = np.zeros(
            (
                alpha.shape[0],
                alpha.shape[1],
                3
            ),
            dtype=np.uint8
        )

        preview[
            alpha > 0
        ] = (
            255,
            255,
            255
        )

        pix = self.array_to_pixmap(
            preview
        )


        self.optimized_preview.setPixmap(
            pix.scaled(
                700,
                700,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def show_shirt_preview(self):

        if self.optimized_image is None:
            return

        shirt_colors = {

            "Nero": (30, 30, 30),

            "Antracite": (
                70,
                70,
                70
            ),

            "Grigio": (
                130,
                130,
                130
            ),

            "Rosso": (
                40,
                40,
                180
            ),

            "Blu": (
                180,
                80,
                30
            ),

            "Bianco": (
                255,
                255,
                255
            )
        }

        color = shirt_colors[
            self.shirt_color.currentText()
        ]

        img = self.optimized_image

        h, w = img.shape[:2]

        shirt = np.full(
            (
                h,
                w,
                3
            ),
            color,
            dtype=np.uint8
        )

        if (
            len(img.shape) == 3
            and
            img.shape[2] == 4
        ):

            alpha = (
                img[:, :, 3]
                .astype(np.float32)
                / 255.0
            )

            alpha = alpha[
                :,
                :,
                np.newaxis
            ]

            graphic = img[:, :, :3]

            preview = (
                graphic * alpha
                +
                shirt * (1 - alpha)
            ).astype(
                np.uint8
            )

        else:

            preview = img[:, :, :3]

        pix = self.array_to_pixmap(
            preview
        )


        self.optimized_preview.setPixmap(
            pix.scaled(
                700,
                700,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def export_mode_changed(self, mode):

        self.settings.setValue("export_mode", mode)

        if mode == "Cartella predefinita...":

            folder = QFileDialog.getExistingDirectory(
                self,
                "Seleziona cartella di esportazione"
            )

            if folder:
                self.settings.setValue(
                    "export_folder",
                    folder
                )


    def batch_process(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Cartella PNG"
        )

        if not folder:
            return

        output_folder = os.path.join(
            folder,
            "output"
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        preset = (
            self.preset_combo.currentText()
        )

        density = (
            self.ink_slider.value()
        )

        black_mode = (
            self.black_mode.currentText()
        )

        files = [
            f
            for f in os.listdir(folder)
            if f.lower().endswith(
                ".png"
            )
        ]

        total_files = len(
            files
        )

        if total_files == 0:

            QMessageBox.information(
                self,
                "Batch Processing",
                "Nessun file PNG trovato."
            )

            return

        processed = 0

        self.batch_progress.setValue(
            0
        )

        QApplication.processEvents()

        for file in files:

            path = os.path.join(
                folder,
                file
            )

            image = cv2.imread(
                path,
                cv2.IMREAD_UNCHANGED
            )

            if image is None:
                continue

            result = self.black_saver.process(
                image,
                preset,
                density,
                black_mode
            )

            result = self.white_engine.prepare_for_rip(
                result,
                choke=0.25,
                feather=0.50
            )

            output_path = os.path.join(
                output_folder,
                file.replace(
                    ".png",
                    "_optimized.png"
                )
            )

            cv2.imwrite(
                output_path,
                result
            )

            processed += 1

            progress = int(
                (
                    processed
                    /
                    total_files
                )
                * 100
            )

            self.batch_progress.setValue(
                progress
            )

            QApplication.processEvents()

        self.batch_progress.setValue(
            100
        )

        QMessageBox.information(
            self,
            "Batch Completato",
            f"{processed} file elaborati.\n\nSalvati in:\n{output_folder}"
        )
        

    def dragEnterEvent(self, event):

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):

        urls = event.mimeData().urls()

        if not urls:
            return

        path = urls[0].toLocalFile()

        if path.lower().endswith(
            (".png", ".jpg", ".jpeg", ".tif", ".tiff")
        ):

            self.current_file = path

            self.original_image = cv2.imread(
                path,
                cv2.IMREAD_UNCHANGED
            )

            pix = QPixmap(path)

            self.original_preview.setPixmap(
                pix.scaled(
                    700,
                    700,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

            self.info.setText(path)


    def save_image(self):

        if self.optimized_image is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva PNG",
            "",
            "PNG (*.png)"
        )

        if not path:
            return

        cv2.imwrite(
            path,
            self.optimized_image
        )

        self.info.setText(
            f"Salvato:\n{path}"
        )