import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector

st.set_page_config(
    page_title="QuantumLab — Interactive Simulator", 
    page_icon="⚛️", 
    layout="wide"
)

# Custom CSS for perfect single-screen layout and padding
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        h2 { font-size: 1.3rem !important; margin-bottom: 5px !important; }
        h4 { font-size: 0.95rem !important; margin-top: 5px !important; margin-bottom: 3px !important; }
        p { font-size: 0.8rem !important; margin-bottom: 3px !important; }
    </style>
""", unsafe_allow_html=True)

# Visible Main Title
st.markdown("## ⚛️ QuantumLab — Interactive Quantum Circuit Simulator")

st.sidebar.header("🔧 Circuit Settings")
preset = st.sidebar.selectbox("⚡ Quick Presets", ["Custom Circuit", "Bell State", "GHZ State (3-Qubit)"])
num_qubits = st.sidebar.slider("Number of Qubits", min_value=1, max_value=4, value=2 if preset=="Custom Circuit" else (3 if "GHZ" in preset else 2))
shots = st.sidebar.slider("Simulation Shots", min_value=100, max_value=5000, value=1000, step=100)

qc = QuantumCircuit(num_qubits, num_qubits)

if preset == "Bell State" and num_qubits >= 2:
    qc.h(0)
    qc.cx(0, 1)
elif preset == "GHZ State (3-Qubit)" and num_qubits >= 3:
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
else:
    for i in range(num_qubits):
        gate = st.sidebar.selectbox(f"Qubit {i} Gate", ["None", "X", "H", "Y", "Z", "S", "T"], key=f"gate_{i}")
        if gate == "X": qc.x(i)
        elif gate == "H": qc.h(i)
        elif gate == "Y": qc.y(i)
        elif gate == "Z": qc.z(i)
        elif gate == "S": qc.s(i)
        elif gate == "T": qc.t(i)

    if num_qubits >= 2:
        add_cnot = st.sidebar.checkbox("Add CNOT (CX)")
        if add_cnot:
            control = st.sidebar.selectbox("Control", range(num_qubits), key="cnot_ctrl")
            target = st.sidebar.selectbox("Target", range(num_qubits), key="cnot_tgt")
            if control != target: qc.cx(control, target)

# Statevector prep
qc_no_meas = qc.remove_final_measurements(inplace=False)
qc_no_meas.save_statevector()
qc.measure(range(num_qubits), range(num_qubits))

# Balanced 2-Column Dashboard Layout
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("#### 📐 Circuit Diagram")
    fig_circ, ax_circ = plt.subplots(figsize=(3.2, 1.3))
    qc.draw(output='mpl', ax=ax_circ)
    st.pyplot(fig_circ, use_container_width=False)
    
    st.markdown("#### 🔮 Statevector Amplitudes")
    sv_simulator = AerSimulator()
    transpiled_sv = transpile(qc_no_meas, sv_simulator)
    result_sv = sv_simulator.run(transpiled_sv).result()
    statevector = result_sv.get_statevector(qc_no_meas)
    st.text(str(statevector))

with col2:
    st.markdown("#### 📊 Measurement Probabilities")
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    job = simulator.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)
    
    fig_hist, ax_hist = plt.subplots(figsize=(3.2, 1.3))
    plot_histogram(counts, ax=ax_hist)
    st.pyplot(fig_hist, use_container_width=False)
    
    st.markdown("#### 🌐 Bloch Sphere Projection")
    try:
        fig_bloch = plot_bloch_multivector(statevector)
        # Resize bloch figure slightly to match compact layout
        fig_bloch.set_size_inches(3.2, 1.3)
        st.pyplot(fig_bloch, use_container_width=False)
    except Exception:
        st.info("Bloch multi-vector rendered.")
