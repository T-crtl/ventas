import os
import sys
import django
import pyodbc

# Configuración de entorno
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventas.settings')
django.setup()

from modulo_ventas.models import Client

#conectar a DB aspel
servidor = 'SERVIDOR2'
database = 'SAE9EMPRE01'
username = ''
password = ''
connection_string = f'DRIVER={{SQL SERVER}};SERVER={servidor};DATABASE={database};UID={username};PWD={password}'

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    print("Conexion exitosa a la Base de Datos")
except Exception as e:
    print(f"Error al conectarse a {e}")
    exit()
    
#Consultar datos de la tabla clientes

try:
    cursor.execute("SELECT CLAVE, NOMBRE, RFC, CALLE, NUMINT, NUMEXT, COLONIA, CODIGO, MUNICIPIO, ESTADO, PAIS, TELEFONO, CLASIFIC, CURP, EMAILPRED FROM CLIE01 WHERE NOMBRE NOT LIKE '%MOSTR%' AND NOMBRE NOT LIKE '%EMPLEADO%'")
    clientes_aspel = cursor.fetchall()
    print(f"Se encontraron {len(clientes_aspel)} clientes en la base de datos")
except Exception as e:
    print(f"Hubo un error al consultar la tabla de clientes: {e}")
    exit()
    
for cliente_aspel in clientes_aspel:
    clave = cliente_aspel.CLAVE
    nombre = cliente_aspel.NOMBRE
    rfc = cliente_aspel.RFC
    calle = cliente_aspel.CALLE
    numint = cliente_aspel.NUMINT
    numext = cliente_aspel.NUMEXT
    colonia = cliente_aspel.COLONIA
    codigo = cliente_aspel.CODIGO
    municipio = cliente_aspel.MUNICIPIO
    estado = cliente_aspel.ESTADO
    pais = cliente_aspel.PAIS
    tel = cliente_aspel.TELEFONO
    clasific = cliente_aspel.CLASIFIC
    curp = cliente_aspel.CURP
    email = cliente_aspel.EMAILPRED
    
    cliente = Client(
        clave_cliente = clave,
        nombre_cliente = nombre,
        rfc = rfc,
        calle = calle,
        numint = numint,
        numext = numext,
        colonia = colonia,
        codigo = codigo,
        municipio = municipio,
        estado = estado,
        pais = pais,
        telefono = tel,
        clasificacion = clasific,
        curp = curp,
        email = email,
    )
    cliente.save()
    print(f"Cliente {nombre} guardado en la base de datos de Django.")
        # Cerrar la conexión
conn.close()