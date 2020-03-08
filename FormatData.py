import pandas as pd
import matplotlib.pyplot as plt

class InputError(Exception):
    
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class FormatData(InputError):
    
    def read_sheets(self, format_name, sheet_name):
        
        return pd.read_excel(
            f"{format_name}.xlsx", 
            sheet_name=sheet_name, 
            encoding="latin-1"
        )

    def count_colors(self, df):

        color_list = ["W", "U", "B", "R", "G", "A"]
        color_count = {color: 0 for color in color_list}

        for color in color_list:
            for index, row in df.iterrows():
                if color in row.color:
                    color_count[color] += 1
        return color_count
    
    def count_sets(self, df):
    
        set_list = ["THB", "ELD", "M20", "WAR", "RNA", "GRN"]
        set_count = {set_name: 0 for set_name in set_list}

        for index, row in df.iterrows():
            if row.set in set_list:
                set_count[row.set] += 1
            else:
                pass

        return set_count
    
        
    def __init__(self, format_name, block):
        
        self.data = self.read_sheets(format_name, block)
        self.color_count = self.count_colors(self.data)
        self.set_count = self.count_sets(self.data)
    
    def main_boards(self):
        
        return self.data[self.data.board == "main"].copy()
    
    def side_boards(self):
        
        return self.data[self.data.board == "side"].copy()
    
    def return_table(self, df):
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        ax.set_axis_off()
        ax.set_frame_on(False)

        table = pd.plotting.table(ax, df, loc="center")

        table.auto_set_column_width(0)
        table.set_fontsize(16)
        table.scale(10,5)
        
        
        return table
    
    def top_five(self, board="main", color=""):

        board_dict = {
            "main": self.main_boards(),
            "side": self.side_boards()
        }

        board = board_dict[board]

        card_counts = (
            board[
                ~(board.set.isna()) 
                & (board.color.str.contains(color))
            ].card
            .value_counts()[0:5]
        )
        
        return self.return_table(card_counts)
    
    def get_deck(self, deck_index):
        
        deck = self.data[self.data.deck_index == deck_index]
        
        if len(deck) > 0:
            return deck
        else:
            raise InputError(
                deck_index, 
                "No deck with this deck index in this set."
            )