from datetime import datetime, timedelta

def calcular_fecha_devolucion(tipo_prestamo: str, tipo_documento: str) -> datetime:
    '''
    Calcula la fecha de devolución basada en el tipo de préstamo y el tipo de documento.
    '''
    ahora = datetime.now()

    if tipo_prestamo == "sala":
        return ahora + timedelta(hours=4)
    
    if tipo_prestamo == "domicilio":
        if tipo_documento.lower() == "libro":
            return ahora + timedelta(days=7)
        elif tipo_documento.lower() == "multimedia":
            return ahora + timedelta(days=3)
    
    return ahora + timedelta(days=5)  # Valor por defecto si no coincide ningún caso