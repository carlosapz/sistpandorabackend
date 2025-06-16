import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Funciones de cálculo
def matriz_rigidez_viga(E, I, L):
    k_local = (E * I / L**3) * np.array([
        [12, 6*L, -12, 6*L],
        [6*L, 4*L**2, -6*L, 2*L**2],
        [-12, -6*L, 12, -6*L],
        [6*L, 2*L**2, -6*L, 4*L**2]
    ])
    return k_local

def ensamblar_matriz_rigidez(nodos, E, I, L):
    K_global = np.zeros((2 * nodos, 2 * nodos))  # Matriz global (dos grados de libertad por nodo)
    k_local = matriz_rigidez_viga(E, I, L)
    pasos.append(f"Paso 1: Matriz de rigidez local de cada segmento:\n{k_local}")
    
    # Ensamblaje para cada elemento de la viga
    for i in range(nodos - 1):
        K_global[2*i:2*i+4, 2*i:2*i+4] += k_local
    pasos.append(f"\nPaso 2: Matriz de rigidez global ensamblada:\n{K_global}")
    return K_global

def aplicar_condiciones_frontera(K_global, nodos_restringidos):
    for nodo in nodos_restringidos:
        K_global[nodo, :] = 0
        K_global[:, nodo] = 0
        K_global[nodo, nodo] = 1
    pasos.append(f"\nPaso 3: Aplicación de condiciones de frontera (desplazamiento y rotación restringidos en nodo 1):\n{K_global}")
    return K_global

def resolver(K_global, fuerzas):
    desplazamientos = np.linalg.solve(K_global, fuerzas)
    pasos.append(f"\nPaso 4: Resolución del sistema de ecuaciones para obtener los desplazamientos:\n{desplazamientos}")
    return desplazamientos

def calcular():
    global pasos
    pasos = []  # Limpiar los pasos anteriores

    try:
        # Leer los inputs de la interfaz
        L = float(entry_longitud.get())  # Longitud de la viga
        E = float(entry_modulo.get())  # Módulo de elasticidad
        I = float(entry_inercia.get())  # Inercia de la sección
        nodos = int(entry_nodos.get())  # Número de nodos
        fuerza = float(entry_fuerza.get())  # Fuerza aplicada

        # Cálculos
        L_segmento = L / (nodos - 1)
        K_global = ensamblar_matriz_rigidez(nodos, E, I, L_segmento)

        # Condiciones de frontera (restricción en el primer nodo)
        nodos_restringidos = [0, 1]  # Restricción en el primer nodo (desplazamiento y rotación)
        K_global_restringido = aplicar_condiciones_frontera(K_global, nodos_restringidos)

        # Fuerzas aplicadas (en N)
        fuerzas = np.zeros(2 * nodos)
        fuerzas[4] = -fuerza  # Fuerza aplicada en el último nodo (N)

        # Resolver para los desplazamientos
        desplazamientos = resolver(K_global_restringido, fuerzas)

        # Mostrar resultados numéricos
        label_resultados.config(text="Desplazamientos: \n" + str(desplazamientos))

        # Mostrar pasos intermedios
        steps_text.delete(1.0, tk.END)  # Limpiar el área de texto
        for paso in pasos:
            steps_text.insert(tk.END, paso + "\n\n")

        # Graficar los resultados
        nodos_posiciones = np.linspace(0, L, nodos)
        plt.figure(figsize=(10, 6))
        plt.plot(nodos_posiciones, desplazamientos[::2], label="Desplazamiento en Y", marker='o')
        plt.title("Desplazamientos de la viga hiperestática")
        plt.xlabel("Posición a lo largo de la viga (m)")
        plt.ylabel("Desplazamiento (m)")
        plt.grid(True)
        plt.legend()
        plt.show()

    except ValueError:
        messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos.")

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Cálculo de viga hiperestática - Matriz de Rigidez")

# Estilo de la interfaz
root.config(bg="#F0F0F0")
root.geometry("800x600")

# Etiquetas y campos de entrada
tk.Label(root, text="Longitud de la viga (L) [m]:", bg="#F0F0F0").pack(pady=5)
entry_longitud = tk.Entry(root)
entry_longitud.pack(pady=5)

tk.Label(root, text="Módulo de elasticidad (E) [Pa]:", bg="#F0F0F0").pack(pady=5)
entry_modulo = tk.Entry(root)
entry_modulo.pack(pady=5)

tk.Label(root, text="Inercia de la sección (I) [m^4]:", bg="#F0F0F0").pack(pady=5)
entry_inercia = tk.Entry(root)
entry_inercia.pack(pady=5)

tk.Label(root, text="Número de nodos:", bg="#F0F0F0").pack(pady=5)
entry_nodos = tk.Entry(root)
entry_nodos.pack(pady=5)

tk.Label(root, text="Fuerza aplicada (F) [N]:", bg="#F0F0F0").pack(pady=5)
entry_fuerza = tk.Entry(root)
entry_fuerza.pack(pady=5)

# Botón para calcular
button_calcular = tk.Button(root, text="Calcular", command=calcular, bg="#4CAF50", fg="white")
button_calcular.pack(pady=20)

# Etiqueta para mostrar los resultados
label_resultados = tk.Label(root, text="Desplazamientos: \n", bg="#F0F0F0")
label_resultados.pack(pady=10)

# Área de texto para mostrar los pasos intermedios
steps_text = scrolledtext.ScrolledText(root, width=90, height=15, wrap=tk.WORD)
steps_text.pack(pady=10)

# Ejecutar la interfaz gráfica
root.mainloop()
