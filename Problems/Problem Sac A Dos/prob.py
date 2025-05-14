import tkinter as tk
from tkinter import ttk, messagebox
from gurobipy import Model, GRB


def solve_knapsack(names, values, weights, volumes, capacities, constraints, resolution_type):
    """
    Résout le problème de sac à dos avec les paramètres donnés.
    """
    modele = Model("Sac à dos dynamique")
    n = len(values)

    # Choix du type de variables
    if resolution_type == "Binaire":
        vtype = GRB.BINARY
    else:
        vtype = GRB.CONTINUOUS

    # Variables de décision
    x = modele.addVars(n, vtype=vtype, name="x")

    # Fonction objectif
    modele.setObjective(sum(values[i] * x[i] for i in range(n)), GRB.MAXIMIZE)

    # Contraintes de capacité
    for cap_type, (attr, limit) in capacities.items():
        modele.addConstr(sum(attr[i] * x[i] for i in range(n)) <= limit, name=f"Cap_{cap_type}")

    # Contraintes supplémentaires
    for constraint in constraints:
        modele.addConstr(constraint(x), name="CustomConstraint")

    # Résolution
    modele.optimize()

    # Récupération des résultats
    if modele.status == GRB.OPTIMAL:
        solution = {names[i]: x[i].x for i in range(n)}
        return solution, modele.objVal
    else:
        return None, None


class KnapsackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Problème de Sac à Dos Dynamique")

        # Variables pour stocker les données
        self.names = []
        self.values = []
        self.weights = []
        self.volumes = []
        self.constraints = []
        self.capacity1 = tk.IntVar(value=50)
        self.capacity2 = tk.IntVar(value=30)
        self.num_objects = tk.IntVar(value=5)
        self.num_capacities = tk.IntVar(value=1)
        self.resolution_type = tk.StringVar(value="Binaire")

        # Interface principale
        self.create_widgets()

    def create_widgets(self):
        """Création des widgets de l'interface."""
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Saisie du nombre d'articles
        ttk.Label(frame, text="Nombre d'articles:").grid(column=0, row=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.num_objects, width=10).grid(column=1, row=0, sticky=tk.W)
        ttk.Button(frame, text="Générer", command=self.generate_inputs).grid(column=2, row=0, sticky=tk.W)

        # Choix du nombre de capacités
        ttk.Label(frame, text="Nombre de capacités:").grid(column=0, row=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="1", variable=self.num_capacities, value=1, command=self.update_capacities).grid(column=1, row=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="2", variable=self.num_capacities, value=2, command=self.update_capacities).grid(column=2, row=1, sticky=tk.W)

        # Capacité 1
        ttk.Label(frame, text="Capacité 1 (poids max):").grid(column=0, row=2, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.capacity1, width=10).grid(column=1, row=2, sticky=tk.W)

        # Capacité 2 (optionnelle)
        self.capacity2_frame = ttk.Frame(frame)
        self.capacity2_frame.grid(column=0, row=3, columnspan=3, sticky=(tk.W, tk.E))
        ttk.Label(self.capacity2_frame, text="Capacité 2 (volume max):").grid(column=0, row=0, sticky=tk.W)
        ttk.Entry(self.capacity2_frame, textvariable=self.capacity2, width=10).grid(column=1, row=0, sticky=tk.W)

        # Option de type de résolution
        ttk.Label(frame, text="Type de résolution:").grid(column=0, row=4, sticky=tk.W)
        ttk.Radiobutton(frame, text="Binaire", variable=self.resolution_type, value="Binaire").grid(column=1, row=4, sticky=tk.W)
        ttk.Radiobutton(frame, text="Continue", variable=self.resolution_type, value="Continue").grid(column=2, row=4, sticky=tk.W)

        # Ajouter une contrainte et résoudre
        ttk.Button(frame, text="Ajouter contrainte", command=self.add_constraint).grid(column=0, row=5, sticky=tk.W)
        ttk.Button(frame, text="Résoudre", command=self.solve).grid(column=2, row=5, sticky=tk.W)

        self.inputs_frame = ttk.Frame(frame)
        self.inputs_frame.grid(column=0, row=6, columnspan=3, sticky=(tk.W, tk.E))

    def update_capacities(self):
        """Met à jour les champs en fonction du nombre de capacités choisi."""
        if self.num_capacities.get() == 1:
            self.capacity2_frame.grid_remove()
        else:
            self.capacity2_frame.grid()

    def generate_inputs(self):
        """Génère les champs pour entrer les données des articles."""
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        self.names = [tk.StringVar(value=f"Article {i + 1}") for i in range(self.num_objects.get())]
        self.values = [tk.IntVar(value=10) for i in range(self.num_objects.get())]
        self.weights = [tk.IntVar(value=5) for i in range(self.num_objects.get())]
        self.volumes = [tk.IntVar(value=3) for i in range(self.num_objects.get())]

        ttk.Label(self.inputs_frame, text="Nom").grid(column=0, row=0)
        ttk.Label(self.inputs_frame, text="Valeur").grid(column=1, row=0)
        ttk.Label(self.inputs_frame, text="Poids").grid(column=2, row=0)
        if self.num_capacities.get() == 2:
            ttk.Label(self.inputs_frame, text="Volume").grid(column=3, row=0)

        for i in range(self.num_objects.get()):
            ttk.Entry(self.inputs_frame, textvariable=self.names[i], width=15).grid(column=0, row=i + 1)
            ttk.Entry(self.inputs_frame, textvariable=self.values[i], width=10).grid(column=1, row=i + 1)
            ttk.Entry(self.inputs_frame, textvariable=self.weights[i], width=10).grid(column=2, row=i + 1)
            if self.num_capacities.get() == 2:
                ttk.Entry(self.inputs_frame, textvariable=self.volumes[i], width=10).grid(column=3, row=i + 1)

    def add_constraint(self):
        """Ajoute une contrainte personnalisée."""
        def save_constraint():
            try:
                raw_constraint = constraint_entry.get()
                self.constraints.append(eval(f"lambda x: {raw_constraint}"))
                messagebox.showinfo("Succès", "Contrainte ajoutée !")
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur dans la contrainte : {e}")

        add_window = tk.Toplevel(self.root)
        add_window.title("Ajouter une contrainte")
        ttk.Label(add_window, text="Entrez une contrainte (ex: x[0] + x[1] <= 1)").grid(column=0, row=0)
        constraint_entry = ttk.Entry(add_window, width=30)
        constraint_entry.grid(column=0, row=1)
        ttk.Button(add_window, text="Ajouter", command=save_constraint).grid(column=0, row=2)

    def solve(self):
        """Résout le problème de sac à dos."""
        names = [n.get() for n in self.names]
        values = [v.get() for v in self.values]
        weights = [w.get() for w in self.weights]
        volumes = [v.get() for v in self.volumes]
        capacity1 = self.capacity1.get()
        capacity2 = self.capacity2.get() if self.num_capacities.get() == 2 else 0
        capacities = {"Poids": (weights, capacity1)}
        if self.num_capacities.get() == 2:
            capacities["Volume"] = (volumes, capacity2)

        try:
            solution, optimal_value = solve_knapsack(names, values, weights, volumes, capacities, self.constraints, self.resolution_type.get())
            if solution:
                result = f"Valeur optimale: {optimal_value}\nSolution:\n" + "\n".join([f"{name}: {round(val, 2)}" for name, val in solution.items()])
                messagebox.showinfo("Résultat", result)
            else:
                messagebox.showerror("Erreur", "Pas de solution optimale trouvée.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur dans la résolution : {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = KnapsackApp(root)
    root.mainloop()
