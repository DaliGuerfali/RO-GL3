from pathlib import Path
import tkinter as tk
import subprocess

class MainApplication:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("OR Dashboard")
        self.window.geometry("1200x720")
        self.window.configure(bg="#f0f0f0")
        self.window.resizable(False, False)

        # Sidebar for navigation
        self.sidebar = tk.Frame(self.window, bg="#333333", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        buttons = [
            ("Home", self.show_home),
            ("Knapsack", self.show_knapsack),
            ("VRP", self.show_vrp),
            ("Prod Plan", self.show_prodplan),
            ("About", self.show_about)
        ]
        for idx, (text, cmd) in enumerate(buttons):
            btn = tk.Button(self.sidebar, text=text, fg="#ffffff", bg="#555555",
                            activebackground="#777777", font=("Arial",14), command=cmd)
            btn.pack(fill=tk.X, pady=5, padx=10)

        # Container for frames
        self.container = tk.Frame(self.window, bg="#f0f0f0")
        self.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Setup frames
        self.frames = {}
        for F in (HomeFrame, KnapsackFrame, VRPFrame, ProdPlanFrame, AboutFrame):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_home()

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def show_home(self): self.show_frame('HomeFrame')
    def show_knapsack(self):
        self.show_frame('KnapsackFrame')
        subprocess.Popen(["python", str(Path(__file__).parent.parent.parent / "Problems" / "Problem Sac A Dos" / "sacados.py")])
    def show_vrp(self):
        self.show_frame('VRPFrame')
        subprocess.Popen(["python", str(Path(__file__).parent.parent.parent / "Problems" / "VRP" / "vrp.py")])
    def show_prodplan(self):
        self.show_frame('ProdPlanFrame')
        subprocess.Popen(["python", str(Path(__file__).parent.parent.parent / "Problems" / "Production_Planning" / "pp.py")])
    def show_about(self): self.show_frame('AboutFrame')

    def run(self):
        self.window.mainloop()

class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        tk.Label(self, text="Operations Research Project", font=("Arial",24), bg=self["bg"]).pack(pady=40)
        tk.Label(self, text="Select a problem from the sidebar", font=("Arial",16), bg=self["bg"]).pack(pady=20)

class KnapsackFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        tk.Label(self, text="Knapsack Problem", font=("Arial",20), bg=self["bg"]).pack(pady=(30,10))
        # Description
        desc_ks = (
            "The knapsack problem involves selecting items with given values and weights (\n"
            "and optional volumes) to maximize total value while respecting capacity constraints.\n"
            "This solver uses Gurobi to optimize a 0-1 or continuous formulation and supports\n"
            "custom constraints entered via the UI."
        )
        tk.Label(self, text=desc_ks, font=("Arial",12), bg=self["bg"], justify=tk.LEFT, wraplength=800).pack(pady=10, padx=20)
        tk.Button(self, text="Back to Home", command=controller.show_home).pack(pady=20)

class VRPFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        tk.Label(self, text="Vehicle Routing Problem", font=("Arial",20), bg=self["bg"]).pack(pady=(30,10))
        # Description
        desc_vrp = (
            "The vehicle routing problem assigns multiple vehicles to visit a set of\n"
            "locations with minimal total travel distance. Constraints can include maximum\n"
            "route lengths and forbidden routes. Gurobi solves a binary optimization model,\n"
            "and the app displays computed routes and plots them on a map-like graph."
        )
        tk.Label(self, text=desc_vrp, font=("Arial",12), bg=self["bg"], justify=tk.LEFT, wraplength=800).pack(pady=10, padx=20)
        tk.Button(self, text="Back to Home", command=controller.show_home).pack(pady=20)

class ProdPlanFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        tk.Label(self, text="Production Planning", font=("Arial",20), bg=self["bg"]).pack(pady=(30,10))
        # Description
        desc_pp = (
            "The production planning problem determines the optimal production and\n"
            "inventory levels over multiple periods to meet forecasted demand at minimal\n"
            "production and holding costs. The LP model is solved with Gurobi, and results\n"
            "are plotted to show production vs. inventory trends."
        )
        tk.Label(self, text=desc_pp, font=("Arial",12), bg=self["bg"], justify=tk.LEFT, wraplength=800).pack(pady=10, padx=20)
        tk.Button(self, text="Back to Home", command=controller.show_home).pack(pady=20)

class AboutFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        text = ("Operation Research Dashboard\n"
                "Built on Tkinter\n"
                "2025")
        tk.Label(self, text=text, font=("Arial",16), bg=self["bg"], justify=tk.LEFT).pack(pady=40)
        tk.Button(self, text="Back to Home", command=controller.show_home).pack(pady=20)

if __name__ == "__main__":
    app = MainApplication()
    app.run()