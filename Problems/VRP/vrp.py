import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from gurobipy import GRB, Model, quicksum
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.spatial.distance import euclidean
import json
from pathlib import Path

# Dark mode with green accent
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ModernVRPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VRP Route Optimizer")
        self.root.geometry("800x800")
        self.root.configure(bg="#23272f")

        # Header
        header = ctk.CTkFrame(self.root, fg_color="#181c22")
        header.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(header, text="Vehicle Routing Problem", font=ctk.CTkFont(size=26, weight="bold"), text_color="#00e676").pack(pady=18)

        # Main container
        self.main_container = ctk.CTkScrollableFrame(self.root, fg_color="#2c313c")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        ctk.CTkLabel(self.main_container, text="VRP Route Optimizer", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00e676").pack(pady=10)
        desc_vrp = (
            "The vehicle routing problem assigns multiple vehicles to visit a set of\n"
            "locations with minimal total travel distance. Constraints can include maximum\n"
            "route lengths and forbidden routes. Gurobi solves a binary optimization model,\n"
            "and the app displays computed routes and plots them on a map-like graph."
        )
        ctk.CTkLabel(self.main_container, text=desc_vrp, font=ctk.CTkFont(size=14), text_color="#ffffff", justify=tk.LEFT, wraplength=600).pack(pady=10, padx=20)

        # Number of locations
        self.cities_frame = ctk.CTkFrame(self.main_container)
        self.cities_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(self.cities_frame, text="Locations:").pack(side=tk.LEFT, padx=10)
        self.num_locations = tk.IntVar(value=5)
        self.loc_menu = ctk.CTkOptionMenu(self.cities_frame, values=[str(i) for i in range(3, 21)], variable=self.num_locations, command=self.update_inputs)
        self.loc_menu.pack(side=tk.LEFT, padx=10)

        # Inputs
        self.input_frame = ctk.CTkFrame(self.main_container)
        self.input_frame.pack(fill=tk.X, pady=10)
        self.vehicle_frame = ctk.CTkFrame(self.main_container)
        self.vehicle_frame.pack(fill=tk.X, pady=10)

        # Vehicle count
        ctk.CTkLabel(self.vehicle_frame, text="Vehicles:").pack(side=tk.LEFT, padx=10)
        self.num_vehicles = tk.IntVar(value=2)
        self.veh_menu = ctk.CTkOptionMenu(self.vehicle_frame, values=[str(i) for i in range(1, 11)], variable=self.num_vehicles)
        self.veh_menu.pack(side=tk.LEFT, padx=10)

        # Constraint inputs
        self.max_dist_var = tk.DoubleVar(value=0)
        self.restrict_var = tk.StringVar(value="")
        ctk.CTkLabel(self.main_container, text="Max Route Length (0=none):").pack(pady=5)
        self.dist_entry = ctk.CTkEntry(self.main_container, textvariable=self.max_dist_var)
        self.dist_entry.pack(pady=5)
        ctk.CTkLabel(self.main_container, text="Forbidden routes (e.g. 1-2,3-4):").pack(pady=5)
        self.rest_entry = ctk.CTkEntry(self.main_container, textvariable=self.restrict_var)
        self.rest_entry.pack(pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_container)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Load Config", command=self.load_config, width=140).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_frame, text="Save Config", command=self.save_config, width=140).pack(side=tk.LEFT, padx=10)

        self.solve_btn = ctk.CTkButton(self.main_container, text="Solve VRP", command=self.solve_vrp, width=200, font=ctk.CTkFont(size=16, weight="bold"))
        self.solve_btn.pack(pady=20)

        # dynamic input trackers
        self.coord_inputs = []
        self.name_inputs = []
        self.update_inputs()

    def update_inputs(self, _=None):
        for w in self.input_frame.winfo_children(): w.destroy()
        self.coord_inputs.clear(); self.name_inputs.clear()
        for i in range(self.num_locations.get()):
            row = ctk.CTkFrame(self.input_frame); row.pack(fill=tk.X, pady=3)
            ctk.CTkLabel(row, text=f"Loc {i+1}:").pack(side=tk.LEFT, padx=5)
            nm = ctk.CTkEntry(row, width=100); nm.pack(side=tk.LEFT, padx=5)
            self.name_inputs.append(nm)
            x=ctk.CTkEntry(row, width=60); y=ctk.CTkEntry(row, width=60)
            x.pack(side=tk.LEFT, padx=2); y.pack(side=tk.LEFT, padx=2)
            self.coord_inputs.append((x,y))

    def save_config(self):
        cfg = {'locations': [], 'vehicles': self.num_vehicles.get(), 'max_dist': self.max_dist_var.get(), 'forbidden': self.restrict_var.get()}
        for nm,(x,y) in zip(self.name_inputs, self.coord_inputs):
            cfg['locations'].append({'name':nm.get(), 'x':float(x.get() or 0), 'y':float(y.get() or 0)})
        fn = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json')])
        if not fn:
            return
        try:
            with open(fn, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=4)
            messagebox.showinfo('Saved', 'Configuration saved successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save configuration:\n{e}')

    def load_config(self):
        # Open in VRP examples directory
        examples_dir = Path(__file__).parent / 'VRPexemples'
        fn = filedialog.askopenfilename(initialdir=str(examples_dir.resolve()), filetypes=[('JSON files','*.json')])
        if not fn:
            return
        try:
            # Load raw bytes and detect encoding
            raw = Path(fn).read_bytes()
            # Check for UTF-16 BOM
            if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
                content = raw.decode('utf-16')
            else:
                try:
                    content = raw.decode('utf-8-sig')
                except Exception:
                    try:
                        content = raw.decode('utf-8')
                    except Exception:
                        content = raw.decode('latin-1')
            if not content.strip():
                raise ValueError('Configuration file is empty')
            cfg = json.loads(content)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to parse JSON configuration:\n{e}')
            return
        self.num_locations.set(len(cfg.get('locations',[])))
        self.num_vehicles.set(cfg.get('vehicles',1))
        self.max_dist_var.set(cfg.get('max_dist',0))
        self.restrict_var.set(cfg.get('forbidden',''))
        self.update_inputs()
        for i,loc in enumerate(cfg.get('locations',[])):
            if i<len(self.coord_inputs): self.name_inputs[i].insert(0,loc.get('name',''))
            xi,yi=self.coord_inputs[i]; xi.insert(0,str(loc.get('x',0))); yi.insert(0,str(loc.get('y',0)))
        messagebox.showinfo('Loaded', 'Configuration loaded successfully!')

    def solve_vrp(self):
        # collecter les coordonnées et noms
        coords, names = [], []
        for nm, (x, y) in zip(self.name_inputs, self.coord_inputs):
            try:
                coords.append((float(x.get()), float(y.get())))
                names.append(nm.get() or f"Loc{len(coords)}")
            except ValueError:
                messagebox.showerror('Input Error', 'Coordinates must be numbers')
                return
        n, m = len(coords), self.num_vehicles.get()
        # compute distances
        dist = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                dist[i, j] = euclidean(coords[i], coords[j]) if i != j else 0
        # disable solve button
        self.solve_btn.configure(state='disabled', text='Solving...')
        self.root.update()
        try:
            # construction du modèle Gurobi pour le VRP
            model = Model('VRP')
            model.setParam('TimeLimit', 60)  # limite de temps
            model.setParam('MIPGap', 0.05)   # tolérance d'optimalité

            # variable binaire x[i,j,k] = 1 si le véhicule k va de i à j
            x = model.addVars(n, n, m, vtype=GRB.BINARY, name='x')
            # variable continue t[i,k] pour l'ordre de visite (MTZ)
            t = model.addVars(n, m, vtype=GRB.CONTINUOUS, name='t')

            # objectif : minimiser la distance totale parcourue
            model.setObjective(
                quicksum(dist[i, j] * x[i, j, k]
                         for i in range(n) for j in range(n) for k in range(m) if i != j),
                GRB.MINIMIZE
            )

            # chaque client (j≠0) doit être visité exactement une fois par une des m voitures
            for j in range(1, n):
                model.addConstr(
                    quicksum(x[i, j, k] for i in range(n) for k in range(m) if i != j) == 1,
                    name=f"visit_once_{j}"
                )

            # chaque véhicule k part du dépôt (0) et y revient
            for k in range(m):
                model.addConstr(quicksum(x[0, j, k] for j in range(1, n)) == 1, name=f"depart_{k}")
                model.addConstr(quicksum(x[i, 0, k] for i in range(1, n)) == 1, name=f"retour_{k}")

            # élimination des sous-tours (MTZ) : si k va i->j, alors t[j,k] >= t[i,k] + 1
            M = n  # grosse constante
            for k in range(m):
                model.addConstr(t[0, k] == 0, name=f"time_depot_{k}")
                for i in range(n):
                    for j in range(1, n):
                        if i != j:
                            model.addConstr(
                                t[j, k] >= t[i, k] + 1 - M * (1 - x[i, j, k]),
                                name=f"mtz_{i}_{j}_{k}"
                            )

            # conservation de flux : si une voiture arrive en j, elle doit aussi en repartir
            for k in range(m):
                for j in range(1, n):
                    model.addConstr(
                        quicksum(x[i, j, k] for i in range(n) if i != j) ==
                        quicksum(x[j, i, k] for i in range(n) if i != j),
                        name=f"flow_{j}_{k}"
                    )

            # contraintes utilisateurs : routes interdites
            for route in self.restrict_var.get().split(','):
                if '-' in route:
                    try:
                        a, b = map(int, route.split('-'))
                        for k in range(m):
                            model.addConstr(x[a-1, b-1, k] == 0)
                            model.addConstr(x[b-1, a-1, k] == 0)
                    except ValueError:
                        pass
            # contrainte de distance maximale par véhicule
            md = self.max_dist_var.get()
            if md > 0:
                for k in range(m):
                    model.addConstr(
                        quicksum(dist[i, j] * x[i, j, k]
                                 for i in range(n) for j in range(n) if i != j) <= md,
                        name=f"maxdist_{k}"
                    )

            # résolution
            model.optimize()
            if model.status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
                messagebox.showerror('Error', 'No feasible solution found')
                return
            sol = model.getAttr('x', x)
            routes = []
            for k in range(m):
                path, cur = [0], 0
                while True:
                    nxt = next((j for j in range(n) if j != cur and sol[cur, j, k] > 0.5), None)
                    if nxt is None or nxt == 0:
                        path.append(0)
                        break
                    path.append(nxt)
                    cur = nxt
                if len(path) > 2:
                    routes.append(path)
            self.display_vrp_result(coords, routes, routes)
            self.show_vrp_graph(coords, routes)
        finally:
            self.solve_btn.configure(state='normal', text='Solve VRP')

    def display_vrp_result(self, coords, routes, combined):
        w=ctk.CTkToplevel(self.root); w.title('VRP Result'); w.geometry('400x300')
        txt=ctk.CTkTextbox(w, width=380, height=280); txt.pack(padx=10,pady=10)
        text='Routes:\n'
        for i,r in enumerate(routes,1): text+=f'Vehicle {i}: '+'-'.join(str(x) for x in r)+'\n'
        txt.insert('1.0', text)
        txt.configure(state='disabled')

    def show_vrp_graph(self, coords, routes):
        w=ctk.CTkToplevel(self.root); w.title('VRP Graph'); w.geometry('600x600')
        plt.style.use('dark_background')
        fig,ax=plt.subplots(figsize=(6,6))
        colors=plt.cm.tab10(np.linspace(0,1,len(routes)))
        for c,r in zip(colors,routes):
            pts=[coords[i] for i in r]
            xs,ys=zip(*pts);
            ax.plot(xs,ys,color=c,marker='o')
        ax.set_facecolor('#2b2b2b'); ax.grid(True, color='gray', linestyle='--', alpha=0.5)
        canvas=FigureCanvasTkAgg(fig, master=w); canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__=='__main__':
    root=ctk.CTk(); ModernVRPApp(root); root.mainloop()
