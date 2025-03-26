# Datos del préstamo
monto_credito = 150000  # Monto restante después del enganche
tasa_interes_anual = 0.18  # Tasa de interés anual (18%)
plazo_meses = 36  # Plazo en meses

# Cálculo de la tasa de interés mensual
tasa_interes_mensual = tasa_interes_anual / 12

# Fórmula de amortización para calcular el pago mensual
pago_mensual = monto_credito * (tasa_interes_mensual * (1 + tasa_interes_mensual)**plazo_meses) / ((1 + tasa_interes_mensual)**plazo_meses - 1)

print(pago_mensual)