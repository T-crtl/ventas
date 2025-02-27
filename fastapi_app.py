from fastapi import FastAPI, HTTPException
import pyodbc

# Configura la conexión a la base de datos SQL Server
def get_db_connection():
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=SERVIDOR2;"  # Cambia esto por tu servidor
        "DATABASE=SAE9EMPRE01;"         # Cambia esto por tu base de datos
        "UID=sa;"       # Cambia esto por tu usuario
        "PWD=Aspel01;"    # Cambia esto por tu contraseña
    )
    return pyodbc.connect(connection_string)

app = FastAPI()

@app.get("/buscar_cantidad/")
async def buscar_cantidad(cvelote: str):
    try:
        # Conecta a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Realiza la consulta SQL
        query = f"SELECT [CANTIDAD] FROM [dbo].[PROD_ORDENES01] WHERE [CVELOTE] = ?"
        cursor.execute(query, cvelote)
        result = cursor.fetchone()

        # Cierra la conexión
        cursor.close()
        conn.close()

        # Si no se encuentra el registro, devuelve un error 404
        if not result:
            raise HTTPException(status_code=404, detail="Lote no encontrado")

        # Devuelve el valor de la columna [CANTIDAD]
        return {"cvelote": cvelote, "cantidad": result[0]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#test code