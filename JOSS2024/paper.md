---
title: "Photon-Weave"
tags:
 - Python
 - Quantum Optics Simulation
 - Quantum
  
authors:
 - name: Simon Sekavčnik
    orcid: 0000-0002-1370-9751
    affiliation: 1
 - name: Kareem El-Safty
    orcid: 0000-0001-8740-0637
    affiliation: 1
 - name: Janis Nötzel
    orcid: 0000-0003-0091-3072
    affiliation: 1
affiliations:
  - name: Technical University of Munich, Theoretical Quantum System Design, Munich, Germany
    index: 1
date: 15.10.2024
bibliography: paper.bib
---

# Summary
Photon Weave is a quantum systems simulator designed to offer intuitive abstractions for simulating photonic quantum systems and their interactions in Fock space along with arbitrary custom Hilbert space. The simulator focuses on simplifying complex quantum state representations, such as photon pulses (envelopes) with polarization, making it more approachable for specialized quantum simulations. While general-purpose quantum simulation libraries such as QuTiP [@johansson2012qutip]provide robust tools for quantum state manipulations, they often require meticulous organization of operations for larger simulations, introducing complexity that can be automated. Photon Weave addresses this by abstracting such details, streamlining the simulation process, and allowing quantum systems to interact naturally as the simulation progresses.

In contracts to frameworks such as Qiskit [@wille2019ibm], which are primarily designed for qubit-based computations, Photon Weave excels at simulating continuous-variable quantum systems, particularly photons, as well as custom quantum states that can interact dynamically. Furthermore, Photon Weave offers a balance of flexibility and automation by deferring the joining of quantum spaces until it is necessary, enhancing computational efficiency. The simulator supports both CPU and GPU execution, ensuring scalability and performance for large-scale simulations. This is achieved by using the jax [@jax2018github] library.

