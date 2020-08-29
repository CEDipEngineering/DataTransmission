# File to make an interface for working with the applications
import tkinter as tk
import tkinter.filedialog as tkfd


class Application1:
    def __init__(self, master=None):
        self.master = master
        self.widget1 = tk.Frame(self.master)
        self.widget1.pack()
        self.game = tk.Label(self.widget1, text = 'Por favor, selecione uma imagem para ser enviada:')
        self.game["font"] = ("Verdana", "12", "bold")
        self.game.config(anchor=tk.CENTER)
        self.game.pack()
        self.button = tk.Button(self.widget1)
        self.button["text"] = "Escolher"
        self.button["font"] = ("Cambria", "16", "bold")
        self.button["width"] = 24
        self.button["command"] = self.get_image
        self.button.config(anchor=tk.CENTER)
        self.button.pack()
        self.got_img = False
    
    def get_image(self):
        file = tkfd.askopenfilename(title='Choose a file')
        if file != None:
            self.data = file
            self.master.destroy()

class Application2:
    def __init__(self, master=None):
        self.master = master
        self.widget1 = tk.Frame(self.master)
        self.widget1.pack()
        self.game = tk.Label(self.widget1, text = 'Análise da imagem:')
        self.game["font"] = ("Verdana", "20", "bold")
        self.game.config(anchor=tk.CENTER)
        self.game.pack()

if __name__ == "__main__":

    ask_file = tk.Tk()
    ask_file.geometry("900x120")
    app_1 = Application1(ask_file)
    ask_file.mainloop()

    print(app_1.data)