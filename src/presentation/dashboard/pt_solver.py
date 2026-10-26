import math

def solve_pt_interpolated(gas_row, temp_c, state_type="Bubble"):
    """
    Motor físico-termodinámico que estima la presión de saturación bubble/dew
    a través del algoritmo Clausius-Clapeyron corregido por temperatura crítica y deslizamiento.
    """
    T = temp_c + 273.15
    T_b = gas_row["boiling_point_c"] + 273.15
    T_c = gas_row["critical_temp_c"] + 273.15
    P_c = gas_row["critical_pressure_bar"]
    
    if temp_c >= gas_row["critical_temp_c"]:
        return P_c
        
    glide = 0.0
    if state_type == "Dew":
        if gas_row["ashrae_name"] == "R-407C": glide = 5.0
        elif gas_row["ashrae_name"] == "R-455A": glide = 12.0
        elif gas_row["ashrae_name"].startswith("R-4"): glide = 2.0
        
    evaluated_temp = temp_c - glide
    T_eval = evaluated_temp + 273.15
    
    trouton = 10.5
    if gas_row["compound_type"] == "Natural":
        trouton = 12.8 if gas_row["ashrae_name"] == "R-717" else 10.6
        
    ln_p = math.log(1.01325) + trouton * T_b * (1.0 / T_b - 1.0 / T_eval)
    p_abs = math.exp(ln_p)
    
    T_r = T_eval / T_c
    if T_r > 0.6:
        correction = 1.0 + 0.15 * math.sin(math.pi * (T_r - 0.6) / 0.4)
        p_abs = p_abs * correction
        
    return min(max(p_abs, 0.005), P_c)
