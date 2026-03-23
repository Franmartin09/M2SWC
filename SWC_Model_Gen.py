import joblib
import m2cgen as m2c
import os
import datetime
import re

def calculate_metrics(c_code, features):
    constants = re.findall(r'[-+]?\d*\.\d+(?:[eE][-+]?\d+)?', c_code)
    est_rom_kb = ((len(constants) * 8) + (len(c_code) // 4)) / 1024
    lines = c_code.split('\n')
    max_indent = max([len(l) - len(l.lstrip()) for l in lines]) if lines else 0
    est_ram_bytes = (features * 8) + (max_indent * 16) + 256
    return est_rom_kb, est_ram_bytes

# --- 1. CONFIGURACIÓN ---
model_path = r"E:\Proyectos\AUTOSAR_SWC_Gen\PythonModels2C\Python_Model\FULL_CABIN_R9.joblib"
output_folder = "SWC_Model"

# Rutas de los 2 archivos a generar
swc_internal_h_file = os.path.join(output_folder, "ModelLib.h")
swc_internal_c_file = os.path.join(output_folder, "ModelLib.c")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Carga del modelo (Mockup para que el script corra si no tienes el archivo)
try:
    model = joblib.load(model_path)
    num_features = getattr(model, "n_features_in_", 0)
    model_type_name = f"{type(model).__module__}.{type(model).__name__}"
except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    raise

# --- 2. ANÁLISIS DE FOOTPRINT (Igual) ---
# Si no falló la carga, generamos el código real
if 'model' in locals():
    raw_c_code = m2c.export_to_c(model, function_name="model_predict")

rom_kb, ram_bytes = calculate_metrics(raw_c_code, num_features)


# --- 3. GENERACIÓN: MODEL ---
# 3.1 Implementación (.c) - Quitamos 'static' para que pueda llamarse desde fuera
internal_c_content = f"""/*******************************************************************************
 * @file    ModelLib.c
 * @brief   Auto-generated Inference Engine Implementation
 * @author  Fran Martin Aguilar
 * @date    {datetime.date.today()}
 *******************************************************************************/
#include "ModelLib.h"

{raw_c_code}
"""
with open(swc_internal_c_file, "w") as f: f.write(internal_c_content)

# Busca la firma completa de la función model_predict
match = re.search(r'([a-zA-Z_][\w\s\*]*model_predict\s*\([^)]*\))', raw_c_code)
    
if match:
    function_signature = match.group(1).strip()
else:
    raise ValueError("No se pudo encontrar la firma de model_predict en el código generado")


# 3.2 Declaración (.h) - Solo la firma de la función
internal_h_content = f"""/*******************************************************************************
 * @file    ModelLib.h
 * @brief   Auto-generated Inference Engine Header
 * @author  Fran Martin Aguilar
 * @date    {datetime.date.today()}
 *
 * --- ESTIMATED RESOURCE FOOTPRINT ---
 * ROM (Flash):    ~{rom_kb:.2f} KB
 * RAM (Stack):    ~{ram_bytes} Bytes
 *******************************************************************************/
#ifndef ModelLib_Engine_H
#define ModelLib_Engine_H

/* Contract: The model expects an array of {num_features} doubles */
extern {function_signature};

#endif /* ModelLib_Engine_H */
"""
with open(swc_internal_h_file, "w") as f: f.write(internal_h_content)

# --- 5. RESUMEN ---
print("-" * 50)
print(f"✅ ARQUITECTURA AUTOSAR GENERADA CON ÉXITO EN: {output_folder}")
print(f"📁 Archivos creados:")
print(f"   1. {os.path.basename(swc_internal_h_file)} (Modelo ML - Contrato)")
print(f"   2. {os.path.basename(swc_internal_c_file)} (Modelo ML - Matemáticas)")
print("-" * 50)