from PySide6.QtCharts import (
    QChart,
    QChartView,
    QCategoryAxis,
    QLineSeries,
    QValueAxis,
)
from datetime import datetime
from math import ceil
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


APP_TITLE = "Budget Burndown"


class BudgetBurndownDialog(QDialog):
    def __init__(self, p_application, p_parent=None):
        super().__init__(p_parent)
        self._application = p_application
        self._chart = QChart()
        self._chart_view = QChartView(self._chart)
        self._setup_ui()
        self._refresh_chart()

    def _setup_ui(self) -> None:
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 680)

        layout = QVBoxLayout()

        controls = QHBoxLayout()
        self._forecast_weeks_input = QSpinBox()
        self._forecast_weeks_input.setRange(1, 104)
        self._forecast_weeks_input.setValue(self._application.get_burndown_forecast_weeks())
        self._forecast_weeks_input.valueChanged.connect(self._on_forecast_changed)
        refresh = QPushButton("Burndown aktualisieren")
        refresh.clicked.connect(self._refresh_chart)

        controls.addWidget(QLabel("Anzahl der letzten Wochen, die für Prognose berücksichtigt werden sollen:"))
        controls.addWidget(self._forecast_weeks_input)
        controls.addWidget(refresh)
        controls.addStretch()
        layout.addLayout(controls)

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

    def _refresh_chart(self) -> None:
        self._forecast_weeks_input.interpretText()
        self._chart.removeAllSeries()
        for axis in list(self._chart.axes()):
            self._chart.removeAxis(axis)

        try:
            data = self._application.get_budget_burndown_data(
                p_forecast_weeks=int(self._forecast_weeks_input.value()),
            )
        except Exception as exc:
            self._chart.setTitle(str(exc))
            QMessageBox.warning(self, APP_TITLE, str(exc))
            return

        labels = list(data.get("labels", []))
        if not labels:
            self._chart.setTitle("Keine Daten für Burndown vorhanden.")
            return

        plan = list(data.get("plan", []))
        actual_raw = data.get("actual", [])
        forecast_raw = data.get("forecast", [])
        total_budget = float(data.get("total_budget", 0.0) or 0.0)
        if total_budget < 0:
            total_budget = 0.0

        def _as_points(
            p_rows: object,
        ) -> list[tuple[int, float]]:
            points: list[tuple[int, float]] = []
            if not isinstance(p_rows, list):
                return points
            for idx, row in enumerate(p_rows):
                if not isinstance(row, dict):
                    continue
                week_index = row.get("week_index", idx)
                value = float(row.get("value", 0.0))
                points.append((int(week_index), value))
            return points

        def _to_burndown(p_values: list[float]) -> list[float]:
            return [max(0.0, total_budget - float(value)) for value in p_values]

        plan = [
            (float(index), value)
            for index, value in enumerate(_to_burndown([float(value) for value in plan]))
        ]
        actual = [
            (float(index), _to_burndown([value])[0])
            for index, value in _as_points(actual_raw)
        ]
        forecast = [
            (float(index), _to_burndown([value])[0])
            for index, value in _as_points(forecast_raw)
        ]

        self._chart.setTitle("Budget Burndown")
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignBottom)

        series_plan = QLineSeries()
        series_plan.setName("Plan")
        pen_plan = QPen(QColor("#2E8B57"), 3)
        pen_plan.setStyle(Qt.PenStyle.DashLine)
        series_plan.setPen(pen_plan)
        for index, value in plan:
            series_plan.append(float(index), float(value))
        self._chart.addSeries(series_plan)

        if actual:
            series_actual = QLineSeries()
            series_actual.setName("Ist")
            series_actual.setPen(QPen(QColor("#000000"), 3))
            for index, value in actual:
                series_actual.append(float(index), float(value))
            self._chart.addSeries(series_actual)

        if forecast:
            series_forecast = QLineSeries()
            series_forecast.setName("Forecast")
            pen_forecast = QPen(QColor("#4169E1"), 3)
            pen_forecast.setStyle(Qt.PenStyle.DotLine)
            series_forecast.setPen(pen_forecast)
            for index, value in forecast:
                series_forecast.append(float(index), float(value))
            self._chart.addSeries(series_forecast)

        axis_x = QCategoryAxis()
        for idx, label in enumerate(labels):
            axis_label = str(label)
            if isinstance(label, str):
                try:
                    axis_label = datetime.fromisoformat(label).strftime("%d.%m.%y")
                except Exception:
                    axis_label = str(label)
            axis_x.append(axis_label, float(idx))
        axis_x.setRange(0.0, float(len(labels)))
        axis_x.setTitleText("Zeit")
        axis_x.setLabelsAngle(0)
        self._chart.addAxis(axis_x, Qt.AlignBottom)

        values_for_scale = [float(value) for _index, value in plan]
        if actual:
            values_for_scale.extend(float(value) for _index, value in actual)
        if forecast:
            values_for_scale.extend(float(value) for _index, value in forecast)

        if not values_for_scale:
            values_for_scale = [0.0]

        min_value = min(values_for_scale)
        max_value = max(values_for_scale)
        if min_value == max_value:
            min_value -= 1
            max_value += 1

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        axis_y.setTitleText("Restbudget")
        step = 5000.0
        max_budget = max(0.0, total_budget)
        if max_budget == 0:
            max_budget = step
        rounded_budget = max(step, ceil(max_budget / step) * step)
        axis_y.setRange(0.0, rounded_budget)
        axis_y.setTickInterval(step)
        axis_y.setTickCount(int(rounded_budget / step) + 1)
        axis_y.setMinorTickCount(0)
        self._chart.addAxis(axis_y, Qt.AlignLeft)

        for series in self._chart.series():
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

        self._persist_forecast_setting()

    def _on_forecast_changed(self) -> None:
        self._persist_forecast_setting()
        self._refresh_chart()

    def _persist_forecast_setting(self) -> None:
        try:
            self._application.set_burndown_forecast_weeks(int(self._forecast_weeks_input.value()))
        except Exception:
            pass
