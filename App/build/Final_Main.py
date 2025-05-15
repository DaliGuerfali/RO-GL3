from pathlib import Path
import tkinter as tk
import subprocess

class MainApplication:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("OR Dashboard")
        self.window.geometry("1200x720")
        self.window.configure(bg="#23272f")
        self.window.resizable(False, False)

        # Sidebar for navigation (modern look)
        self.sidebar = tk.Frame(self.window, bg="#181c22", width=220, relief=tk.RAISED, bd=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        logo = tk.Label(self.sidebar, text="OR DASHBOARD", fg="#00e676", bg="#181c22", font=("Segoe UI", 20, "bold"), pady=30)
        logo.pack()
        buttons = [
            ("Home", self.show_home),
            ("VRP", self.show_vrp),
            ("Prod Plan", self.show_prodplan),
            ("About", self.show_about)
        ]
        for idx, (text, cmd) in enumerate(buttons):
            btn = tk.Button(
                self.sidebar, text=text, fg="#ffffff", bg="#23272f", activebackground="#00e676", activeforeground="#23272f",
                font=("Segoe UI", 15, "bold"), command=cmd, bd=0, relief=tk.FLAT, cursor="hand2", pady=12
            )
            btn.pack(fill=tk.X, pady=(0, 10), padx=30)

        # Container for frames (rounded corners effect)
        self.container = tk.Frame(self.window, bg="#2c313c", bd=0, highlightthickness=0)
        self.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Setup frames
        self.frames = {}
        for F in (HomeFrame, VRPFrame, ProdPlanFrame, AboutFrame):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_home()

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def show_home(self): self.show_frame('HomeFrame')
    def show_knapsack(self):
        pass
    def show_vrp(self):
        self.show_frame('VRPFrame')
        # subprocess.Popen is now only called from the button in VRPFrame

    def show_prodplan(self):
        self.show_frame('ProdPlanFrame')
        # subprocess.Popen is now only called from the button in ProdPlanFrame

    def show_about(self): self.show_frame('AboutFrame')

    def run(self):
        self.window.mainloop()

class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2c313c")
        tk.Label(self, text="Operations Research Project", font=("Segoe UI",28,"bold"), bg=self["bg"], fg="#00e676").pack(pady=60)
        tk.Label(self, text="Select a problem to launch:", font=("Segoe UI",16), bg=self["bg"], fg="#ffffff").pack(pady=20)
        btn_frame = tk.Frame(self, bg=self["bg"])
        btn_frame.pack(pady=30)
        tk.Button(
            btn_frame, text="Open VRP", command=controller.show_vrp, bg="#00e676", fg="#23272f", font=("Segoe UI",16,"bold"), bd=0, relief=tk.FLAT, cursor="hand2", width=18, height=2
        ).pack(pady=10)
        tk.Button(
            btn_frame, text="Open Production Planning", command=controller.show_prodplan, bg="#00e676", fg="#23272f", font=("Segoe UI",16,"bold"), bd=0, relief=tk.FLAT, cursor="hand2", width=18, height=2
        ).pack(pady=10)

class VRPFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2c313c")
        tk.Label(self, text="Vehicle Routing Problem", font=("Segoe UI",22,"bold"), bg=self["bg"], fg="#00e676").pack(pady=(40,10))
        desc_vrp = (
            "The vehicle routing problem assigns multiple vehicles to visit a set of\n"
            "locations with minimal total travel distance. Constraints can include maximum\n"
            "route lengths and forbidden routes. Gurobi solves a binary optimization model,\n"
            "and the app displays computed routes and plots them on a map-like graph."
        )
        tk.Label(self, text=desc_vrp, font=("Segoe UI",13), bg=self["bg"], fg="#ffffff", justify=tk.LEFT, wraplength=800).pack(pady=10, padx=30)
        tk.Button(self, text="Start VRP Solver", command=self.launch_vrp, bg="#00e676", fg="#23272f", font=("Segoe UI",14,"bold"), bd=0, relief=tk.FLAT, cursor="hand2", width=20, height=2).pack(pady=30)

    def launch_vrp(self):
        subprocess.Popen(["python", str(Path(__file__).parent.parent.parent / "Problems" / "VRP" / "vrp.py")])

class ProdPlanFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2c313c")
        tk.Label(self, text="Production Planning", font=("Segoe UI",22,"bold"), bg=self["bg"], fg="#00e676").pack(pady=(40,10))
        desc_pp = (
            "The production planning problem determines the optimal production and\n"
            "inventory levels over multiple periods to meet forecasted demand at minimal\n"
            "production and holding costs. The LP model is solved with Gurobi, and results\n"
            "are plotted to show production vs. inventory trends."
        )
        tk.Label(self, text=desc_pp, font=("Segoe UI",13), bg=self["bg"], fg="#ffffff", justify=tk.LEFT, wraplength=800).pack(pady=10, padx=30)
        tk.Button(self, text="Start Production Planning", command=self.launch_prodplan, bg="#00e676", fg="#23272f", font=("Segoe UI",14,"bold"), bd=0, relief=tk.FLAT, cursor="hand2", width=24, height=2).pack(pady=30)

    def launch_prodplan(self):
        subprocess.Popen(["python", str(Path(__file__).parent.parent.parent / "Problems" / "Production_Planning" / "pp.py")])

class AboutFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2c313c")
        text = ("Operation Research Dashboard\n"
                "Built on Tkinter\n"
                "2025")
        tk.Label(self, text=text, font=("Segoe UI",16), bg=self["bg"], fg="#00e676", justify=tk.LEFT).pack(pady=60)
        tk.Button(self, text="Back to Home", command=controller.show_home, bg="#00e676", fg="#23272f", font=("Segoe UI",12,"bold"), bd=0, relief=tk.FLAT, cursor="hand2").pack(pady=30)

if __name__ == "__main__":
    app = MainApplication()
    app.run()