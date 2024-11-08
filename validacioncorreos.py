import streamlit as st
import pandas as pd
import requests
import io

# Configuración de la API de ZeroBounce
ZERO_BOUNCE_API_KEY = "64babb3d17a4475ea72001b882708f6e"  # Reemplaza con tu API Key de ZeroBounce

def verificar_correo(correo):
    """
    Valida un correo usando la API de ZeroBounce.
    Retorna True si el correo es válido, de lo contrario, False.
    """
    url = "https://api.zerobounce.net/v2/validate"
    params = {
        "api_key": ZERO_BOUNCE_API_KEY,
        "email": correo
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Verifica si la respuesta contiene el estado 'status' y si es 'valid'
    if 'status' in data:
        return data['status'] == 'valid'
    else:
        st.warning(f"Error en la validación del correo {correo}: {data.get('error', 'Respuesta inesperada de la API')}")
        return False

def procesar_archivo(archivo):
    """
    Procesa un archivo de Excel, validando los correos y regresando
    un DataFrame solo con los correos válidos.
    """
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()  # Elimina espacios en blanco en los encabezados
    
    # Verifica si la columna 'correo' está en el archivo
    if 'Correo' not in df.columns:
        st.error("El archivo debe tener una columna llamada 'Correo'")
        return None

    # Filtra solo los correos válidos
    df['valido'] = df['Correo'].apply(verificar_correo)
    df_valido = df[df['valido'] == True].drop(columns=['valido'])
    return df_valido

def main():
    st.title("Validador de Correos con ZeroBounce")
    st.write("Adjunta uno o varios archivos de Excel para validar los correos en la columna 'correo'. Los correos inválidos serán eliminados del archivo de salida.")
    
    archivos = st.file_uploader("Sube tus archivos de Excel", type="xlsx", accept_multiple_files=True)

    if archivos:
        archivos_procesados = []
        
        for archivo in archivos:
            # Procesa cada archivo
            df_valido = procesar_archivo(archivo)
            if df_valido is not None:
                archivos_procesados.append((archivo.name, df_valido))
        
        if archivos_procesados and st.button("Descargar Archivos Validados"):
            for nombre, df in archivos_procesados:
                # Convierte cada DataFrame en un archivo Excel descargable
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Correos Validos')
                buffer.seek(0)
                
                # Botón de descarga
                st.download_button(
                    label=f"Descargar {nombre} (validados)",
                    data=buffer,
                    file_name=f"validados_{nombre}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
