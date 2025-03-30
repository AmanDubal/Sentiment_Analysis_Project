import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to classify text using TextBlob
def classify_text(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    
    if sentiment > 0:
        return "positive"
    elif sentiment < 0:
        return "negative"
    else:
        return "neutral"

# Function to truncate long text to a maximum of 20 words
def truncate_text(text, max_words=20):
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return text

# Function to load CSV or Excel file and choose the text column
def load_file():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")])
    if file_path:
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='latin1')
            
            column_names = df.columns.tolist()
            column_list.delete(0, tk.END)
            for name in column_names:
                column_list.insert(tk.END, name)
            column_frame.pack(pady=5)
            activate_widgets()  # Activate widgets after loading file
        except pd.errors.ParserError as e:
            messagebox.showerror("Error", f"Error parsing file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")

# Function to classify the texts in the chosen column
def classify_column(entries_count):
    global df
    selected_column_index = column_list.curselection()
    if not selected_column_index:
        messagebox.showwarning("Warning", "PleaSSSse select a text column.")
        return

    text_column = column_list.get(selected_column_index[0])
    if text_column not in df.columns:
        messagebox.showerror("Error", "Selected column does not exist in the DataFrame.")
        return
    
    texts = df[text_column].dropna().tolist()  # Remove NaN values

    if len(texts) < entries_count:
        messagebox.showerror("Error", f"Not enough entries. The column contains only {len(texts)} entries.")
        return

    global sentiment_counts
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    
    result_text_widget.config(state=tk.NORMAL)  # Enable editing of the Text widget
    result_text_widget.delete(1.0, tk.END)  # Clear previous results
    for t in texts[:entries_count]:
        result = classify_text(t)
        sentiment_counts[result] += 1
        color = "black"
        if result == "positive":
            color = "green"
        elif result == "negative":
            color = "red"
        truncated_text = truncate_text(t)
        result_text_widget.insert(tk.END, f"Text: {truncated_text}\nSentiment: {result}\n\n", (result,))
        result_text_widget.tag_config(result, foreground=color)
    result_text_widget.config(state=tk.DISABLED)  # Disable editing after inserting text

# Function to plot the pie chart of sentiment distribution
def plot_pie_chart():
    global sentiment_counts
    if not sentiment_counts:
        messagebox.showwarning("Warning", "No sentiment data to plot. Please analyze some text first.")
        return
    
    labels = sentiment_counts.keys()
    sizes = sentiment_counts.values()
    colors = ['#ff9999','#66b3ff','#99ff99']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # Embed the plot into the Tkinter window
    chart_window = tk.Toplevel(root)
    chart_window.title("Sentiment Distribution")
    
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Function to show the about information
def show_about():
    description_label.pack(pady=10)  # Show the description below the About button

# Function to activate widgets after loading the file
def activate_widgets():
    choose_column_button.pack(pady=5)
    entries_frame.pack(pady=5)
    plot_chart_button.pack(pady=10)
    result_text_frame.pack(pady=10)
    choose_column_button.config(state=tk.NORMAL)
    plot_chart_button.config(state=tk.NORMAL)
    result_text_widget.config(state=tk.NORMAL)

# Function to style buttons with hover effect
def style_button(button):
    button.config(bg="green", fg="white", activebackground="white", activeforeground="green", bd=2, font=('Helvetica', 12), width=20, height=2)
    button.bind("<Enter>", lambda e: on_enter(button))
    button.bind("<Leave>", lambda e: on_leave(button))

# Function to handle mouse entering the button (hover effect)
def on_enter(button):
    button.config(bg="white", fg="green")

# Function to handle mouse leaving the button
def on_leave(button):
    button.config(bg="green", fg="white")

# Create the main window
root = tk.Tk()
root.title("Sentiment Analysis")
root.geometry("400x300")  # Adjusted window size
root.configure(bg='blue')  # Set the background color of the main window to blue

# Create an About button
about_button = tk.Button(root, text="About", command=show_about)
style_button(about_button)
about_button.pack(pady=10)

# Create a description label (initially hidden)
description_text = (
    "Welcome to the Sentiment Analysis Application.\n\n"
    "This tool allows you to analyze the sentiment of text data from CSV or Excel files. "
    "Load your file, select the text column, and the application will classify the sentiment "
    "of the entries as positive, negative, or neutral. You can also view a pie chart "
    "of sentiment distribution, which reflects the number of entries chosen and updates "
    "as the number of entries changes.\n\n"
    "Features:\n"
    "- Load text data from CSV or Excel files.\n"
    "- Choose the text column to analyze.\n"
    "- Analyze sentiments with options for 10, 50, or 100 entries.\n"
    "- Display sentiments in a color-coded text view.\n"
    "- Generate a pie chart showing sentiment distribution based on the selected number of entries.\n"
)

description_label = tk.Label(root, text=description_text, wraplength=700, justify="left", bg='blue', fg='yellow', font=('Helvetica', 12))
# Initially not packed

# Create a button to load the file
load_button = tk.Button(root, text="Load File", command=load_file)
style_button(load_button)
load_button.pack(pady=10)

# Create a frame for choosing the text column (initially hidden)
column_frame = tk.Frame(root)
column_list = tk.Listbox(column_frame, selectmode=tk.SINGLE, width=30, height=6)
column_scrollbar = tk.Scrollbar(column_frame, orient="vertical", command=column_list.yview)
column_list.configure(yscrollcommand=column_scrollbar.set)
column_list.pack(side=tk.LEFT, padx=5)
column_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
choose_column_button = tk.Button(column_frame, text="Choose Text Column", state=tk.DISABLED)
style_button(choose_column_button)
# Initially not packed

# Create a frame for fixed entry options (initially hidden)
entries_frame = tk.Frame(root, bg='blue')

entries_label = tk.Label(entries_frame, text="Analyze first:", bg='blue', fg='white')
entries_label.pack(side=tk.LEFT)

def create_entries_button(count):
    return tk.Button(entries_frame, text=f"{count} entries", command=lambda: classify_column(count))

for count in [10, 50, 100]:
    button = create_entries_button(count)
    style_button(button)
    button.pack(side=tk.LEFT, padx=5)

# Create a button to plot the pie chart (initially hidden)
plot_chart_button = tk.Button(root, text="Show Sentiment Chart", command=plot_pie_chart, state=tk.DISABLED)
style_button(plot_chart_button)
# Initially not packed

# Create a Text widget to display the results (initially hidden)
result_text_frame = tk.Frame(root)
result_text_widget = tk.Text(result_text_frame, wrap=tk.WORD, height=10, width=60, state=tk.DISABLED)
result_scrollbar = tk.Scrollbar(result_text_frame, orient="vertical", command=result_text_widget.yview)
result_text_widget.configure(yscrollcommand=result_scrollbar.set)
result_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# Initially not packed

# Initialize DataFrame and sentiment counts
df = pd.DataFrame()
sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

# Start the GUI event loop
root.mainloop()
