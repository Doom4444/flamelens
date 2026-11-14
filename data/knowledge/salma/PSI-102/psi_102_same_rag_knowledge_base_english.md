## project_id: PSI-102
mission_name: SAME (Smoke Aerosol Measurement Experiment)
investigation_type: Microgravity Investigation
platform: International Space Station (ISS) - Microgravity Science Glovebox (MSG)
sponsoring_agency: National Aeronautics and Space Administration (NASA)
nasa_center: Glenn Research Center (GRC)
start_date: 2001-03-02
end_date: 2008-02-28
principal_investigator: David L. Urban
co_investigators: George Mulholland, Thomas Cleary, Jiann Yang
project_scientist: Claire Fortenberry
keywords: \[PSI-102, SAME, Smoke Aerosol Measurement Experiment, microgravity, smoke particulate, aerosol growth, droplet size distribution, TEM analysis, thermophoretic sampling, spacecraft fire detection, Pyrell, DBP, nucleation, condensation, coagulation, ionization detector, optical detector\]

# PSI-102 (SAME): Comprehensive Knowledge Base for Microgravity Smoke Aerosol Growth and Spacecraft Fire Detection

## 1. Project Overview: PSI-102 (SAME)

**Context and Identification:** Project **PSI-102**, designated as **SAME** (*Smoke Aerosol Measurement Experiment*), is a microgravity combustion and aerosol investigation conducted by the **NASA Glenn Research Center (GRC)** between March 2, 2001, and February 28, 2008. The Principal Investigator (PI) is **David L. Urban**, supported by co-investigators from the University of Maryland and the National Institute of Standards and Technology (NIST). The experiments were performed aboard the International Space Station (ISS) inside the Microgravity Science Glovebox (MSG).

**Scientific Objectives:**

1. Quantify the particle sizes and droplet size distributions achieved by liquid smoke aerosols generated from overheated spacecraft materials in a low-gravity ($\mu\text{-g}$) environment.

2. Relate smoke droplet size distribution and number density to smoke generation rates, thermodynamic properties of pyrolysis vapors, and the local flow environment.

3. Develop and validate a predictive numerical code for smoke droplet growth as a function of fuel pyrolysis rate, vapor thermodynamics, and microgravity flow conditions.

4. Evaluate the response adequacy of existing spacecraft smoke detectors (ionization and optical detectors) when exposed to reduced-gravity smokes.

**Fundamental Hypotheses:**
The investigation was motivated by three core hypotheses regarding smoke formation in microgravity:
1. In a $\mu\text{-g}$ environment, the absence of strong buoyancy-induced flows alters time-temperature histories and particle trajectories.
2. Smoke particle growth from a pyrolyzing or smoldering source—driven by nucleation, condensation, and coagulation—leads to substantially larger particles (liquid aerosol droplets) compared to those produced in normal gravity ($1\text{-g}$). This is favored by higher vapor concentrations and longer residence times near the source due to reduced velocities and mixing.
3. The resulting shift toward larger particle sizes and lower number densities (for the same total smoke mass) directly impairs the response characteristics of standard spacecraft smoke detectors, potentially resulting in failure to alarm when exposed to microgravity smoke.

**Experimental Apparatus and Approach:**

* **Hardware Configuration:** Crew members installed near-field hardware in the MSG glovebox, attached the Far Field Box, and positioned video cameras.

* **Combustion & Sampling Sequence:** Operators ran self-diagnostics on two smoke detectors, activated video cameras, energized the material igniter for a predefined duration ($15 \text{ to } 60\text{ seconds}$), and initiated thermophoretic soot/aerosol samplers. Typical combustion events lasted approximately 2 minutes.

* **Post-Flight Analysis:** Particulates collected on thermophoretic probes were analyzed post-flight using a Transmission Electron Microscope (TEM) to determine primary and aggregate particle dimensions. Sample mass loss was measured via post-flight weighing, and digital video records were analyzed to evaluate smoke detector responses. Corresponding $1\text{-g}$ tests were conducted under controlled conditions to match flight mass loss rates.

## 2. Summary Table of SAME Experimental Matrix & Parameters (Cleaned Dataset)

| Parameter / Field | Experimental Specification (SAME / PSI-102) | Details & Operational Range | 
| ----- | ----- | ----- | 
| **Investigation Platform** | International Space Station (ISS) | Microgravity Science Glovebox (MSG) | 
| **Test Materials** | Overheated spacecraft materials (e.g., Dibutyl Phthalate - DBP, Pyrell foam) | Representative electrical/thermal insulation and fire-retardant polymers | 
| **Ignition Duration** | $15\text{ s}$ to $60\text{ s}$ | Controlled thermal degradation of samples | 
| **Event Duration** | $\sim 2\text{ minutes}$ per combustion test | Standard duration for pyrolysis and sampling | 
| **Sampling Technique** | Thermophoretic Probes | Captures aerosol particles for post-flight TEM analysis | 
| **Diagnostics** | Near-field & Far-field detectors, video cameras | Ionization detectors, optical detectors (DustTrak/P-Trak counterparts), digital imaging | 
| **Post-Flight Analysis** | Transmission Electron Microscopy (TEM) | Measurement of primary particle and aggregate dimensions, droplet size distribution | 
| **Key Measured Variables** | Mass loss, particle size, number density, detector response | Correlates pyrolysis rate and flow environment with aerosol microphysics | 

## 3. In-Depth Physical Interpretation: Smoke Aerosol Dynamics in Microgravity

### 3.1. Absence of Buoyancy and Enhanced Residence Time

On Earth ($1\text{-g}$), strong buoyancy-induced convective currents rapidly transport pyrolysis vapors away from the heating source, diluting the vapor cloud and cooling precursors quickly. 

In microgravity ($\mu\text{-g}$):
* **Stagnant/Low-Velocity Flow:** The complete suppression of buoyancy eliminates natural draft. Pyrolysis vapors linger directly above the heated source.
* **Elevated Vapor Concentration & Residence Time:** Reduced velocities and minimal mixing trap smoke precursors near the source. This extended residence time drastically increases the probability of molecular collision and agglomeration.

### 3.2. Nucleation, Condensation, and Coagulation Mechanics

The microgravity environment fundamentally alters aerosol microphysics:
* **Enhanced Droplet Growth:** Higher local vapor saturation ratios promote rapid homogeneous and heterogeneous nucleation, followed by heavy condensation onto existing nuclei and rapid coagulation.
* **Shift in Particle Size Distribution:** Liquid aerosol smokes produced in microgravity exhibit **substantially larger droplet sizes** and a corresponding **lower particle number density** for the exact same mass of generated smoke compared to normal gravity.

### 3.3. Failure Mechanism of Spacecraft Smoke Detectors

* **Ionization Detectors:** These detectors rely on small, numerous ultrafine particles to disrupt an ion current. Large aerosol droplets present a massive total surface area but very low particle number density, resulting in insufficient ion capture and a delayed or missing alarm.
* **Optical (Light-Scattering) Detectors:** Scattering efficiency depends heavily on particle size parameters. While larger droplets scatter light effectively, their shifted size distribution outside the optimal detection window can trick standard algorithms, validating NASA's concern that existing fire detection technologies might fail during early-stage microgravity fires.

## 4. Operational Solutions and Engineering Recommendations

Findings from **PSI-102 (SAME)** and its reflight **PSI-101 (SAME-R)** establish critical engineering benchmarks for spacecraft safety:

1. **New Baseline for Fire Prevention, Detection, and Suppression (FPDS):**
   * SAME provided the definitive microgravity baseline data needed to re-evaluate existing sensor technology and formulate advanced, multi-criteria smoke detectors capable of detecting large-droplet aerosols in reduced gravity.

2. **Advanced Spacecraft Fire Detection Technologies:**
   * Insights into droplet size distributions led to the development of robust detection algorithms and hardware (such as modified Condensation Particle Counters / TSI P-Trak validated in DAFT/DAFT-2) for long-duration crewed exploration missions (ISS and future deep-space habitats).

3. **Terrestrial Applications in Extreme Environments:**
   * Accurate smoke detection in closed, confined environments with atypical ventilation—such as nuclear submarines, underwater laboratories, and high-altitude aircraft—benefits directly from SAME's aerosol growth models, saving lives in extreme Earth environments.