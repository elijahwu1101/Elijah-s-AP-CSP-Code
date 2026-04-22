import pandas as pd
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, OptionList, Label, DataTable, Button, Log
from textual.widgets.option_list import Option

class PlantFinderApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id='left_panel') as left_panel:
                left_panel.styles.width = "3fr"
                yield Label("Watering Frequency:")
                yield OptionList(
                    Option("Very Frequent", id="very frequent"),
                    Option("Frequent", id="frequence"),
                    Option("Moderate", id="moderate"),
                    Option("Rare", id="rare"),
                    Option("None", id="none"),
                    id = "WaterOptionList"
                )

                yield Label("Sunlight:")
                yield OptionList(
                    Option("Bright", id="bright"),
                    Option("Medium", id="medium"),
                    Option("Low", id="low"),
                    Option("None", id="none"),
                    id = "SunlightOptionList"
                )

                yield Label("Temperature Range:")
                yield OptionList(
                    Option("80-90", id="80-90"),
                    Option("70-80", id="70-80"),
                    Option("60-70", id="60-70"),
                    Option("None", id="none"),
                    id = "TempOptionList"
                )

                yield Button('Find', id='find_button')

            with Vertical(id='right_panel') as right_panel:
                right_panel.styles.width = "7fr"

                self.log_widget = Log(id="log")
                self.log_widget.styles.height = 10
                yield self.log_widget
                yield DataTable(id="main-table") 

        yield Footer()

    def on_mount(self) -> None:
        self.water_optionlist = self.query_one('#WaterOptionList', OptionList)
        self.sunlight_optionlist = self.query_one('#SunlightOptionList', OptionList)
        self.temp_optionlist = self.query_one('#TempOptionList', OptionList)
        
        self.water_optionlist.highlighted = self.water_optionlist.get_option_index("none") 
        self.sunlight_optionlist.highlighted = self.sunlight_optionlist.get_option_index("none") 
        self.temp_optionlist.highlighted = self.temp_optionlist.get_option_index("none") 

        self.plants_db = load_plants()
        self.table = self.query_one("#main-table", DataTable)
        self.log_widget.write_line('App start!')


    def get_plants_filters(self):
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

    def refresh_table(self, dt: DataTable, df: pd.DataFrame) -> None:
        dt.clear(columns=True)          # wipe existing data and columns
        dt.add_columns(*df.columns.tolist())
        for row in df.itertuples(index=False):
            dt.add_row(*row)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "find_button":
            plant_filters = self.get_plants_filters()
            plants_found = plants_finder(self.plants_db, plant_filters)
            self.log_widget.write_line("Found " + str(plants_found.shape[0]) + " plants!")
            self.refresh_table(self.table, plants_found)



class PlantFilters:
    def __init__ (self, watering=None, sunlight=None, temperature = None):
        if watering == 'none':
            self.watering = None
        else:
            self.watering = watering

        if sunlight == 'none':
            self.sunlight = None
        else:
            self.sunlight = sunlight

        if temperature == 'none':
            self.temperature = None
        else:
            self.temperature = temperature
    
    @property
    def watering(self):
        return self._watering
    
    @watering.setter
    def watering(self, value):
        self._watering = value

    @property
    def brightness(self):
        return self._brightness
    
    @brightness.setter
    def brightness(self, value):
        self._brightness = value
    
    @property 
    def low_temperature(self):
        return self._low_temperature
    
    @low_temperature.setter
    def low_temperature(self, value):
        self._temperature = value
    
    @property
    def high_temperature(self):
        return self._high_temperature

    @high_temperature.setter
    def high_temperature(self, value):
        self._high_temperature = value
    
    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, value):
        self._temperature = value
        if (value is not None):
            self._low_temperature, self._high_temperature = value.split("-")
            self._low_temperature = int(self._low_temperature)
            self._high_temperature = int(self._high_temperature)
        else:
            self._low_temperature = None
            self._high_temperature = None
    
    def quit(self):
        return False



def welcome_screen():
    print("Welcome to the Automatic Plant Picker")
    input("Please press the ENTER key to begin: ")

def option_selector(option_list):
    option_size = len(option_list)
    for i, option in enumerate(option_list, start=0):
        print(f"{i}. {option}")
    
    while True:
        choice = input("\nEnter your choice [0-" + str(option_size-1) + "]: ")
        if choice in {str(i) for i in range(0, option_size)}:
            print(f"You selected: {option_list[int(choice)]}")
            print()
            break
        print("Invalid input. Please enter a number between the shown range. ")

    if int(choice) == option_size - 1:
        return None
    else:
        return option_list[int(choice)]

def get_plant_filters():
    watering_options = ["Very Frequent", "Frequent", "Moderate", "Rare", "It does not matter"]
    sunlight_options = ["Low", "Medium", "Bright", "It does not matter"]
    temp_options = ["60-70", "70-80", "80-90", "It does not matter"]

    watering_selection = option_selector(watering_options)
    sunlight_selection = option_selector(sunlight_options)
    temp_selection = option_selector(temp_options)

    return PlantFilters(watering_selection, sunlight_selection, temp_selection)

def plants_finder(plants_db, plant_filters):
    print(plant_filters.watering)
    print(plant_filters.sunlight)
    print(plant_filters.temperature)

    filtered_plants = plants_db

    if plant_filters.watering is not None:
        filtered_plants = filtered_plants[filtered_plants["watering"].str.lower() == plant_filters.watering.lower()]
    
    if plant_filters.sunlight is not None:
        filtered_plants = filtered_plants[filtered_plants["sunlight"].str.lower() == plant_filters.sunlight.lower()]
    
    if plant_filters.temperature is not None:
        filtered_plants = filtered_plants[~((plant_filters.low_temperature > filtered_plants["upper_temperature"]) | (plant_filters.high_temperature < filtered_plants["lower_temperature"]))]

    return (filtered_plants)

def show_results(plants_df):
    print()
    print("There were " + str(plants_df.shape[0]) + " plants that satisfy these criteria!")

    if plants_df is not None:
        print(plants_df)
    
def load_plants():
    df = pd.read_csv("Elijah-Plant-Data.csv")
    df["lower_temperature"] = df["lower_temperature"].astype(int)
    df["upper_temperature"] = df["upper_temperature"].astype(int)
    return(df)
if __name__ == '__main__':
    PlantFinderApp().run()
