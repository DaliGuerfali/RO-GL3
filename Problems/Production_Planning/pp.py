import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from gurobipy import Model, GRB
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
from tkinter import filedialog
from pathlib import Path

# Dark mode with green accent
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ProductionPlanningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Production Planning")
        self.root.geometry("600x600")

        self.container = ctk.CTkScrollableFrame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.container, text="Production Planning Problem", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        # Period selection
        frame_period = ctk.CTkFrame(self.container)
        frame_period.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(frame_period, text="Periods:").pack(side=tk.LEFT, padx=5)
        self.periods_var = tk.IntVar(value=4)
        self.period_menu = ctk.CTkOptionMenu(
            frame_period,
            values=[str(i) for i in range(2, 13)],
            variable=self.periods_var,
            command=self.update_inputs
        )
        self.period_menu.pack(side=tk.LEFT, padx=5)

        # Cost inputs
        frame_cost = ctk.CTkFrame(self.container)
        frame_cost.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(frame_cost, text="Prod Cost/unit:").pack(side=tk.LEFT, padx=5)
        self.prod_cost_var = tk.DoubleVar(value=1.0)
        ctk.CTkEntry(frame_cost, textvariable=self.prod_cost_var, width=80).pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(frame_cost, text="Inv Cost/unit:").pack(side=tk.LEFT, padx=5)
        self.inv_cost_var = tk.DoubleVar(value=0.5)
        ctk.CTkEntry(frame_cost, textvariable=self.inv_cost_var, width=80).pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(frame_cost, text="Initial Inv:").pack(side=tk.LEFT, padx=5)
        self.init_inv_var = tk.DoubleVar(value=0.0)
        ctk.CTkEntry(frame_cost, textvariable=self.init_inv_var, width=80).pack(side=tk.LEFT, padx=5)

        # Dynamic demand inputs
        self.input_frame = ctk.CTkFrame(self.container)
        self.input_frame.pack(fill=tk.X, pady=10)

        # Config buttons (Save/Load)
        btn_frame = ctk.CTkFrame(self.container)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Load Config", command=self.load_config, width=140).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_frame, text="Save Config", command=self.save_config, width=140).pack(side=tk.LEFT, padx=10)

        # Solve button
        self.solve_btn = ctk.CTkButton(
            self.container,
            text="Solve",
            command=self.solve,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.solve_btn.pack(pady=10)

        self.outputs_frame = ctk.CTkFrame(self.container)
        self.outputs_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.update_inputs()

    def update_inputs(self, _=None):
        # clear old entries
        for w in self.input_frame.winfo_children():
            w.destroy()
        # headers
        header = ctk.CTkLabel(self.input_frame, text="Period    Demand", font=ctk.CTkFont(size=14))
        header.pack(anchor="w", padx=10)
        # demand entries
        self.demand_vars = []
        for t in range(1, self.periods_var.get() + 1):
            row = ctk.CTkFrame(self.input_frame)
            row.pack(fill=tk.X, pady=2)
            ctk.CTkLabel(row, text=f"Period {t}:").pack(side=tk.LEFT, padx=5)
            var = tk.DoubleVar(value=10.0)
            entry = ctk.CTkEntry(row, textvariable=var, width=100)
            entry.pack(side=tk.LEFT, padx=5)
            self.demand_vars.append(var)

    def solve(self):
        try:
            T = self.periods_var.get()
            demands = [var.get() for var in self.demand_vars]
            prod_cost = self.prod_cost_var.get()
            inv_cost = self.inv_cost_var.get()
            init_inv = self.init_inv_var.get()

            # create model
            model = Model("ProductionPlanning")
            x = model.addVars(T, lb=0, vtype=GRB.CONTINUOUS, name="prod")
            I = model.addVars(T, lb=0, vtype=GRB.CONTINUOUS, name="inv")

            # inventory balance
            for t in range(T):
                if t == 0:
                    model.addConstr(I[t] == init_inv + x[t] - demands[t])
                else:
                    model.addConstr(I[t] == I[t-1] + x[t] - demands[t])

            # objective: minimize production + inventory costs
            obj = prod_cost * x.sum() + inv_cost * I.sum()
            model.setObjective(obj, GRB.MINIMIZE)

            model.optimize()

            if model.status in (GRB.OPTIMAL, GRB.TIME_LIMIT):
                prod = [x[t].X for t in range(T)]
                inv = [I[t].X for t in range(T)]
                cost = model.objVal

                # display text
                for w in self.outputs_frame.winfo_children(): w.destroy()
                text = f"Total Cost: {cost:.2f}\n"
                for t in range(T):
                    text += f"P{t+1}: Prod={prod[t]:.2f}, Inv={inv[t]:.2f}\n"
                label = ctk.CTkTextbox(self.outputs_frame, width=560, height=150)
                label.insert("0.0", text)
                label.configure(state="disabled")
                label.pack(padx=10, pady=5)

                # plot
                fig, ax = plt.subplots(figsize=(5,3))
                ax.plot(range(1, T+1), prod, marker='o', label='Production')
                ax.plot(range(1, T+1), inv, marker='x', label='Inventory')
                ax.set_xlabel('Period')
                ax.set_ylabel('Quantity')
                ax.set_title('Production and Inventory Levels')
                ax.legend()
                canvas = FigureCanvasTkAgg(fig, master=self.outputs_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(padx=10, pady=5)

            else:
                messagebox.showerror("Error", "No optimal solution found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_config(self):
        config = {
            'periods': self.periods_var.get(),
            'prod_cost': self.prod_cost_var.get(),
            'inv_cost': self.inv_cost_var.get(),
            'init_inv': self.init_inv_var.get(),
            'demands': [v.get() for v in self.demand_vars]
        }
        fn = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json')])
        if not fn:
            return
        try:
            with open(fn, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo('Saved', 'Configuration saved successfully.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save configuration:\n{e}')

    def load_config(self):
        examples_dir = Path(__file__).parent / 'PPexemples'
        fn = filedialog.askopenfilename(initialdir=str(examples_dir.resolve()), filetypes=[('JSON files','*.json')])
        if not fn:
            return
        try:
            raw = Path(fn).read_bytes()
            # decode JSON robustly
            try:
                content = raw.decode('utf-8-sig')
            except:
                try:
                    content = raw.decode('utf-8')
                except:
                    content = raw.decode('latin-1')
            cfg = json.loads(content)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to parse configuration:\n{e}')
            return
        # populate fields
        self.periods_var.set(cfg.get('periods', self.periods_var.get()))
        self.prod_cost_var.set(cfg.get('prod_cost', self.prod_cost_var.get()))
        self.inv_cost_var.set(cfg.get('inv_cost', self.inv_cost_var.get()))
        self.init_inv_var.set(cfg.get('init_inv', self.init_inv_var.get()))
        self.update_inputs()
        demands = cfg.get('demands', [])
        for i, val in enumerate(demands):
            if i < len(self.demand_vars):
                self.demand_vars[i].set(val)
        messagebox.showinfo('Loaded', 'Configuration loaded successfully!')

if __name__ == "__main__":
    root = ctk.CTk()
    app = ProductionPlanningApp(root)
    root.mainloop()