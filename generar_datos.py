"""
Genera los datos ficticios de una foto salarial al 30/09/2026: los colaboradores
activos de una embotelladora mediana (520 personas) y la banda salarial de cada
cargo, con montos en bolivianos (Bs).

Salidas (carpeta datos/):
  - colaboradores.csv  una fila por colaborador activo
  - bandas.csv         banda salarial por cargo: mínimo, punto medio y máximo

Es la misma embotelladora ficticia de los otros proyectos del portafolio: mismas
áreas, niveles, cargos y sueldos medios. Todo es inventado: no hay datos de
ninguna empresa real.

Uso:
    python generar_datos.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
FECHA_CORTE = pd.Timestamp("2026-09-30")
DOTACION = 520

# --- Supuestos generales (los mismos de los otros proyectos) ------------------
SALARIO_MINIMO = 2750                      # salario mínimo nacional (supuesto fijo)
INCREMENTO_ANUAL = 0.04                    # incremento salarial de cada mayo
INDICE_2026 = (1 + INCREMENTO_ANUAL) ** 3  # mayo de 2024, 2025 y 2026 sobre los sueldos medios de 2023

# --- Estructura de la empresa -------------------------------------------------
# peso: participación en la dotación | niveles: mezcla operativo / técnico / profesional
AREAS = {
    "Producción":                dict(peso=0.40, niveles=[0.82, 0.13, 0.05]),
    "Logística y Distribución":  dict(peso=0.24, niveles=[0.85, 0.11, 0.04]),
    "Ventas":                    dict(peso=0.14, niveles=[0.82, 0.12, 0.06]),
    "Mantenimiento":             dict(peso=0.08, niveles=[0.35, 0.55, 0.10]),
    "Calidad":                   dict(peso=0.06, niveles=[0.45, 0.45, 0.10]),
    "Administración y Finanzas": dict(peso=0.08, niveles=[0.40, 0.40, 0.20]),
}

# salario_medio: sueldo medio del nivel en 2023 (Bs por mes)
# amplitud: la banda va de punto medio × (1 - amplitud) a punto medio × (1 + amplitud)
NIVELES = {
    "Operativo":              dict(salario_medio=3600, amplitud=0.15),
    "Técnico y supervisión":  dict(salario_medio=6500, amplitud=0.20),
    "Profesional y jefatura": dict(salario_medio=12500, amplitud=0.25),
}

# peso: participación del cargo dentro de su área y nivel
# sueldo: punto medio del cargo relativo al sueldo medio del nivel
# mujer: probabilidad de que el cargo lo ocupe una mujer
CARGOS = pd.DataFrame([
    ("Operario de línea",          "Producción",                "Operativo",              0.50, 1.00, 0.28),
    ("Operador de llenadora",      "Producción",                "Operativo",              0.25, 1.10, 0.08),
    ("Auxiliar de producción",     "Producción",                "Operativo",              0.25, 0.90, 0.50),
    ("Supervisor de turno",        "Producción",                "Técnico y supervisión",  1.00, 1.05, 0.18),
    ("Jefe de producción",         "Producción",                "Profesional y jefatura", 0.30, 1.25, 0.05),
    ("Ingeniero de procesos",      "Producción",                "Profesional y jefatura", 0.70, 0.85, 0.20),
    ("Chofer repartidor",          "Logística y Distribución",  "Operativo",              0.40, 1.12, 0.02),
    ("Ayudante de reparto",        "Logística y Distribución",  "Operativo",              0.40, 0.86, 0.05),
    ("Auxiliar de almacén",        "Logística y Distribución",  "Operativo",              0.20, 0.92, 0.20),
    ("Supervisor de distribución", "Logística y Distribución",  "Técnico y supervisión",  0.60, 1.05, 0.10),
    ("Encargado de almacén",       "Logística y Distribución",  "Técnico y supervisión",  0.40, 0.92, 0.25),
    ("Jefe de logística",          "Logística y Distribución",  "Profesional y jefatura", 1.00, 1.15, 0.10),
    ("Preventista",                "Ventas",                    "Operativo",              0.60, 1.02, 0.35),
    ("Mercaderista",               "Ventas",                    "Operativo",              0.40, 0.86, 0.75),
    ("Supervisor de ventas",       "Ventas",                    "Técnico y supervisión",  1.00, 1.08, 0.30),
    ("Jefe comercial",             "Ventas",                    "Profesional y jefatura", 0.35, 1.30, 0.15),
    ("Analista comercial",         "Ventas",                    "Profesional y jefatura", 0.65, 0.72, 0.50),
    ("Ayudante de mantenimiento",  "Mantenimiento",             "Operativo",              1.00, 0.95, 0.05),
    ("Técnico mecánico",           "Mantenimiento",             "Técnico y supervisión",  0.55, 1.00, 0.04),
    ("Técnico eléctrico",          "Mantenimiento",             "Técnico y supervisión",  0.45, 1.02, 0.06),
    ("Jefe de mantenimiento",      "Mantenimiento",             "Profesional y jefatura", 1.00, 1.10, 0.00),
    ("Inspector de calidad",       "Calidad",                   "Operativo",              1.00, 1.00, 0.75),
    ("Analista de laboratorio",    "Calidad",                   "Técnico y supervisión",  1.00, 0.92, 0.65),
    ("Jefe de calidad",            "Calidad",                   "Profesional y jefatura", 1.00, 1.10, 0.30),
    ("Auxiliar administrativo",    "Administración y Finanzas", "Operativo",              0.60, 0.95, 0.80),
    ("Cajero",                     "Administración y Finanzas", "Operativo",              0.40, 1.00, 0.75),
    ("Asistente contable",         "Administración y Finanzas", "Técnico y supervisión",  0.60, 0.85, 0.70),
    ("Asistente de RRHH",          "Administración y Finanzas", "Técnico y supervisión",  0.40, 0.85, 0.80),
    ("Contador general",           "Administración y Finanzas", "Profesional y jefatura", 0.25, 1.05, 0.30),
    ("Jefe de RRHH",               "Administración y Finanzas", "Profesional y jefatura", 0.20, 1.05, 0.45),
    ("Analista financiero",        "Administración y Finanzas", "Profesional y jefatura", 0.55, 0.75, 0.40),
], columns=["cargo", "area", "nivel", "peso", "sueldo", "mujer"])

# Antigüedad de la dotación activa: (probabilidad, desde, hasta) en años.
# El último tramo es 6 años más una cola exponencial de media 5 años (tope 30).
TRAMOS_ANTIGUEDAD = [(0.19, 0, 1), (0.27, 1, 3), (0.24, 3, 6), (0.30, 6, None)]
# En Producción y Logística se contrataron más mujeres en los últimos 3 años
FACTOR_MUJER_RECIENTE = 1.5   # ingresos de los últimos 3 años
FACTOR_MUJER_ANTIGUA = 0.8    # ingresos anteriores

# --- Cómo se forma el haber básico (posición dentro de la banda) ---------------
ENTRADA = 0.92              # quien recién entra gana cerca del 92% del punto medio de su banda
PROGRESION_ANUAL = 0.016    # y sube cerca de 1,6% por año de antigüedad, hasta 10 años
TOPE_PROGRESION = 10
EFECTO_DESEMPENO = 0.02     # cerca de 2% por cada punto de evaluación por encima (o debajo) de 3
RUIDO = 0.05                # variación individual (desvío del logaritmo del sueldo)
RUIDO_INGRESO = 0.03        # los ingresos del último año varían menos: entran con un sueldo de ingreso

# --- Patrones sembrados: lo que el análisis tiene que encontrar ---------------
# 1) Brecha de género que el cargo, la antigüedad y el desempeño no explican.
#    Se concentra en Técnico y supervisión (por ejemplo, aumentos más bajos al
#    ascender); en los otros niveles es chica.
BRECHA_MUJERES = {"Operativo": 0.005, "Técnico y supervisión": 0.12, "Profesional y jefatura": 0.005}
# 2) Compresión: el mercado de estos cargos subió y la empresa ya contrata más
#    arriba. La banda se actualizó en 2026, pero el sueldo de quienes ya estaban no.
CARGOS_COMPRIMIDOS = ["Operario de línea", "Operador de llenadora", "Chofer repartidor"]
SUBA_MERCADO = 0.08         # el punto medio de la banda de esos cargos subió 8%
ENTRADA_MERCADO = 0.96      # los ingresos del último año entraron cerca del 96% del nuevo punto medio
# 3) Sueldos fuera de banda
PROB_SIN_AJUSTE = 0.03      # sueldos que quedaron atrás (por ejemplo, un ascenso sin ajuste)
EFECTO_SIN_AJUSTE = 0.12    # quedan cerca de 12% más abajo
PROB_HISTORICO = 0.06       # entre quienes tienen 8 años o más: sueldo histórico negociado
EFECTO_HISTORICO = 0.20     # cerca de 20% más arriba


def bandas_salariales():
    """Banda de cada cargo a septiembre de 2026. El punto medio se redondea a Bs 20, así el
    mínimo y el máximo son montos exactos (por ejemplo, 85% y 115% del punto medio)."""
    bandas = CARGOS[["cargo", "area", "nivel"]].copy()
    medio = (CARGOS["nivel"].map(lambda n: NIVELES[n]["salario_medio"]) * CARGOS["sueldo"] * INDICE_2026
             * np.where(CARGOS["cargo"].isin(CARGOS_COMPRIMIDOS), 1 + SUBA_MERCADO, 1.0))
    medio = (medio / 20).round() * 20
    amplitud = CARGOS["nivel"].map(lambda n: NIVELES[n]["amplitud"])
    bandas["minimo_bs"] = (medio * (1 - amplitud)).round().astype(int)
    bandas["punto_medio_bs"] = medio.astype(int)
    bandas["maximo_bs"] = (medio * (1 + amplitud)).round().astype(int)
    return bandas


def dotacion_por_cargo():
    """Personas por cargo según la estructura: peso del área × peso del nivel × peso del cargo.
    Se redondea por el método del mayor resto para que el total sea DOTACION."""
    orden_niveles = list(NIVELES)
    peso = np.array([
        AREAS[c.area]["peso"] * AREAS[c.area]["niveles"][orden_niveles.index(c.nivel)] * c.peso
        for c in CARGOS.itertuples()
    ])
    esperado = peso / peso.sum() * DOTACION
    cantidad = np.floor(esperado).astype(int)
    faltan = DOTACION - cantidad.sum()
    cantidad[np.argsort(-(esperado - cantidad), kind="stable")[:faltan]] += 1
    return cantidad


def sortear_antiguedad(rng):
    probabilidades = [t[0] for t in TRAMOS_ANTIGUEDAD]
    _, desde, hasta = TRAMOS_ANTIGUEDAD[rng.choice(len(TRAMOS_ANTIGUEDAD), p=probabilidades)]
    if hasta is None:
        return min(desde + rng.exponential(5), 30)
    return rng.uniform(desde, hasta)


def generar_colaboradores(rng, bandas):
    punto_medio = bandas.set_index("cargo")["punto_medio_bs"]
    posiciones = rng.permutation(np.repeat(CARGOS.index, dotacion_por_cargo()))

    filas = []
    for i in posiciones:
        c = CARGOS.loc[i]
        anios = sortear_antiguedad(rng)

        prob_mujer = c.mujer
        if c.area in ("Producción", "Logística y Distribución"):
            prob_mujer *= FACTOR_MUJER_RECIENTE if anios < 3 else FACTOR_MUJER_ANTIGUA
        mujer = rng.random() < prob_mujer
        desempeno = int(np.clip(round(rng.normal(3.3, 0.8)), 1, 5))

        # posición en la banda (logaritmo del cociente sueldo / punto medio)
        ruido = rng.normal(0, RUIDO_INGRESO if anios < 1 else RUIDO)
        if c.cargo in CARGOS_COMPRIMIDOS and anios < 1:
            posicion = np.log(ENTRADA_MERCADO)          # contratado al nuevo valor de mercado
        else:
            posicion = np.log(ENTRADA) + PROGRESION_ANUAL * min(anios, TOPE_PROGRESION)
            if c.cargo in CARGOS_COMPRIMIDOS:
                posicion -= np.log(1 + SUBA_MERCADO)    # su sueldo sigue atado al mercado anterior
        posicion += EFECTO_DESEMPENO * (desempeno - 3) + ruido
        if mujer:
            posicion -= BRECHA_MUJERES[c.nivel]
        if rng.random() < PROB_SIN_AJUSTE:
            posicion -= EFECTO_SIN_AJUSTE
        if anios >= 8 and rng.random() < PROB_HISTORICO:
            posicion += EFECTO_HISTORICO

        haber = max(round(punto_medio[c.cargo] * np.exp(posicion)), SALARIO_MINIMO)
        filas.append(dict(
            area=c.area,
            cargo=c.cargo,
            nivel=c.nivel,
            genero="Mujer" if mujer else "Hombre",
            fecha_ingreso=(FECHA_CORTE - pd.Timedelta(days=int(anios * 365.25))).date(),
            evaluacion_desempeno=desempeno,
            haber_basico_bs=int(haber),
        ))

    tabla = pd.DataFrame(filas).sort_values("fecha_ingreso", kind="stable").reset_index(drop=True)
    tabla.insert(0, "id_colaborador", [f"C{n:04d}" for n in range(1, len(tabla) + 1)])
    return tabla


def main():
    carpeta = Path(__file__).resolve().parent / "datos"
    carpeta.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEMILLA)
    bandas = bandas_salariales()
    colaboradores = generar_colaboradores(rng, bandas)
    colaboradores.to_csv(carpeta / "colaboradores.csv", index=False, encoding="utf-8")
    bandas.to_csv(carpeta / "bandas.csv", index=False, encoding="utf-8")
    print(f"colaboradores.csv: {len(colaboradores):,} filas")
    print(f"bandas.csv: {len(bandas):,} cargos")


if __name__ == "__main__":
    main()
