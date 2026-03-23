import numpy as np
import joblib
import ctypes
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_PATH = os.path.join(BASE_DIR, "SWC_Model/model.dll")
MODEL_PATH = os.path.join(BASE_DIR, "Python_Model/FULL_CABIN_R9.joblib")

# --- CONFIG ---
NUM_FEATURES = 384
NUM_TESTS = 100

# --- Load Python model ---
model = joblib.load(MODEL_PATH)

# --- Load C model ---
c_lib = ctypes.CDLL(DLL_PATH)

# Definir tipos
c_lib.model_predict.argtypes = [
    ctypes.POINTER(ctypes.c_double),   # input
    ctypes.POINTER(ctypes.c_double)    # output (array of 2 doubles)
]

# --- Test loop ---
errors_prob = []
errors_class = []

for i in range(NUM_TESTS):
    x = np.random.rand(NUM_FEATURES).astype(np.float64)

    # -------- Python --------
    py_prob = model.predict_proba(x.reshape(1, -1))[0, 1]  # P(class 1)
    py_class = int(py_prob >= 0.5)

    # -------- C --------
    c_input = x.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    # output array of 2 doubles
    c_output = (ctypes.c_double * 2)()

    c_lib.model_predict(c_input, c_output)

    c_prob = c_output[1]  # P(class 1)
    c_class = int(c_prob >= 0.5)

    # -------- Errors --------
    diff_prob = abs(py_prob - c_prob)
    diff_class = abs(py_class - c_class)

    errors_prob.append(diff_prob)
    errors_class.append(diff_class)

    print(
        f"Test {i}: "
        f"PY_prob={py_prob:.6f} | C_prob={c_prob:.6f} | diff_prob={diff_prob:.6e} | "
        f"PY_class={py_class} | C_class={c_class} | diff_class={diff_class}"
    )

# --- Summary ---
print("\n--- RESULT (PROBABILITY) ---")
print(f"Max error: {max(errors_prob)}")
print(f"Mean error: {np.mean(errors_prob)}")

print("\n--- RESULT (CLASS) ---")
print(f"Classification mismatch rate: {np.mean(errors_class)}")

# ==============================
# --- MODEL INFO ---
# ==============================
model_file_size = os.path.getsize(MODEL_PATH)
dll_file_size = os.path.getsize(DLL_PATH)

print("\nModel:")
print(model)

print("\n--- ROM REPORT ---")
print(f"Model file size (.joblib): {model_file_size / 1024:.2f} KB")
print(f"DLL file size (.dll): {dll_file_size / 1024:.2f} KB")
