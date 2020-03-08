import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from wordcloud import WordCloud
import requests
import re
from FormatData import FormatData

def get_card_counts_df(card_set):
    mains = card_set.main_boards()
    
    return (
        pd.DataFrame(
            mains[~mains.set.isna()]
            .groupby(["card", "color"])
            ["count"]
            .sum()
        )
        .sort_values(
            "count",
            ascending=False
        )
        .reset_index()
    )

def make_table(df, color, ax):

    ax.set_axis_off()
    ax.set_frame_on(False)

    table = pd.plotting.table(
        ax, df[df.color.str.contains(color)].head(5), 
        loc="center")
    table.auto_set_column_width(0)
    table.set_fontsize(16)
    table.scale(1, 2)
    return table

def gather_tables(df):
    fig, axes = plt.subplots(3, 2, figsize=(15, 10))
    plt.subplots_adjust(wspace=2, hspace=600)
    make_table(df, "", axes[0][0])
    make_table(df, "W", axes[0][1])
    make_table(df, "U", axes[1][0])
    make_table(df, "B", axes[1][1])
    make_table(df, "R", axes[2][0])
    make_table(df, "G", axes[2][1])
    
    return fig

def save_tables(df, file):
    tables = gather_tables(df)
    plt.savefig(r"C:\Users\gfmar_000\Desktop\MTG Webpage\\" + file)
    plt.close(tables)

def plot_colors_bar(color_count, axs):
    
    x = list(color_count.keys())
    y = list(color_count.values())
    
    axs.bar(x, y)
    
    for x_coord in color_count:
        axs.annotate(color_count[x_coord], (x_coord, color_count[x_coord] + 0.75))
    
    return axs

def plot_colors_pie(color_count, axs):
    
    axs.pie(color_count.values(),
           colors = ["white", "blue", "black", "red", "green", "grey"],
           wedgeprops={"edgecolor": "k"},
           labels=["W", "U", "B", "R", "G", "A"],
           autopct="%.1f%%",
           pctdistance=0.5)
    
    centre_circle = plt.Circle((0,0),0.70,fc='white', ec="black")
    plt.sca(axs)
    plt.gca().add_artist(centre_circle)
    
    return axs

def plot_sets(set_count, axs):
    
    axs.pie(
        set_count.values(),
        colors = [
            "white",
            "blue",
            "black",
            "red",
            "green",
            "grey"
        ],
        wedgeprops={"edgecolor": "black"},
        labels=["THB", "ELD", "M20", "WAR", "RNA", "GRN"],
        autopct="%.1f%%",
        pctdistance=0.5
    )
    
    centre_circle = plt.Circle((0,0),0.70,fc='white', ec="black")
    plt.sca(axs)
    plt.gca().add_artist(centre_circle)
    
    
    return axs

def compare_standard_colors(set_1_data, set_2_data, set_1="ELD", set_2="THB"):
    
    labels=["W", "U", "B", "R", "G", "A"]
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    plot_colors_bar(set_1_data, axs[0][0])
    plot_colors_bar(set_2_data, axs[0][1])
    
    
    plot_colors_pie(set_1_data, axs[1][0])
    plot_colors_pie(set_2_data, axs[1][1])

    axs[0][0].set_title(f"Colors in {set_1} Standard")

    axs[0][1].set_title(f"Colors in {set_2} Standard")
    
    fig.suptitle("Comparing Colors in Standard")
    
    return fig

def compare_standard_sets(set_1_data, set_2_data, set_1="ELD", set_2="THB"):
    
    fig, axs = plt.subplots(1, 2, figsize=(12, 12))

    plot_sets(set_1_data, axs[0])
    plot_sets(set_2_data, axs[1])
    
    axs[0].set_title(f"Sets in {set_1} Standard", loc="left")
    axs[1].set_title(f"Sets in {set_2} Standard", loc="left")
    
    fig.suptitle("Comparing Sets in Standard")
    
    return fig

def generate_pdf(set_1="ELD", set_2="THB"):
    
    set_1_data = FormatData("Set Metrics", set_1)
    set_2_data = FormatData("Set Metrics", set_2)
    
    with PdfPages("test_pdf.pdf") as export_pdf:
    
        colors_fig = compare_standard_colors(set_1_data.color_count, set_2_data.color_count)
        export_pdf.savefig()
        plt.close(colors_fig)

        sets_fig = compare_standard_sets(set_1_data.set_count, set_2_data.set_count)
        export_pdf.savefig()
        plt.close(sets_fig)

def get_card_info(card_name: str) -> list:
    
    url = "https://api.scryfall.com/cards/search?q=name%3A" + card_name
    
    api_results = requests.get(url)
    
    api_json = api_results.json()["data"][0]
    
    return [api_json["colors"], api_json["set"]]

def get_card_name(set_code: str, collectors_number: str) -> str:
    
    url = "https://api.scryfall.com/cards/" + set_code + "/" + collectors_number
    
    api_results = requests.get(url)
    
    api_json = api_results.json()
    
    return api_json["name"]

def get_set_info(set_code: str) -> (dict, dict):
    
    url = "https://api.scryfall.com/cards/search?order=set&q=set%3A" + set_code
    page = 1
    
    api_results = requests.get(url)
    
    api_json = api_results.json()
    
    set_info_by_name = {}
    set_info_by_number = {}
    
    for card in api_json["data"]:
        set_info_by_name[card["name"]] = card["colors"]
        set_info_by_number[card["collector_number"]] = card["name"]
        
    check_for_more = api_json["has_more"]
  
    while check_for_more:
        
        page += 1
        
        api_results_next_page = requests.get(url + "&page=" + str(page))
        
        api_json_next_page = api_results_next_page.json()
        
        for card in api_json_next_page["data"]:
            set_info_by_name[card["name"]] = card["colors"]
            set_info_by_number[card["collector_number"]] = card["name"]
        
        check_for_more = api_json_next_page["has_more"]
    
    return set_info_by_name, set_info_by_number

def format_decklist(decklist: str) -> str:
    
    regex_split = re.split(r'^ [0-9] ', decklist)[0]
    
    return regex_split.split("\n")

def list_colors(card_name: str, set_code: str) -> str:
    
    for card in standard_sets[set_code]:
        if (re.match(card_name + ".+", card) or card_name == card):
            colors = standard_sets[set_code][card]
    
    return colors

def split_qty_and_name(formatted_decklist: str) -> (list, list):
    
    qty_column = []
    name_column = []
    
    for card in formatted_decklist:
        if card == "":
            continue
        
        qty, name = card.split(maxsplit=1)
        
        qty_column.append(qty)
        name_column.append(name)
    
    return qty_column, name_column

def export_deck(mtga_decklist):
    color_order = {
        "W": 1,
        "U": 2,
        "B": 3,
        "R": 4,
        "G": 5
    }
    decklist = format_decklist(mtga_decklist)
    decklist_count, decklist_name = split_qty_and_name(decklist)
    
    color_identity = []
    for name in decklist_name:
        for set_code in standard_sets:
            if set_code.upper() in name:
                colors = list_colors(name.split(" (")[0], set_code)
                colors.sort(key=lambda x: color_order[x])
                color_identity.append("".join(colors))
    
    with open("decklists.txt", "a") as text_file:
        text_file.write("\n---\n")
        for card in list(zip(
        	decklist_count, 
        	decklist_name, 
        	color_identity
    	)):
            text_file.write(
            	card[0] + ";" + card[1] + ";" + card[2] + "\n"
        	)

if __name__ == "__main__":

	thb = FormatData("Set Metrics", "THB")
	eld = FormatData("Set Metrics", "ELD")

	thb_card_counts = get_card_counts_df(thb)
	eld_card_counts = get_card_counts_df(eld)

	save_tables(thb_card_counts, "thb_top_5.png")
	save_tables(eld_card_counts, "eld_top_5.png")

	set_1_colors = eld.color_count
	set_2_colors = thb.color_count

	color_comparison = compare_standard_colors(set_1_colors, set_2_colors)
	plt.savefig(r".\MTG Webpage\compare_colors.png")
	plt.close(color_comparison)