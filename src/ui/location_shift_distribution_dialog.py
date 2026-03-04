from PySide6.QtCharts import (
    QBarCategoryAxis,
    QChart,
    QChartView,
    QStackedBarSeries,
    QBarSet,
    QValueAxis,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


APP_TITLE = "Schichtverteilung nach Standort"
DEFAULT_WEEKS = 13


class LocationShiftDistributionDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._chart = QChart()
        self._chart_view = QChartView(self._chart)
        self._setup_ui()
        self._refresh_chart()

    def _setup_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(980, 620)

        layout = QVBoxLayout()

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        self._weeks_input = QSpinBox()
        self._weeks_input.setMinimum(1)
        self._weeks_input.setMaximum(260)
        self._weeks_input.setValue(DEFAULT_WEEKS)
        self._weeks_input.valueChanged.connect(self._refresh_chart)
        form.addRow("Betrachtungszeitraum (Wochen):", self._weeks_input)
        layout.addLayout(form)

        self._chart_view.setRenderHint(QPainter.Antialiasing, True)
        self._chart_view.setMinimumHeight(430)
        layout.addWidget(self._chart_view)

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_button = QPushButton("Dialog schließen")
        close_button.clicked.connect(self.close)
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def _refresh_chart(self):
        weeks = int(self._weeks_input.value())
        data = self._application.get_location_shift_distribution_last_weeks(weeks)
        week_entries = data.get("weeks", [])
        location_entries = data.get("locations", [])

        self._chart.removeAllSeries()
        axis_x_existing = self._chart.axisX()
        if axis_x_existing is not None:
            self._chart.removeAxis(axis_x_existing)
        axis_y_existing = self._chart.axisY()
        if axis_y_existing is not None:
            self._chart.removeAxis(axis_y_existing)
        self._chart.setTitle("Verteilung der Schichten pro Standort")
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignBottom)

        categories = [str(entry.get("week_label", "")) for entry in week_entries]
        totals = []
        for entry in week_entries:
            counts = entry.get("counts", {})
            if isinstance(counts, dict):
                totals.append(sum(int(v) for v in counts.values()))
            else:
                totals.append(0)

        series = QStackedBarSeries()
        palette = [
            QColor("#3366cc"),
            QColor("#dc3912"),
            QColor("#ff9900"),
            QColor("#109618"),
            QColor("#990099"),
            QColor("#0099c6"),
            QColor("#dd4477"),
            QColor("#66aa00"),
        ]

        for idx, location in enumerate(location_entries):
            location_id = str(location.get("location_id", ""))
            location_name = str(location.get("location_name", location_id))
            bar_set = QBarSet(f"{location_id} - {location_name}")
            bar_set.setColor(palette[idx % len(palette)])
            for entry in week_entries:
                counts = entry.get("counts", {})
                value = 0
                if isinstance(counts, dict):
                    value = int(counts.get(location_id, 0))
                bar_set.append(value)
            series.append(bar_set)

        if len(series.barSets()) == 0:
            empty_set = QBarSet("Keine Daten")
            for _ in categories:
                empty_set.append(0)
            series.append(empty_set)

        self._chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self._chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setMinorTickCount(0)
        max_value = max(totals) if totals else 0
        axis_y.setRange(0, max(1, int(max_value)))
        self._chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
