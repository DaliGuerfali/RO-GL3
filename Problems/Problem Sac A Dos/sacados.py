import customtkinter as ctk
from tkinter import messagebox, filedialog
from gurobipy import Model, GRB
import json
from pathlib import Path

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernKnapsackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KnapSack_ZELLO")
        self.root.geometry("700x700")  # Increased width for better centering
        
        # Configure grid weight for centering
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Data storage
        self.names = []
        self.values = []
        self.weights = []
        self.volumes = []
        self.constraints = []
        self.capacity1 = ctk.DoubleVar(value=50.0)
        self.capacity2 = ctk.DoubleVar(value=30.0)
        self.num_objects = ctk.IntVar(value=5)
        self.num_capacities = ctk.IntVar(value=1)
        self.resolution_type = ctk.StringVar(value="Binaire")
        
        # Create main container frame
        self.container = ctk.CTkFrame(self.root)
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)  # Center contents horizontally
        
        # Create scrollable frame for all content
        self.main_frame = ctk.CTkScrollableFrame(self.container, width=800, height=750)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)  # Center contents horizontally
        
        self.create_widgets()
        
    def create_widgets(self):
        # Problem configuration section
        config_frame = ctk.CTkFrame(self.main_frame)
        config_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        config_frame.grid_columnconfigure((0, 1, 2), weight=1)  # Equal column weights for centering
        
        # Number of items - centered
        items_frame = ctk.CTkFrame(config_frame)
        items_frame.grid(row=0, column=0, columnspan=3, pady=10)
        items_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(items_frame, text="Number of items:", font=("Roboto", 12)).grid(row=0, column=0, padx=10)
        ctk.CTkEntry(items_frame, textvariable=self.num_objects, width=100).grid(row=0, column=1, padx=10)
        ctk.CTkButton(items_frame, text="Generate", command=self.generate_inputs, 
                     width=100).grid(row=0, column=2, padx=10)
        
        # Capacity selection - centered
        cap_select_frame = ctk.CTkFrame(config_frame)
        cap_select_frame.grid(row=1, column=0, columnspan=3, pady=10)
        cap_select_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(cap_select_frame, text="Number of capacities:", 
                    font=("Roboto", 12)).grid(row=0, column=0, padx=10)
        ctk.CTkRadioButton(cap_select_frame, text="1", variable=self.num_capacities, value=1, 
                          command=self.update_capacities).grid(row=0, column=1, padx=10)
        ctk.CTkRadioButton(cap_select_frame, text="2", variable=self.num_capacities, value=2, 
                          command=self.update_capacities).grid(row=0, column=2, padx=10)
        
        # Capacities frame - centered
        self.capacities_frame = ctk.CTkFrame(self.main_frame)
        self.capacities_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.capacities_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Capacity entries - centered
        cap1_frame = ctk.CTkFrame(self.capacities_frame)
        cap1_frame.grid(row=0, column=0, columnspan=2, pady=10)
        ctk.CTkLabel(cap1_frame, text="Capacity 1 (Weight):", 
                    font=("Roboto", 12)).grid(row=0, column=0, padx=10)
        ctk.CTkEntry(cap1_frame, textvariable=self.capacity1, 
                    width=100).grid(row=0, column=1, padx=10)
        
        # Capacity 2 widgets
        self.capacity2_widgets = []
        cap2_frame = ctk.CTkFrame(self.capacities_frame)
        cap2_frame.grid(row=1, column=0, columnspan=2, pady=10)
        cap2_label = ctk.CTkLabel(cap2_frame, text="Capacity 2 (Volume):", 
                                 font=("Roboto", 12))
        cap2_entry = ctk.CTkEntry(cap2_frame, textvariable=self.capacity2, 
                                 width=100)
        self.capacity2_widgets.extend([cap2_frame, cap2_label, cap2_entry])
        
        # Resolution type - centered
        type_frame = ctk.CTkFrame(self.main_frame)
        type_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        type_frame.grid_columnconfigure((0, 1), weight=1)
        
        resolution_container = ctk.CTkFrame(type_frame)
        resolution_container.grid(row=0, column=0, columnspan=2, pady=10)
        ctk.CTkRadioButton(resolution_container, text="Binary", variable=self.resolution_type, 
                          value="Binaire").grid(row=0, column=0, padx=20)
        ctk.CTkRadioButton(resolution_container, text="Continuous", variable=self.resolution_type, 
                          value="Continue").grid(row=0, column=1, padx=20)
        
        # Items frame - centered
        self.inputs_frame = ctk.CTkFrame(self.main_frame)
        self.inputs_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        self.inputs_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Buttons frame - centered
        buttons_frame = ctk.CTkFrame(self.main_frame)
        buttons_frame.grid(row=4, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create buttons with consistent styling
        button_style = {"width": 120, "height": 32, "corner_radius": 8, "font": ("Roboto", 12)}
        
        button_container = ctk.CTkFrame(buttons_frame)
        button_container.grid(row=0, column=0, columnspan=4, pady=10)
        
        ctk.CTkButton(button_container, text="Add Constraint", command=self.add_constraint,
                     **button_style).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_container, text="Save Config", command=self.save_config,
                     **button_style).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_container, text="Load Config", command=self.load_config,
                     **button_style).grid(row=0, column=2, padx=10)
        ctk.CTkButton(button_container, text="Solve", command=self.solve,
                     **button_style).grid(row=0, column=3, padx=10)
        
        self.update_capacities()

    def generate_inputs(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
            
        self.names = [ctk.StringVar(value=f"Item {i+1}") for i in range(self.num_objects.get())]
        self.values = [ctk.DoubleVar(value=10.0) for _ in range(self.num_objects.get())]
        self.weights = [ctk.DoubleVar(value=5.0) for _ in range(self.num_objects.get())]
        self.volumes = [ctk.DoubleVar(value=3.0) for _ in range(self.num_objects.get())]
        
        # Center the input fields
        input_container = ctk.CTkFrame(self.inputs_frame)
        input_container.grid(row=0, column=0, columnspan=4, padx=20, pady=10)
        
        # Headers with modern styling
        header_style = {"font": ("Roboto", 12, "bold")}
        ctk.CTkLabel(input_container, text="Name", **header_style).grid(row=0, column=0, padx=10, pady=(10, 5))
        ctk.CTkLabel(input_container, text="Value", **header_style).grid(row=0, column=1, padx=10, pady=(10, 5))
        ctk.CTkLabel(input_container, text="Weight", **header_style).grid(row=0, column=2, padx=10, pady=(10, 5))
        if self.num_capacities.get() == 2:
            ctk.CTkLabel(input_container, text="Volume", **header_style).grid(row=0, column=3, padx=10, pady=(10, 5))
        
        # Input fields with consistent styling
        entry_style = {"width": 120, "height": 28, "corner_radius": 6}
        for i in range(self.num_objects.get()):
            ctk.CTkEntry(input_container, textvariable=self.names[i], **entry_style).grid(
                row=i+1, column=0, padx=10, pady=5)
            ctk.CTkEntry(input_container, textvariable=self.values[i], **entry_style).grid(
                row=i+1, column=1, padx=10, pady=5)
            ctk.CTkEntry(input_container, textvariable=self.weights[i], **entry_style).grid(
                row=i+1, column=2, padx=10, pady=5)
            if self.num_capacities.get() == 2:
                ctk.CTkEntry(input_container, textvariable=self.volumes[i], **entry_style).grid(
                    row=i+1, column=3, padx=10, pady=5)

    def update_capacities(self):
        if self.num_capacities.get() == 2:
            self.capacity2_widgets[0].grid(row=1, column=0, columnspan=2, pady=10)
            self.capacity2_widgets[1].grid(row=0, column=0, padx=10)
            self.capacity2_widgets[2].grid(row=0, column=1, padx=10)
        else:
            for widget in self.capacity2_widgets:
                widget.grid_remove()
        self.generate_inputs()

    def add_constraint(self):
        constraint_window = ctk.CTkToplevel(self.root)
        constraint_window.title("Add Constraint")
        constraint_window.geometry("400x200")
        
        ctk.CTkLabel(constraint_window, text="Enter constraint (e.g., x[0] + x[1] <= 1):",
                    font=("Roboto", 12)).pack(pady=20)
        constraint_entry = ctk.CTkEntry(constraint_window, width=300, height=35)
        constraint_entry.pack(pady=10)
        
        def save_constraint():
            try:
                constraint_str = constraint_entry.get()
                constraint = eval(f"lambda x: {constraint_str}")
                self.constraints.append(constraint)
                messagebox.showinfo("Success", "Constraint added successfully!")
                constraint_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid constraint: {str(e)}")
        
        ctk.CTkButton(constraint_window, text="Add", command=save_constraint,
                     width=120, height=32).pack(pady=20)

    def solve_knapsack(self, names, values, weights, volumes, capacities, constraints, resolution_type):
        """Solve the knapsack problem using Gurobi"""
        try:
            model = Model("Dynamic Knapsack")
            n = len(values)
            
            if resolution_type == "Binaire":
                x = model.addVars(n, vtype=GRB.BINARY, name="x")
            else:
                x = model.addVars(n, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name="x")
            
            model.setObjective(sum(values[i] * x[i] for i in range(n)), GRB.MAXIMIZE)
            
            model.addConstr(sum(weights[i] * x[i] for i in range(n)) <= capacities["Weight"][1], "weight_capacity")
            if "Volume" in capacities:
                model.addConstr(sum(volumes[i] * x[i] for i in range(n)) <= capacities["Volume"][1], "volume_capacity")
            
            for i, constraint in enumerate(constraints):
                try:
                    model.addConstr(constraint(x), name=f"custom_constraint_{i}")
                except Exception as e:
                    messagebox.showerror("Constraint Error", f"Error in constraint {i+1}: {str(e)}")
                    return None, None
            
            model.optimize()
            
            if model.status == GRB.OPTIMAL:
                solution = {names[i]: x[i].X for i in range(n)}
                return solution, model.objVal
            else:
                return None, None
                
        except Exception as e:
            messagebox.showerror("Solver Error", f"Error solving problem: {str(e)}")
            return None, None

    def save_config(self):
        config = {
            'num_objects': self.num_objects.get(),
            'num_capacities': self.num_capacities.get(),
            'capacity1': self.capacity1.get(),
            'capacity2': self.capacity2.get(),
            'resolution_type': self.resolution_type.get(),
            'items': [{
                'name': n.get(),
                'value': v.get(),
                'weight': w.get(),
                'volume': vol.get()
            } for n, v, w, vol in zip(self.names, self.values, self.weights, self.volumes)]
        }
        
        filename = filedialog.asksaveasfilename(initialdir=str(Path(__file__).parent / 'SACexemples'),
                                              defaultextension=".json",
                                              filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Saved", "Configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def load_config(self):
        examples_dir = Path(__file__).parent / 'SACexemples'
        filename = filedialog.askopenfilename(initialdir=str(examples_dir), filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        try:
            raw = Path(filename).read_bytes()
            try:
                content = raw.decode('utf-8-sig')
            except:
                content = raw.decode('latin-1')
            config = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            return
        self.num_objects.set(config.get('num_objects', self.num_objects.get()))
        self.num_capacities.set(config.get('num_capacities', self.num_capacities.get()))
        self.capacity1.set(config.get('capacity1', self.capacity1.get()))
        self.capacity2.set(config.get('capacity2', self.capacity2.get()))
        self.resolution_type.set(config.get('resolution_type', self.resolution_type.get()))
        self.update_capacities()
        for i, item in enumerate(config.get('items', [])):
            if i < len(self.names):
                self.names[i].set(item.get('name', self.names[i].get()))
                self.values[i].set(item.get('value', self.values[i].get()))
                self.weights[i].set(item.get('weight', self.weights[i].get()))
                self.volumes[i].set(item.get('volume', self.volumes[i].get()))

    def solve(self):
        try:
            names = [n.get() for n in self.names]
            values = [v.get() for v in self.values]
            weights = [w.get() for w in self.weights]
            volumes = [v.get() for v in self.volumes]
            
            capacities = {"Weight": (weights, self.capacity1.get())}
            if self.num_capacities.get() == 2:
                capacities["Volume"] = (volumes, self.capacity2.get())
            
            solution, optimal_value = self.solve_knapsack(names, values, weights, volumes, 
                                                        capacities, self.constraints, 
                                                        self.resolution_type.get())
            
            if solution:
                result_window = ctk.CTkToplevel(self.root)
                result_window.title("Solution")
                result_window.geometry("400x400")
                # Create a scrollable text display for results
                result_frame = ctk.CTkScrollableFrame(result_window, width=350, height=350)
                result_frame.pack(padx=20, pady=20, fill="both", expand=True)
                
                # Add the results with nice formatting
                ctk.CTkLabel(result_frame, 
                           text=f"Optimal Value: {optimal_value:.2f}",
                           font=("Roboto", 14, "bold")).pack(pady=(0, 10))
                
                ctk.CTkLabel(result_frame, 
                           text="Selected Items:",
                           font=("Roboto", 12, "bold")).pack(pady=(10, 5))
                
                for name, value in solution.items():
                    if value > 0.001:
                        item_frame = ctk.CTkFrame(result_frame)
                        item_frame.pack(fill="x", padx=10, pady=2)
                        ctk.CTkLabel(item_frame, 
                                   text=f"{name}: {value:.3f}",
                                   font=("Roboto", 12)).pack(pady=5)
                
                # Add a close button
                ctk.CTkButton(result_window, 
                            text="Close",
                            command=result_window.destroy,
                            width=100,
                            height=32).pack(pady=10)
            else:
                messagebox.showwarning("No Solution", "No optimal solution found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error solving problem: {str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ModernKnapsackApp(root)
    root.mainloop()