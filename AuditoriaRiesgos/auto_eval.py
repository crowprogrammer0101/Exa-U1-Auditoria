import requests

URL = "http://localhost:5500"
activos = [
    {"activo": "Servidor de Base de Datos", "tipo": "Base de Datos"},
    {"activo": "Aplicación Web de Banca", "tipo": "Aplicación"},
    {"activo": "Firewall Perimetral", "tipo": "Seguridad"},
    {"activo": "VPN Corporativa", "tipo": "Infraestructura"},
    {"activo": "Base de Datos Clientes", "tipo": "Información"}
]

def analizar_y_tratar(activo):
    print(f"\n🔍 Analizando: {activo['activo']}")

    # Paso 1: Analizar riesgos
    res_riesgos = requests.post(f"{URL}/analizar-riesgos", json={"activo": activo["activo"]})
    if res_riesgos.status_code != 200:
        print(f"❌ Error en análisis de {activo['activo']}: {res_riesgos.text}")
        return

    data = res_riesgos.json()
    riesgos = data["riesgos"]
    impactos = data["impactos"]

    # Mostrar riesgos e impactos
    for i in range(len(riesgos)):
        riesgo = riesgos[i]
        impacto = impactos[i]
        print(f"⚠️ Riesgo: {riesgo} — Impacto: {impacto}")

        # Paso 2: Solicitar tratamiento
        res_tratamiento = requests.post(f"{URL}/sugerir-tratamiento", json={
            "activo": activo["activo"],
            "riesgo": riesgo,
            "impacto": impacto
        })

        if res_tratamiento.status_code == 200:
            tratamiento = res_tratamiento.json()["tratamiento"]
            print(f"💊 Tratamiento: {tratamiento}\n")
        else:
            print(f"❌ Error en sugerencia: {res_tratamiento.text}")

if __name__ == "__main__":
    for activo in activos:
        analizar_y_tratar(activo)
