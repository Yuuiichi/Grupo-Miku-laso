import re
from typing import Tuple

def validar_rut(rut: str) -> bool:
    rut = rut.replace(".", "").replace("-", "")
    
    if not re.match(r'^\d{7,8}[0-9Kk]$', rut):
        return False
    
    rut_num = rut[:-1]
    dv = rut[-1].upper()
    
    suma = 0
    multiplo = 2
    
    for digit in reversed(rut_num):
        suma += int(digit) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    return dv == dv_calculado


def formatear_rut(rut: str) -> str:

    rut = rut.replace(".", "").replace("-", "")
    return f"{rut[:-1]}-{rut[-1]}"


def validar_email(email: str) -> bool:
    """
    Valida formato de email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_password_fuerte(password: str) -> Tuple[bool, str]:
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    # Verificar caracteres especiales (opcional pero recomendado)
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return True, "Contraseña aceptable (se recomienda incluir caracteres especiales)"
    
    return True, "Contraseña fuerte"


def validar_password_basica(password: str) -> Tuple[bool, str]:

    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if password.isspace():
        return False, "La contraseña no puede contener solo espacios"
    
    return True, "Contraseña válida"
