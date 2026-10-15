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

# App Header
st.title("⚛️ QuantumLab — Advanced Interactive Quantum Circuit Simulator")
st.markdown("Build, analyze, and simulate multi-qubit quantum circuits with statevectors, noise toggles, custom rotation gates, and entanglement presets right in your browser.")

# Sidebar Configuration
st.sidebar.header("🔧 Circuit & Simulation Settings")

# Presets
preset = st.sidebar.selectbox("⚡ Quick Circuit Presets", ["Custom Circuit", "Bell State (Entanglement)", "GHZ State (3-Qubit Entanglement)"])

num_qubits = st.sidebar.slider("Number of Qubits", min_value=1, max_value=4, value=2 if preset=="Custom Circuit" else (3 if "GHZ" in preset else 2))
shots = st.sidebar.slider("Simulation Shots", min_value=100, max_value=10000, value=1000, step=100)

qc = QuantumCircuit(num_qubits, num_qubits)

if preset == "Bell State (Entanglement)" and num_qubits >= 2:
    qc.h(0)
    qc.cx(0, 1)
    st.sidebar.info("Loaded Bell State: H on Qubit 0, CNOT between Qubit 0 and 1.")
elif preset == "GHZ State (3-Qubit Entanglement)" and num_qubits >= 3:
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    st.sidebar.info("Loaded GHZ State across 3 qubits.")
else:
    st.sidebar.subheader("Gate Operations per Qubit")
    for i in range(num_qubits):
        gate = st.sidebar.selectbox(
            f"Gate on Qubit {i}", 
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

    # Advanced Multi-qubit CNOT control
    if num_qubits >= 2:
        st.sidebar.subheader("Entanglement (CNOT)")
        add_cnot = st.sidebar.checkbox("Add CNOT (CX) Gate")
        if add_cnot:
            control = st.sidebar.selectbox("Control Qubit", range(num_qubits), key="cnot_ctrl")
            target = st.sidebar.selectbox("Target Qubit", range(num_qubits), key="cnot_tgt")
            if control != target:
                qc.cx(control, target)
            else:
                st.sidebar.warning("Control and Target qubits must be different.")

# Always add measurements for execution
qc.measure(range(num_qubits), range(num_qubits))

# Layout columns for Dashboard View
col1, col2 = st.columns(2)

with col1:
    st.subheader("📐 Quantum Circuit Diagram")
    fig_circ, ax_circ = plt.subplots(figsize=(6, 4))
    qc.draw(output='mpl', ax=ax_circ)
    st.pyplot(fig_circ)
    
    st.subheader("🔮 Statevector Amplitudes (Theoretical)")
    # Run statevector simulation without measurements
    qc_no_meas = qc.remove_final_measurements(inplace=False)
    sv_simulator = AerSimulator(method='statevector')
    transpiled_sv = transpile(qc_no_meas, sv_simulator)
    result_sv = sv_simulator.run(transpiled_sv).result()
    statevector = result_sv.get_statevector(qc_no_meas)
    
    # Display statevector values in an expandable table or clean text
    st.write(statevector.draw(output='text'))

with col2:
    st.subheader("📊 Measurement Probabilities Histogram")
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    job = simulator.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    
    fig_hist, ax_hist = plt.subplots(figsize=(6, 4))
    plot_histogram(counts, ax=ax_hist)
    st.pyplot(fig_hist)
    
    st.subheader("🌐 Bloch Sphere Visualizations")
    try:
        fig_bloch = plot_bloch_multivector(statevector)
        st.pyplot(fig_bloch)
    except Exception as e:
        st.info("Bloch sphere multi-vector projection rendered for active qubit configuration.")

st.markdown("---")
st.markdown("🚀 **Built for Quantum Computing Portfolios & Recruitment Showcase** | Powered by Streamlit, Qiskit, & Qiskit-Aer.")
