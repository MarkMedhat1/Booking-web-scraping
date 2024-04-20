import tkinter as tk
from tkinter import messagebox
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup


def scrape_hotel_data():
    url = 'https://www.booking.com/searchresults.html?ss=hur&ssne=Cairo&ssne_untouched=Cairo&label=gen173nr-1FCAEoggI46AdIM1gEaEOIAQGYATG4ARfIAQzYAQHoAQH4AQKIAgGoAgO4AreSo68GwAIB0gIkZWYxMzdhNTEtZDA5YS00YTJkLWI1ODctOGRkYjJmNmM2MTk22AIF4AIB&sid=2712e21d7b8eaa4091d8d752e443d91d&aid=304142&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=-290029&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=8aafa7a8e34c00b8&ac_meta=GhA4YWFmYTdhOGUzNGMwMGI4IAAoATICZW46A2h1ckAASgBQAA%3D%3D&checkin=2024-03-13&checkout=2024-04-30&group_adults=2&no_rooms=1&group_children=0'
    headers = {'User-Agent': 'Chrome/55.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    hotels = soup.findAll('div', {'data-testid': 'property-card'})
    hotels_data = []
    for hotel in hotels:
        name_element = hotel.find('div', {'class': 'f6431b446c'})
        name = name_element.text.strip()
        location_element = hotel.find('span', {'data-testid': 'address'})
        location = location_element.text.strip()
        rate_element = hotel.find('div', {'class': 'a3b8729ab1'})
        rate = rate_element.text.strip()
        hotels_data.append({
            'name': name,
            'location': location,
            'rate': rate
        })

    conn = sqlite3.connect('scraped_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS hotels (name TEXT, location TEXT, rate TEXT)''')

    for hotel in hotels_data:
        c.execute("INSERT INTO hotels (name, location, rate) VALUES (?, ?, ?)",
                  (hotel['name'], hotel['location'], hotel['rate']))

    conn.commit()
    conn.close()
    messagebox.showinfo("Scraping Completed", "Hotel data scraped and saved to database")


def display_hotel_data():
    conn = sqlite3.connect('scraped_data.db')
    df = pd.read_sql_query("SELECT * FROM hotels", conn)
    conn.close()

    root = tk.Tk()
    root.title("Scraped Hotels")

    listbox = tk.Listbox(root)
    listbox.pack()

    for index, row in df.iterrows():
        listbox.insert(tk.END, f"{row['name']} - {row['location']} - {row['rate']}")

    root.mainloop()


root = tk.Tk()
root.title("Hotel Scraping App")
root.geometry("500x300")
root.configure(bg='gray10')
scrape_button = tk.Button(root, text="Check for updates ", command=scrape_hotel_data)
scrape_button.pack(pady=10)

display_button = tk.Button(root, text="Display Hotel Data", command=display_hotel_data)
display_button.pack(pady=10)

root.mainloop()
