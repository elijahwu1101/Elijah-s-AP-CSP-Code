import csv
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, OptionList, Label, DataTable, Button, Log
from textual.widgets.option_list import Option


class PlantFinderApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal():
            with Vertical(id="left_panel") as left_panel:
                left_panel.styles.width = "3fr"

                yield Label("Watering Frequency:")
                yield OptionList(
                    Option("Very Frequent", id="very frequent"),
                    Option("Frequent", id="frequent"),
                    Option("Moderate", id="moderate"),
                    Option("Rare", id="rare"),
                    Option("None", id="none"),
                    id="WaterOptionList",
                )

                yield Label("Sunlight:")
                yield OptionList(
                    Option("Bright", id="bright"),
                    Option("Medium", id="medium"),
                    Option("Low", id="low"),
                    Option("None", id="none"),
                    id="SunlightOptionList",
                )

                yield Label("Temperature Range:")
                yield OptionList(
                    Option("80-90", id="80-90"),
                    Option("70-80", id="70-80"),
                    Option("60-70", id="60-70"),
                    Option("None", id="none"),
                    id="TempOptionList",
                )

                yield Label("More information:")
                yield DataTable(id="more-info-table")

                yield Button("Find", id="find_button")

            with Vertical(id="right_panel") as right_panel:
                right_panel.styles.width = "7fr"

                self.log_widget = Log(id="log")
                self.log_widget.styles.height = 10
                yield self.log_widget
                yield DataTable(id="main-table")

        yield Footer()

    def on_mount(self) -> None:
        self.water_optionlist = self.query_one("#WaterOptionList", OptionList)
        self.sunlight_optionlist = self.query_one("#SunlightOptionList", OptionList)
        self.temp_optionlist = self.query_one("#TempOptionList", OptionList)

        self.columns_to_display = [
            "common_name",
            "temperature_range",
            "sunlight",
            "watering",
        ]

        self.water_optionlist.highlighted = self.water_optionlist.get_option_index("none")
        self.sunlight_optionlist.highlighted = self.sunlight_optionlist.get_option_index("none")
        self.temp_optionlist.highlighted = self.temp_optionlist.get_option_index("none")

        self.plants_db = load_plants()
        self.plants_found = []

        self.table = self.query_one("#main-table", DataTable)
        self.more_info_table = self.query_one("#more-info-table", DataTable)

        self.log_widget.write_line("App start!")

    def get_plants_filters(self):
        watering_selection = None
        sunlight_selection = None
        temp_selection = None

        index = self.water_optionlist.highlighted
        if index is not None:
            watering_selection = self.water_optionlist.get_option_at_index(index).id

        index = self.sunlight_optionlist.highlighted
        if index is not None:
            sunlight_selection = self.sunlight_optionlist.get_option_at_index(index).id

        index = self.temp_optionlist.highlighted
        if index is not None:
            temp_selection = self.temp_optionlist.get_option_at_index(index).id

        return PlantFilters(watering_selection, sunlight_selection, temp_selection)

    def refresh_table(self, dt: DataTable, plants: list[dict], columns: list[str]) -> None:
        dt.clear(columns=True)
        dt.add_columns(*columns)

        for plant in plants:
            dt.add_row(*(str(plant[column]) for column in columns))

    def refresh_more_info_table(self, dt: DataTable, rows: list[dict]) -> None:
        dt.clear(columns=True)
        dt.add_columns("Field", "Value")

        for row in rows:
            dt.add_row(row["Field"], row["Value"])

    def create_more_info_data(self, event: DataTable.CellHighlighted):
        row_index = event.coordinate[0]
        plant = self.plants_found[row_index]

        rows = []
        for key, value in plant.items():
            rows.append({"Field": key, "Value": str(value)})

        return rows

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        if event.data_table.id == "main-table" and self.plants_found:
            more_info_rows = self.create_more_info_data(event)
            self.refresh_more_info_table(self.more_info_table, more_info_rows)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "find_button":
            plant_filters = self.get_plants_filters()
            self.plants_found = plants_finder(self.plants_db, plant_filters)

            self.log_widget.write_line(f"Found {len(self.plants_found)} plants!")
            self.refresh_table(self.table, self.plants_found, self.columns_to_display)


class PlantFilters:
    def __init__(self, watering=None, sunlight=None, temperature=None):
        self.watering = None if watering == "none" else watering
        self.sunlight = None if sunlight == "none" else sunlight
        self.temperature = None if temperature == "none" else temperature

        if self.temperature is not None:
            low, high = self.temperature.split("-")
            self.low_temperature = int(low)
            self.high_temperature = int(high)
        else:
            self.low_temperature = None
            self.high_temperature = None


def load_plants():
    plants = []

    with open("Elijah-Plant-Data.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            plant = dict(row)
            plant["lower_temperature"] = int(plant["lower_temperature"])
            plant["upper_temperature"] = int(plant["upper_temperature"])
            plants.append(plant)

    return plants


def plants_finder(plants_db, plant_filters):
    filtered_plants = []

    for plant in plants_db:
        matches = True

        if plant_filters.watering is not None:
            if plant["watering"].lower() != plant_filters.watering.lower():
                matches = False

        if plant_filters.sunlight is not None:
            if plant["sunlight"].lower() != plant_filters.sunlight.lower():
                matches = False

        if plant_filters.temperature is not None:
            if (
                plant_filters.low_temperature > plant["upper_temperature"]
                or plant_filters.high_temperature < plant["lower_temperature"]
            ):
                matches = False

        if matches:
            filtered_plants.append(plant)

    return filtered_plants


if __name__ == "__main__":
    PlantFinderApp().run()