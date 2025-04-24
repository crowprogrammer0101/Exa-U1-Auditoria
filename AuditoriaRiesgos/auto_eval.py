import requests

URL = "http://localhost:5500"
SALIDA = "resultados_riesgos.txt"

activos = [
    {"activo": "Servidor de Base de Datos", "tipo": "Base de Datos"},
    {"activo": "Aplicación Web de Banca", "tipo": "Aplicación"},
    {"activo": "Firewall Perimetral", "tipo": "Seguridad"},
    {"activo": "VPN Corporativa", "tipo": "Infraestructura"},
    {"activo": "Base de Datos Clientes", "tipo": "Información"}
]

def analizar_y_tratar(activo, archivo):
    print(f"\n🔍 Analizando: {activo['activo']}")
    archivo.write(f"\n🔍 Activo: {activo['activo']} ({activo['tipo']})\n")

    res_riesgos = requests.post(f"{URL}/analizar-riesgos", json={"activo": activo["activo"]})
    if res_riesgos.status_code != 200:
        mensaje = f"❌ Error en análisis: {res_riesgos.text}"
        print(mensaje)
        archivo.write(mensaje + "\n")
        return

    data = res_riesgos.json()
    riesgos = data["riesgos"]
    impactos = data["impactos"]

    for i in range(len(riesgos)):
        riesgo = riesgos[i]
        impacto = impactos[i]
        print(f"⚠️ Riesgo: {riesgo} — Impacto: {impacto}")
        archivo.write(f"⚠️ Riesgo: {riesgo}\n➡️ Impacto: {impacto}\n")

        res_tratamiento = requests.post(f"{URL}/sugerir-tratamiento", json={
            "activo": activo["activo"],
            "riesgo": riesgo,
            "impacto": impacto
        })

        if res_tratamiento.status_code == 200:
            tratamiento = res_tratamiento.json()["tratamiento"]
            print(f"💊 Tratamiento: {tratamiento}\n")
            archivo.write(f"💊 Tratamiento: {tratamiento}\n\n")
        else:
            error_msg = f"❌ Error en tratamiento: {res_tratamiento.text}"
            print(error_msg)
            archivo.write(error_msg + "\n\n")

if __name__ == "__main__":
    with open(SALIDA, "w", encoding="utf-8") as archivo:
        archivo.write("📋 RESULTADO DEL ANÁLISIS AUTOMATIZADO DE RIESGOS\n")
        archivo.write("="*50 + "\n")
        for activo in activos:
            analizar_y_tratar(activo, archivo)

    print(f"\n✅ Todo listo. Revisa el archivo: {SALIDA}")
