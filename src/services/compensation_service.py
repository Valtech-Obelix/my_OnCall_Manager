import csv
import re
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, timedelta

from src.domain.exceptions import DomainException
from src.infrastructure.runtime_paths import booking_csv_files
from src.infrastructure.timezone_utils import BERLIN, parse_utc_timestamp


SHIFT_BOUNDARY_HOUR = 1
GER_OT_25_TASK = "Arbeit (25%) WT (6-9, 17-20) Sa (6-20)"
GER_OT_50_TASK = "Arbeit (50%) WT (20-6), Sa (20-6), So & FT"
IND_OT_MOSAT_TASK = "Work On Call Shift (Mo-Sat)"
IND_OT_SUN_TASK = "Work On Call Shift (Sunday)"


class CompensationService:
    def parse_booking_hours(self, p_hours: str) -> Decimal | None:
        text = p_hours.strip()
        if not text:
            return None

        normalized = text.replace(" ", "")
        if "," in normalized and "." in normalized:
            if normalized.rfind(",") > normalized.rfind("."):
                normalized = normalized.replace(".", "").replace(",", ".")
            else:
                normalized = normalized.replace(",", "")
        elif "," in normalized:
            normalized = normalized.replace(",", ".")

        try:
            amount = Decimal(normalized)
        except InvalidOperation:
            return None
        return amount

    def parse_booking_units(self, p_hours: str) -> int | None:
        amount = self.parse_booking_hours(p_hours)
        if amount is None:
            return None

        if amount != amount.to_integral_value():
            return None
        return int(amount)

    def _normalize_task_name(self, p_name: str) -> str:
        return " ".join(p_name.casefold().split())

    def _is_overtime_task(self, p_task_name: str) -> bool:
        normalized = self._normalize_task_name(p_task_name)
        return normalized in {
            self._normalize_task_name(GER_OT_25_TASK),
            self._normalize_task_name(GER_OT_50_TASK),
            self._normalize_task_name(IND_OT_MOSAT_TASK),
            self._normalize_task_name(IND_OT_SUN_TASK),
        }

    def _overtime_bucket_for_task(self, p_task_name: str) -> str | None:
        normalized = self._normalize_task_name(p_task_name)
        mapping = {
            self._normalize_task_name(GER_OT_25_TASK): "GER_25",
            self._normalize_task_name(GER_OT_50_TASK): "GER_50",
            self._normalize_task_name(IND_OT_MOSAT_TASK): "IND_MO_SA",
            self._normalize_task_name(IND_OT_SUN_TASK): "IND_SO",
        }
        return mapping.get(normalized)

    def _format_hours(self, p_hours: Decimal) -> str:
        normalized = p_hours.normalize()
        text = format(normalized, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    def determine_shift_slot(self, p_start_time_utc: str) -> str:
        start_local = parse_utc_timestamp(p_start_time_utc).astimezone(BERLIN)
        shifted_hour = (start_local.hour - SHIFT_BOUNDARY_HOUR) % 24
        if shifted_hour < 8:
            return "F"
        if shifted_hour < 16:
            return "T"
        return "S"

    def determine_day_type(self, p_day: date) -> str:
        if p_day.weekday() == 5:
            return "SATURDAY"
        if p_day.weekday() == 6 or self._is_bavaria_holiday(p_day):
            return "SUNDAY_OR_HOLIDAY"
        return "WEEKDAY"

    def determine_expected_booking_task(
        self,
        p_oncall_location_id: str,
        p_day: date,
        p_slot: str,
    ) -> str | None:
        day_type = self.determine_day_type(p_day)
        location_id = p_oncall_location_id.strip().upper()
        slot = p_slot.strip().upper()

        if slot not in ("F", "T", "S"):
            raise DomainException(f"Unbekannter Schichtslot: {slot}")

        if location_id == "GER":
            if day_type == "WEEKDAY":
                if slot in ("F", "S"):
                    return "Rufbereitschaft Werktags"
                return None
            if day_type == "SATURDAY":
                return "Rufbereitschaft Samstags und Betriebsurlaub"
            return "Rufbereitschaft Sonn- und Feiertags"

        if location_id == "IND":
            if day_type == "WEEKDAY":
                return "On Call Shift Working days"
            return "On Call Shift Weekend and Holidays"

        raise DomainException(f"Unbekannter Rufbereitschaftsstandort: {location_id}")

    def _calculate_amount_for_day_slot(
        self,
        p_oncall_location_id: str,
        p_day: date,
        p_slot: str,
    ) -> int:
        day_type = self.determine_day_type(p_day)
        location_id = p_oncall_location_id.strip().upper()

        if location_id == "GER":
            if day_type == "WEEKDAY":
                if p_slot in ("F", "S"):
                    return 125
                return 0
            if day_type == "SATURDAY":
                return 150
            return 180

        if location_id == "IND":
            if day_type == "WEEKDAY":
                return 6
            return 10

        raise DomainException(f"Unbekannter Rufbereitschaftsstandort: {location_id}")

    def calculate_shift_compensation(
        self,
        p_oncall_location_id: str,
        p_start_time_utc: str,
    ) -> int:
        start_local = parse_utc_timestamp(p_start_time_utc).astimezone(BERLIN)
        slot = self.determine_shift_slot(p_start_time_utc)
        return self._calculate_amount_for_day_slot(
            p_oncall_location_id=p_oncall_location_id,
            p_day=start_local.date(),
            p_slot=slot,
        )

    def _normalize_person_name(self, p_name: str) -> str:
        cleaned = re.sub(r"[^\w\s]", " ", p_name.casefold())
        tokens = [token for token in cleaned.split() if token]
        return " ".join(sorted(tokens))

    def _parse_slot_from_notes(self, p_notes: str) -> str | None:
        normalized = (
            p_notes.strip()
            .lower()
            .replace("[", "")
            .replace("]", "")
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
        )
        if "frueh" in normalized or "fruh" in normalized or "early" in normalized:
            return "F"
        if "tag" in normalized or "day" in normalized:
            return "T"
        if "spaet" in normalized or "spat" in normalized or "late" in normalized:
            return "S"
        return None

    def load_monthly_booking_entries(
        self,
        p_year: int,
        p_month: int,
    ) -> list[dict[str, str]]:
        year = int(p_year)
        month = int(p_month)
        aggregated: dict[tuple[str, str, str, str], dict[str, str | int]] = {}

        for file_path in booking_csv_files():
            with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.reader(csv_file, delimiter=";")
                header = None
                for row in reader:
                    if not row:
                        continue
                    if "Task - Task type" in row:
                        header = row
                        break
                if header is None:
                    continue

                index_map = {name: idx for idx, name in enumerate(header)}
                required = ["Date", "User", "Task - Task type", "Notes", "Time (Hours)"]
                if any(key not in index_map for key in required):
                    continue
                task_name_index = index_map.get("Task")

                for row in reader:
                    if len(row) < len(header):
                        continue
                    task_type = row[index_map["Task - Task type"]].strip().lower()
                    if task_type != "on call":
                        continue
                    try:
                        booking_date = datetime.strptime(
                            row[index_map["Date"]].strip(),
                            "%d-%m-%y",
                        ).date()
                    except ValueError:
                        continue
                    if booking_date.year != year or booking_date.month != month:
                        continue

                    slot = self._parse_slot_from_notes(row[index_map["Notes"]])
                    if slot is None:
                        continue

                    units = self.parse_booking_units(row[index_map["Time (Hours)"]])
                    if units is None or units == 0:
                        continue

                    user = row[index_map["User"]].strip()
                    notes = row[index_map["Notes"]].strip()
                    task_name = ""
                    if task_name_index is not None and task_name_index < len(row):
                        task_name = row[task_name_index].strip()

                    key = (booking_date.isoformat(), user, slot, task_name.casefold())
                    entry = aggregated.setdefault(
                        key,
                        {
                            "booking_date": booking_date.isoformat(),
                            "user": user,
                            "slot": slot,
                            "notes": notes,
                            "task_name": task_name,
                            "source_file": file_path.name,
                            "units": 0,
                        },
                    )
                    entry["units"] = int(entry["units"]) + int(units)

        entries: list[dict[str, str]] = []
        for entry in aggregated.values():
            units = int(entry["units"])
            if units <= 0:
                continue
            for _ in range(units):
                entries.append(
                    {
                        "booking_date": str(entry["booking_date"]),
                        "user": str(entry["user"]),
                        "slot": str(entry["slot"]),
                        "notes": str(entry["notes"]),
                        "task_name": str(entry["task_name"]),
                        "source_file": str(entry["source_file"]),
                    }
                )
        return entries

    def load_monthly_client_utilized_entries(
        self,
        p_year: int,
        p_month: int,
    ) -> list[dict[str, str | Decimal]]:
        year = int(p_year)
        month = int(p_month)
        aggregated: dict[tuple[str, str, str], dict[str, str | Decimal | int]] = {}

        for file_path in booking_csv_files():
            with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.reader(csv_file, delimiter=";")
                header = None
                for row in reader:
                    if not row:
                        continue
                    if "Task - Task type" in row:
                        header = row
                        break
                if header is None:
                    continue

                index_map = {name: idx for idx, name in enumerate(header)}
                required = ["Date", "User", "Task - Task type", "Time (Hours)", "Task"]
                if any(key not in index_map for key in required):
                    continue

                for row in reader:
                    if len(row) < len(header):
                        continue

                    task_type = row[index_map["Task - Task type"]].strip().casefold()
                    if task_type != "client utilized":
                        continue

                    try:
                        booking_date = datetime.strptime(
                            row[index_map["Date"]].strip(),
                            "%d-%m-%y",
                        ).date()
                    except ValueError:
                        continue
                    if booking_date.year != year or booking_date.month != month:
                        continue

                    hours = self.parse_booking_hours(row[index_map["Time (Hours)"]])
                    if hours is None or hours == 0:
                        continue

                    user = row[index_map["User"]].strip()
                    task_name = row[index_map["Task"]].strip()
                    notes = ""
                    if "Notes" in index_map and index_map["Notes"] < len(row):
                        notes = row[index_map["Notes"]].strip()

                    key = (booking_date.isoformat(), user, task_name.casefold())
                    entry = aggregated.setdefault(
                        key,
                        {
                            "booking_date": booking_date.isoformat(),
                            "user": user,
                            "task_name": task_name,
                            "hours": Decimal("0"),
                            "booking_count": 0,
                            "notes": notes,
                            "source_file": file_path.name,
                        },
                    )
                    entry["hours"] = Decimal(entry["hours"]) + hours
                    entry["booking_count"] = int(entry["booking_count"]) + 1

        entries: list[dict[str, str | Decimal]] = []
        for entry in aggregated.values():
            hours = Decimal(entry["hours"])
            if hours == 0:
                continue

            entries.append(
                {
                    "booking_date": str(entry["booking_date"]),
                    "user": str(entry["user"]),
                    "task_name": str(entry["task_name"]),
                    "hours": hours,
                    "notes": str(entry["notes"]),
                    "source_file": str(entry["source_file"]),
                }
            )
        return entries

    def load_monthly_overtime_entries(
        self,
        p_year: int,
        p_month: int,
    ) -> list[dict[str, str | Decimal | int]]:
        year = int(p_year)
        month = int(p_month)
        aggregated: dict[tuple[str, str, str], dict[str, str | Decimal | int]] = {}

        for file_path in booking_csv_files():
            with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.reader(csv_file, delimiter=";")
                header = None
                for row in reader:
                    if not row:
                        continue
                    if "Task - Task type" in row:
                        header = row
                        break
                if header is None:
                    continue

                index_map = {name: idx for idx, name in enumerate(header)}
                required = ["Date", "User", "Task", "Time (Hours)", "Notes"]
                if any(key not in index_map for key in required):
                    continue

                for row in reader:
                    if len(row) < len(header):
                        continue
                    task_name = row[index_map["Task"]].strip()
                    if not self._is_overtime_task(task_name):
                        continue

                    try:
                        booking_date = datetime.strptime(
                            row[index_map["Date"]].strip(),
                            "%d-%m-%y",
                        ).date()
                    except ValueError:
                        continue
                    if booking_date.year != year or booking_date.month != month:
                        continue

                    hours = self.parse_booking_hours(row[index_map["Time (Hours)"]])
                    if hours is None or hours == 0:
                        continue

                    user = row[index_map["User"]].strip()
                    notes = row[index_map["Notes"]].strip()
                    key = (booking_date.isoformat(), user, task_name.casefold())
                    entry = aggregated.setdefault(
                        key,
                        {
                            "booking_date": booking_date.isoformat(),
                            "user": user,
                            "task_name": task_name,
                            "hours": Decimal("0"),
                            "booking_count": 0,
                            "notes": notes,
                            "source_file": file_path.name,
                        },
                    )
                    entry["hours"] = Decimal(entry["hours"]) + hours
                    entry["booking_count"] = int(entry["booking_count"]) + 1

        entries: list[dict[str, str | Decimal | int]] = []
        for entry in aggregated.values():
            hours = Decimal(entry["hours"])
            if hours == 0:
                continue
            entry["hours"] = hours
            entries.append(entry)
        return entries

    def summarize_monthly_compensation_from_bookings(
        self,
        p_booking_entries: list[dict[str, str]],
        p_overtime_entries: list[dict[str, str | Decimal]],
        p_analysts: list[object],
        p_location_filter: str | None = None,
    ) -> list[dict[str, str | int]]:
        analysts_by_name: dict[str, object] = {}
        for analyst in p_analysts:
            analysts_by_name[self._normalize_person_name(str(analyst.buchungsname))] = analyst

        location_filter = p_location_filter.strip().upper() if p_location_filter else None
        aggregated: dict[int, dict[str, str | int]] = {}

        for entry in p_booking_entries:
            analyst = analysts_by_name.get(self._normalize_person_name(entry["user"]))
            if analyst is None:
                continue
            location_id = str(analyst.oncall_location_id).strip().upper()
            if location_filter and location_id != location_filter:
                continue

            analyst_id = int(analyst.id)
            slot = entry["slot"]
            booking_day = date.fromisoformat(entry["booking_date"])
            amount = self._calculate_amount_for_day_slot(location_id, booking_day, slot)

            if analyst_id not in aggregated:
                aggregated[analyst_id] = {
                    "analyst_id": analyst_id,
                    "buchungsname": str(analyst.buchungsname),
                    "oncall_location_id": location_id,
                    "shift_count_f": 0,
                    "shift_count_t": 0,
                    "shift_count_s": 0,
                    "total_amount_eur": 0,
                    "overtime_ger_25_hours": "0",
                    "overtime_ger_50_hours": "0",
                    "overtime_ind_mo_sa_hours": "0",
                    "overtime_ind_so_hours": "0",
                }

            if slot == "F":
                aggregated[analyst_id]["shift_count_f"] = int(aggregated[analyst_id]["shift_count_f"]) + 1
            elif slot == "T":
                aggregated[analyst_id]["shift_count_t"] = int(aggregated[analyst_id]["shift_count_t"]) + 1
            else:
                aggregated[analyst_id]["shift_count_s"] = int(aggregated[analyst_id]["shift_count_s"]) + 1

            aggregated[analyst_id]["total_amount_eur"] = (
                int(aggregated[analyst_id]["total_amount_eur"]) + int(amount)
            )

        for entry in p_overtime_entries:
            analyst = analysts_by_name.get(self._normalize_person_name(str(entry["user"])))
            if analyst is None:
                continue
            location_id = str(analyst.oncall_location_id).strip().upper()
            if location_filter and location_id != location_filter:
                continue
            analyst_id = int(analyst.id)
            if analyst_id not in aggregated:
                aggregated[analyst_id] = {
                    "analyst_id": analyst_id,
                    "buchungsname": str(analyst.buchungsname),
                    "oncall_location_id": location_id,
                    "shift_count_f": 0,
                    "shift_count_t": 0,
                    "shift_count_s": 0,
                    "total_amount_eur": 0,
                    "overtime_ger_25_hours": "0",
                    "overtime_ger_50_hours": "0",
                    "overtime_ind_mo_sa_hours": "0",
                    "overtime_ind_so_hours": "0",
                }

            bucket = self._overtime_bucket_for_task(str(entry.get("task_name", "")))
            if bucket is None:
                continue
            key_map = {
                "GER_25": "overtime_ger_25_hours",
                "GER_50": "overtime_ger_50_hours",
                "IND_MO_SA": "overtime_ind_mo_sa_hours",
                "IND_SO": "overtime_ind_so_hours",
            }
            target_key = key_map[bucket]
            previous = Decimal(str(aggregated[analyst_id][target_key]))
            updated = previous + Decimal(entry["hours"])
            aggregated[analyst_id][target_key] = self._format_hours(updated)

        rows = list(aggregated.values())
        rows.sort(key=lambda row: str(row["buchungsname"]))
        return rows

    def build_booking_compensation_details(
        self,
        p_booking_entries: list[dict[str, str]],
        p_overtime_entries: list[dict[str, str | Decimal]],
        p_analysts: list[object],
        p_analyst_id: int,
        p_location_filter: str | None = None,
    ) -> list[dict[str, str | int]]:
        analyst_by_id: dict[int, object] = {int(a.id): a for a in p_analysts}
        analyst = analyst_by_id.get(int(p_analyst_id))
        if analyst is None:
            return []

        location_id = str(analyst.oncall_location_id).strip().upper()
        location_filter = p_location_filter.strip().upper() if p_location_filter else None
        if location_filter and location_id != location_filter:
            return []

        normalized_target = self._normalize_person_name(str(analyst.buchungsname))
        details: list[dict[str, str | int]] = []
        for entry in p_booking_entries:
            if self._normalize_person_name(entry["user"]) != normalized_target:
                continue
            booking_day = date.fromisoformat(entry["booking_date"])
            day_type = self.determine_day_type(booking_day)
            amount = self._calculate_amount_for_day_slot(location_id, booking_day, entry["slot"])
            details.append(
                {
                    "booking_date": booking_day.strftime("%d.%m.%Y"),
                    "entry_type": "On Call",
                    "user": entry["user"],
                    "task_or_slot": entry["slot"],
                    "day_type": day_type,
                    "hours": "1",
                    "amount_eur": amount,
                    "notes": entry.get("notes", ""),
                    "source_file": entry.get("source_file", ""),
                }
            )
        for entry in p_overtime_entries:
            if self._normalize_person_name(str(entry["user"])) != normalized_target:
                continue
            booking_day = date.fromisoformat(str(entry["booking_date"]))
            details.append(
                {
                    "booking_date": booking_day.strftime("%d.%m.%Y"),
                    "entry_type": "Überstunde",
                    "user": str(entry["user"]),
                    "task_or_slot": str(entry["task_name"]),
                    "day_type": "",
                    "hours": self._format_hours(Decimal(entry["hours"])),
                    "amount_eur": "",
                    "notes": str(entry.get("notes", "")),
                    "source_file": str(entry.get("source_file", "")),
                }
            )
        details.sort(key=lambda row: str(row["booking_date"]))
        return details

    def _is_bavaria_holiday(self, p_day: date) -> bool:
        easter = self._easter_sunday(p_day.year)
        movable = {
            easter - timedelta(days=2),   # Karfreitag
            easter + timedelta(days=1),   # Ostermontag
            easter + timedelta(days=39),  # Christi Himmelfahrt
            easter + timedelta(days=50),  # Pfingstmontag
            easter + timedelta(days=60),  # Fronleichnam
        }
        fixed = {
            date(p_day.year, 1, 1),    # Neujahr
            date(p_day.year, 1, 6),    # Heilige Drei Koenige
            date(p_day.year, 5, 1),    # Tag der Arbeit
            date(p_day.year, 10, 3),   # Tag der Deutschen Einheit
            date(p_day.year, 11, 1),   # Allerheiligen
            date(p_day.year, 12, 25),  # Weihnachten
            date(p_day.year, 12, 26),  # Weihnachten
        }
        return p_day in fixed or p_day in movable

    def _easter_sunday(self, p_year: int) -> date:
        # Gauß/Oudin-Algorithmus (Gregorianischer Kalender)
        a = p_year % 19
        b = p_year // 100
        c = p_year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(p_year, month, day)
