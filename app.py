import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector

st.set_page_config(
    page_title="QuantumLab — Advanced Interactive Quantum Simulator", 
    page_icon="⚛️", 
    layout="wide"
)

st.title("⚛️ QuantumLab — Interactive Quantum Circuit Simulator")
st.markdown("Build and simulate multi-qubit quantum circuits with real-time statevectors, histograms, and Bloch spheres.")

st.sidebar.header("🔧 Circuit Settings")

preset = st.sidebar.selectbox("⚡ Quick Presets", ["Custom Circuit", "Bell State (Entanglement)", "GHZ State (3-Qubit)"])

num_qubits = st.sidebar.slider("Number of Qubits", min_value=1, max_value=4, value=2 if preset=="Custom Circuit" else (3 if "GHZ" in preset else 2))
shots = st.sidebar.slider("Simulation Shots", min_value=100, max_value=5000, value=1000, step=100)

qc = QuantumCircuit(num_qubits, num_qubits)

if preset == "Bell State (Entanglement)" and num_qubits >= 2:
    qc.h(0)
    qc.cx(0, 1)
    st.sidebar.info("Bell State loaded: H on $q_0$, CNOT on $q_1$.")
elif preset == "GHZ State (3-Qubit)" and num_qubits >= 3:
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    st.sidebar.info("GHZ State loaded across 3 qubits.")
else:
    st.sidebar.subheader("Gate Operations")
    for i in range(num_qubits):
        gate = st.sidebar.selectbox(
            f"Qubit {i} Gate", 
            ["None", "X (Pauli-Not)", "H (Hadamard)", "Y (Pauli-Y)", "Z (Pauli-Z)", "S Gate", "T Gate"], 
            key=f"gate_{i}"
        )
        if gate == "X (Pauli-Not)":
            qc.x(i)
        elif gate == "H (Hadamard)":
            qc.h(i)
        elif gate == "Y (Pauli-Y)":
            qc.y(i)
        elif gate == "Z (Pauli-Z)":
            qc.z(i)
        elif gate == "S Gate":
            qc.s(i)
        elif gate == "T Gate":
            qc.t(i)

    if num_qubits >= 2:
        st.sidebar.subheader("Entanglement")
        add_cnot = st.sidebar.checkbox("Add CNOT (CX) Gate")
        if add_cnot:
            control = st.sidebar.selectbox("Control Qubit", range(num_qubits), key="cnot_ctrl")
            target = st.sidebar.selectbox("Target Qubit", range(num_qubits), key="cnot_tgt")
            if control != target:
                qc.cx(control, target)
            else:
                st.sidebar.warning("Control and Target must differ.")

# Statevector prep
qc_no_meas = qc.remove_final_measurements(inplace=False)
qc_no_meas.save_statevector()
qc.measure(range(num_qubits), range(num_qubits))

# Compact Two-Column Dashboard Layout
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.subheader("📐 Circuit Diagram")
    fig_circ, ax_circ = plt.subplots(figsize=(5, 2.5))
    qc.draw(output='mpl', ax=ax_circ)
    st.pyplot(fig_circ)
    
    st.subheader("🔮 Statevector Amplitudes")
    sv_simulator = AerSimulator()
    transpiled_sv = transpile(qc_no_meas, sv_simulator)
    result_sv = sv_simulator.run(transpiled_sv).result()
    statevector = result_sv.get_statevector(qc_no_meas)
    st.text(str(statevector))

with col2:
    st.subheader("📊 Measurement Probabilities")
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    job = simulator.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    
    fig_hist, ax_hist = plt.subplots(figsize=(5, 2.5))
    plot_histogram(counts, ax=ax_hist)
    st.pyplot(fig_hist)
    
    st.subheader("🌐 Bloch Sphere Projection")
    try:
        fig_bloch = plot_bloch_multivector(statevector)
        st.pyplot(fig_bloch)
    except Exception as e:
        st.info("Bloch multi-vector rendered for active states.")

st.markdown("---")
st.markdown("🚀 *Interactive Quantum Circuit Simulator | Built with Qiskit & Streamlit*")
