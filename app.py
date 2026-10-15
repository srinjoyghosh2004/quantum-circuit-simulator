import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

st.set_page_config(page_title="QuantumLab — Interactive Quantum Circuit Simulator", page_icon="⚛️", layout="wide")

st.title("⚛️ QuantumLab — Interactive Quantum Circuit Simulator")
st.markdown("Build and simulate basic quantum circuits right in your browser using Qiskit, NumPy, and Streamlit.")

st.sidebar.header("🔧 Circuit Configuration")
num_qubits = st.sidebar.slider("Number of Qubits", min_num_qubits:=1, max_value=4, value=2)

qc = QuantumCircuit(num_qubits, num_qubits)

st.sidebar.subheader("Gate Operations")
st.sidebar.markdown("Add gates sequentially to your qubits:")

# Dynamic gate selection per qubit
for i in range(num_qubits):
    gate = st.sidebar.selectbox(f"Gate on Qubit {i}", ["None", "X (Pauli-Not)", "H (Hadamard)", "Y", "Z"], key=f"gate_{i}")
    if gate == "X (Pauli-Not)":
        qc.x(i)
    elif gate == "H (Hadamard)":
        qc.h(i)
    elif gate == "Y":
        qc.y(i)
    elif gate == "Z":
        qc.z(i)

# Optional CNOT for multi-qubit
if num_qubits >= 2:
    add_cnot = st.sidebar.checkbox("Add CNOT (CX) Gate")
    if add_cnot:
        control = st.sidebar.selectbox("Control Qubit", range(num_qubits), key="cnot_ctrl")
        target = st.sidebar.selectbox("Target Qubit", range(num_qubits), key="cnot_tgt")
        if control != target:
            qc.cx(control, target)
        else:
            st.sidebar.warning("Control and Target qubits must be different.")

qc.measure(range(num_qubits), range(num_qubits))

col1, col2 = st.columns(2)

with col1:
    st.subheader("📐 Circuit Diagram")
    fig_circ, ax_circ = plt.subplots(figsize=(6, 3))
    qc.draw(output='mpl', ax=ax_circ)
    st.pyplot(fig_circ)

with col2:
    st.subheader("📊 Measurement Probabilities")
    simulator = AerSimulator()
    job = simulator.run(qc, shots=1000)
    result = job.result()
    counts = result.get_counts(qc)
    
    fig_hist, ax_hist = plt.subplots(figsize=(6, 3))
    from qiskit.visualization import plot_histogram
    plot_histogram(counts, ax=ax_hist)
    st.pyplot(fig_hist)

st.markdown("---")
st.markdown("💡 **Tip:** Adjust gates on the left sidebar to see how superposition and entanglement change your circuit measurements instantly!")
