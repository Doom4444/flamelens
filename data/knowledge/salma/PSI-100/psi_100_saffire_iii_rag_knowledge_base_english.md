## project_id: PSI-100
mission_name: SAFFIRE-III (Spacecraft Fire Experiment-III)
investigation_type: Microgravity Investigation
platform: Orbital Sciences Cygnus Spacecraft (post-ISS unberthing)
sponsoring_agency: NASA
nasa_center: Glenn Research Center (GRC)
start_date: 2017-04-18
principal_investigator: David L. Urban
keywords: [PSI-100, SAFFIRE-III, microgravity combustion, spacecraft fire safety, Cygnus, SIBAL, large-scale fire, 30 cm/s, opposed flow, 94 cm x 40 cm, forced convection, NASA-STD-6001]

# PSI-100 (SAFFIRE-III): Comprehensive Knowledge Base for Large-Scale Microgravity Fire Physics

## 1. Project Overview: PSI-100 (SAFFIRE-III)

**Context and Identification:** Project **PSI-100**, designated as **SAFFIRE-III** (*Spacecraft Fire Experiment-III*), is a large-scale microgravity combustion investigation conducted by the **NASA Glenn Research Center (GRC)** starting April 18, 2017, under the direction of Principal Investigator (PI) **David L. Urban**. The experiment was performed aboard an uncrewed **Orbital Sciences Cygnus** resupply vehicle after unberthing from the International Space Station (ISS).

**Scientific Objectives:**

1. Determine the growth rate and propagation behavior of a large-scale fire ($94\text{ cm} \times 40\text{ cm}$) in low-gravity ($\mu\text{-g}$) under a $30\text{ cm/s}$ forced airflow.

2. Evaluate microgravity flammability limits compared to results obtained using NASA’s normal-gravity ($1\text{-g}$) material flammability screening test, **NASA-STD-6001 Test #1**.

**Fundamental Hypothesis:**
Due to significant differences in fire behavior between normal gravity ($1\text{-g}$) and reduced gravity ($\mu\text{-g}$), relying solely on terrestrial standards to design spacecraft fire safety systems introduces inherent risks and critical uncertainties, particularly for long-duration exploration missions. SAFFIRE-III enables the study of a large-scale fire inside an expendable spacecraft without endangering a crew.

**Experimental Apparatus:**

* **Large-Scale Sample:** Unlike the nine smaller samples in SAFFIRE-II ($29\text{ cm} \times 5\text{ cm}$), SAFFIRE-III utilizes a **single large sample** measuring $94\text{ cm}$ long by $40\text{ cm}$ wide made of **SIBAL** composite fabric ($75\%$ cotton / $25\%$ fiberglass by weight).

* **Aerodynamic Control:** The flow duct imposes a forced airflow of $30\text{ cm/s}$ (compared to $20\text{ cm/s}$ in SAFFIRE-I) in an **opposed flow** configuration (airflow moving opposite to the direction of flame propagation).

* **Instrumentation:** Two video cameras record flame propagation; thermocouples measure flow, flame, and plume temperatures; two radiometers record thermal radiation; solid-state sensors track pressure and $\text{O}_2$ and $\text{CO}_2$ mole fractions; and two anemometers monitor airflow velocity.

## 2. SAFFIRE-III Experimental Data (Cleaned Dataset)

**Data Cleaning Note:** In the raw CSV file, sample ID `3-1` was automatically formatted as a date (`03-janv`), and the column labeled `?-g Spread Length` physically represents the **microgravity flame spread rate (**$\mu\text{-g Spread Rate}$**)** in $\text{mm/s}$.

| Parameter | SAFFIRE-III Experimental Value (Test 3-1) | Unit / Details |
| :--- | :--- | :--- |
| **Sample ID** | **3-1** | Single large-scale sample |
| **Material** | **SIBAL** | Composite: $75\%$ Cotton / $25\%$ Fiberglass |
| **Thickness** | $0.37\text{ mm}$ | Thermally thin fabric |
| **Dimensions ($L \times W$)** | $94\text{ cm} \times 40\text{ cm}$ | Total surface area: $0.376\text{ m}^2$ ($3760\text{ cm}^2$) |
| **Airflow Velocity** | $30\text{ cm/s}$ | $50\%$ increase compared to SAFFIRE-I ($20\text{ cm/s}$) |
| **Airflow Direction** | **Opposed Flow** | Fresh air flowing directly toward the flame leading edge |
| **Initial $\text{O}_2$ Concentration** | $21.5\%$ | Nominal spacecraft cabin-type atmosphere |
| **Ignition Power & Duration** | $80\text{ W}$ for $8\text{ s}$ | Total ignition energy: $640\text{ J}$ |
| **Burn Time ($\mu\text{-g}$)** | $570\text{ s}$ ($9\text{ min } 30\text{ s}$) | Sustained and complete combustion across the entire length |
| **Burn Length ($\mu\text{-g}$)** | **Full ($94\text{ cm}$)** | Complete consumption of cotton across the $94\text{ cm}$ length |
| **Flame Spread Rate ($\mu\text{-g}$)** | $1.7\text{ mm/s}$ | Steady, linear propagation ($940\text{ mm} / 570\text{ s} \approx 1.65\text{ mm/s}$) |
| **Burn Length ($1\text{-g}$)** | **Full ($94\text{ cm}$)** | Normal gravity baseline reference |
| **Flame Spread Rate ($1\text{-g}$)** | $1.8\text{ mm/s}$ | Nearly identical velocity to the microgravity observation |

## 3. In-Depth Physical Interpretation: Test 3-1 Analysis

### 3.1. Remarkable Equivalence Between Microgravity ($1.7\text{ mm/s}$) and Normal Gravity ($1.8\text{ mm/s}$)

The major physical finding of Test **3-1** is the near-equality of opposed-flow spread rates at $30\text{ cm/s}$:

* In microgravity ($\mu\text{-g}$): $1.7\text{ mm/s}$ (complete consumption of $94\text{ cm}$ in $570\text{ s}$).

* In normal gravity ($1\text{-g}$): $1.8\text{ mm/s}$ (complete consumption of $94\text{ cm}$).

**Physical Explanation:**
Unlike concurrent flow, where buoyancy on Earth induces exponential flame acceleration (as observed with SIBAL in SAFFIRE-II), **opposed-flow flame spread** is governed by the thermal balance at the flame's leading edge.

1. **Effect of the $30\text{ cm/s}$ Airflow:** At this forced flow velocity ($30\text{ cm/s}$), the convective oxygen supply to the flame leading edge in microgravity matches or approximates the mixed-convection draft induced on Earth.

2. **Solid-Dominated Heat Transfer:** In opposed flow, incoming fresh air blows against and cools the unburned virgin fabric ahead of the flame. The heat required to preheat the cotton to its pyrolysis temperature is transferred primarily via **thermal conduction through the thin fabric thickness ($0.37\text{ mm}$)** and short-range radiation near the flame front. Because this mechanism is largely gravity-independent once adequate oxygen is supplied ($30\text{ cm/s}$, $21.5\%\text{ O}_2$), the $\mu\text{-g}$ spread rate ($1.7\text{ mm/s}$) closely tracks the $1\text{-g}$ rate ($1.8\text{ mm/s}$).

### 3.2. Impact of Large Scale ($94\text{ cm} \times 40\text{ cm}$) and Duration ($570\text{ s}$)

* **Steady-State Regime over Long Distances:** Across nearly a meter of length ($94\text{ cm}$) and $40\text{ cm}$ of width, the flame maintains a constant spread rate of $1.7\text{ mm/s}$ for nearly **10 minutes ($570\text{ s}$)** without extinguishing or accelerating.

* **Width Effect ($40\text{ cm}$):** A $40\text{ cm}$ width eliminates edge heat losses that typically distort small laboratory samples ($5\text{ cm}$ wide). The flame front is two-dimensional and highly representative of a real wall or fabric lining fire in a spacecraft module.

* **Role of the Fiberglass Matrix:** The $25\%$ non-combustible fiberglass substrate preserves the flat geometry of the fabric across the entire $0.376\text{ m}^2$ surface after the $75\%$ cotton pyrolyzes, ensuring stable, laminar aerodynamic flow throughout the $570\text{ s}$ duration.

### 3.3. Physical Comparison: Opposed Flow (SAFFIRE-III) vs. Concurrent Flow (SAFFIRE-II)

Combining data from **PSI-100 (SAFFIRE-III)** and **PSI-99 (SAFFIRE-II)** on the same SIBAL material ($0.37\text{ mm}$):

* **In concurrent flow at $20\text{ cm/s}$ (SAFFIRE-II, Tests 2-5 & 2-6):** The $\mu\text{-g}$ spread rate is $2.1 \text{ to } 2.6\text{ mm/s}$, as hot gases are blown forward to preheat the virgin fabric.

* **In opposed flow at $30\text{ cm/s}$ (SAFFIRE-III, Test 3-1):** Although airflow velocity is $50\%$ higher ($30\text{ cm/s}$), the spread rate is slower ($1.7\text{ mm/s}$) because incoming airflow pushes hot gases backward over already burned material while cooling the unburned fuel ahead of the flame.

## 4. Operational Solutions and Engineering Recommendations

Quantitative results from **PSI-100 (SAFFIRE-III) Test 3-1** provide direct engineering solutions for fire risk mitigation in spacecraft and confined environments:

1. **Validity and Limits of Terrestrial Testing (NASA-STD-6001) in Opposed Flow:**

   * For thin materials under moderate ventilation speeds ($\sim 30\text{ cm/s}$), opposed-flow microgravity spread rates ($1.7\text{ mm/s}$) closely match terrestrial measurements ($1.8\text{ mm/s}$). Terrestrial opposed-flow models can therefore be reliably adapted for space applications provided forced ventilation velocities are known and controlled.

2. **Ventilation Control Strategy During a Fire Emergency:**

   * **Never increase ventilation to "clear smoke" during an active fire:** Maintaining a $30\text{ cm/s}$ airflow continuously supplies oxygen to the flame, allowing it to burn nearly $1\text{ meter}$ of material over $9.5\text{ minutes}$ at rates comparable to Earth.

   * **Immediate Ventilation Shutdown:** Shutting down forced convection eliminates oxygen delivery to the flame front, disrupting the leading-edge thermal balance and triggering rapid radiative extinction.

3. **Sizing Large-Scale Detection and Suppression Systems:**

   * A fire on a wide surface ($40\text{ cm}$) sustains a uniform flame front for nearly 10 minutes ($570\text{ s}$), continuously releasing significant heat, $\text{CO}_2$, and smoke while depleting ambient $\text{O}_2$. Environmental Control and Life Support Systems (ECLSS) must integrate smoke detection with automatic compartment isolation and ventilation cutoff to prevent large-scale fire propagation.