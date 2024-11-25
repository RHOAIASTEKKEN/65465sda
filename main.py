import tkinter as tk
from tkinter import ttk, messagebox
import re
from sympy import Poly, symbols, sympify, degree
from sympy.parsing.sympy_parser import parse_expr

class PolynomialDivisionCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de División de Polinomios")
        
        # Configuración de la ventana
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.numerator_var = tk.StringVar()
        self.denominator_var = tk.StringVar()
        
        # Crear y configurar el marco principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Etiquetas e inputs
        ttk.Label(main_frame, text="Numerador (dividendo):", font=('Arial', 12)).grid(row=0, column=0, pady=5)
        numerator_entry = ttk.Entry(main_frame, textvariable=self.numerator_var, width=50)
        numerator_entry.grid(row=1, column=0, pady=5)
        
        ttk.Label(main_frame, text="Denominador (divisor):", font=('Arial', 12)).grid(row=2, column=0, pady=5)
        denominator_entry = ttk.Entry(main_frame, textvariable=self.denominator_var, width=50)
        denominator_entry.grid(row=3, column=0, pady=5)
        
        # Botón de cálculo
        ttk.Button(main_frame, text="Dividir", command=self.perform_division).grid(row=4, column=0, pady=20)
        
        # Área de resultados
        self.result_text = tk.Text(main_frame, height=20, width=70, font=('Courier', 11))
        self.result_text.grid(row=5, column=0, pady=10)
        
        # Scrollbar para el área de resultados
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=5, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Instrucciones de uso
        instructions = """
        Instrucciones:
        - Escriba los polinomios de forma natural
        - Ejemplos de entrada válida:
          * 2x^2 + 3x + 1
          * x^2 - 4
          * 2x2 + 3x + 1
          * sqrt(2)x^3 + 1/2x
          * 3x + 2
        
        Nota: Puede usar x^2 o x2 para elevar al cuadrado
        """
        self.result_text.insert(tk.END, instructions)

    def format_polynomial(self, poly_str):
        # Limpiamos espacios extras
        poly_str = poly_str.replace(" ", "")
        
        # Lista de patrones de reemplazo
        replacements = [
            (r'(\d+)x(\d+)', r'\1*x^\2'),
            (r'(?<![\d\*])x(\d+)', r'x^\1'),
            (r'(\d+)x', r'\1*x'),
            (r'sqrt\((\d+)\)x', r'sqrt(\1)*x'),
            (r'(\d+)/(\d+)x', r'\1/\2*x'),
        ]
        
        # Aplicar todos los reemplazos
        for pattern, replacement in replacements:
            poly_str = re.sub(pattern, replacement, poly_str)
            
        return poly_str

    def parse_polynomial(self, poly_str):
        try:
            formatted_poly = self.format_polynomial(poly_str)
            x = symbols('x')
            expr = parse_expr(formatted_poly)
            return Poly(expr, x)
        except Exception as e:
            return None

    def pretty_print_polynomial(self, poly):
        if poly == 0:
            return "0"
            
        # Convertir el polinomio a string y limpiar
        poly_str = str(poly.as_expr())
        
        # Reemplazos para mejorar la presentación
        replacements = [
            (r'\*\*', '^'),  # Cambiar ** por ^
            (r'\*', ''),     # Eliminar *
            (r'sqrt\(([\d.]+)\)', r'√\1'),  # Mejorar presentación de raíz cuadrada
        ]
        
        for old, new in replacements:
            poly_str = re.sub(old, new, poly_str)
            
        return poly_str

    def polynomial_division_steps(self, numerator, denominator):
        steps = []
        x = symbols('x')
        current_dividend = numerator
        quotient_terms = []
        
        while degree(current_dividend) >= degree(denominator):
            # Obtener el término líder del cociente
            lead_term = (current_dividend.LC() / denominator.LC()) * x**(degree(current_dividend) - degree(denominator))
            quotient_terms.append(lead_term)
            
            # Multiplicar el divisor por el término líder
            subtrahend = Poly(lead_term * denominator.as_expr(), x)
            
            # Registrar el paso actual
            step = {
                'current_dividend': current_dividend,
                'lead_term': lead_term,
                'subtrahend': subtrahend,
                'next_dividend': current_dividend - subtrahend
            }
            steps.append(step)
            
            # Actualizar el dividendo para el siguiente paso
            current_dividend = current_dividend - subtrahend
        
        quotient = sum(quotient_terms)
        remainder = current_dividend
        
        return steps, Poly(quotient, x), remainder

    def perform_division(self):
        self.result_text.delete(1.0, tk.END)
        
        try:
            numerator_str = self.numerator_var.get().strip()
            denominator_str = self.denominator_var.get().strip()
            
            if not numerator_str or not denominator_str:
                self.result_text.insert(tk.END, "Por favor, ingrese ambos polinomios.")
                return
            
            numerator = self.parse_polynomial(numerator_str)
            denominator = self.parse_polynomial(denominator_str)
            
            if numerator is None or denominator is None:
                self.result_text.insert(tk.END, "Error: Formato de polinomio inválido")
                return
            
            # Obtener los pasos de la división
            steps, quotient, remainder = self.polynomial_division_steps(numerator, denominator)
            
            # Presentación de resultados
            self.result_text.insert(tk.END, "DIVISIÓN DE POLINOMIOS\n")
            self.result_text.insert(tk.END, "=" * 50 + "\n\n")
            
            self.result_text.insert(tk.END, "Dividendo: ")
            self.result_text.insert(tk.END, f"{numerator_str}\n")
            
            self.result_text.insert(tk.END, "Divisor: ")
            self.result_text.insert(tk.END, f"{denominator_str}\n\n")
            
            self.result_text.insert(tk.END, "PASO A PASO:\n")
            self.result_text.insert(tk.END, "-" * 50 + "\n\n")
            
            # Mostrar cada paso
            for i, step in enumerate(steps, 1):
                self.result_text.insert(tk.END, f"Paso {i}:\n")
                self.result_text.insert(tk.END, f"Dividendo actual: {self.pretty_print_polynomial(step['current_dividend'])}\n")
                self.result_text.insert(tk.END, f"Término del cociente: {self.pretty_print_polynomial(Poly(step['lead_term'], symbols('x')))}\n")
                self.result_text.insert(tk.END, f"Término × divisor: {self.pretty_print_polynomial(step['subtrahend'])}\n")
                self.result_text.insert(tk.END, f"Nuevo dividendo: {self.pretty_print_polynomial(step['next_dividend'])}\n\n")
            
            # Mostrar resultado final
            self.result_text.insert(tk.END, "RESULTADO FINAL:\n")
            self.result_text.insert(tk.END, "-" * 50 + "\n")
            self.result_text.insert(tk.END, f"Cociente: {self.pretty_print_polynomial(quotient)}\n")
            self.result_text.insert(tk.END, f"Residuo: {self.pretty_print_polynomial(remainder)}\n\n")
            
            # Mostrar la comprobación
            self.result_text.insert(tk.END, "Comprobación:\n")
            check_str = f"({self.pretty_print_polynomial(quotient)}) × ({denominator_str})"
            if self.pretty_print_polynomial(remainder) != "0":
                check_str += f" + ({self.pretty_print_polynomial(remainder)})"
            check_str += f" = {numerator_str}"
            self.result_text.insert(tk.END, check_str + "\n")
            
        except Exception as e:
            self.result_text.insert(tk.END, f"Error durante el cálculo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PolynomialDivisionCalculator(root)
    root.mainloop()