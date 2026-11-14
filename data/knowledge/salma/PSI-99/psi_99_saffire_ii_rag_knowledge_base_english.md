---
project_id: PSI-99
mission_name: SAFFIRE-II (Spacecraft Fire Experiment-II)
investigation_type: Microgravity Investigation
platform: Orbital Sciences Cygnus Spacecraft (post-ISS unberthing)
sponsoring_agency: NASA
nasa_center: Glenn Research Center (GRC)
start_date: 2016-09-30
end_date: 2017-04-01
principal_investigator: David L. Urban
investigator: Gary Ruff
keywords: [PSI-99, SAFFIRE-II, microgravity combustion, spacecraft fire safety, Cygnus, SIBAL, Silicone, PMMA, Nomex, flame spread, concurrent flow, opposed flow, radiative extinction, NASA-STD-6001]
---

# PSI-99 (SAFFIRE-II): Comprehensive Knowledge Base for Microgravity Fire Physics and Spacecraft Fire Safety

## 1. Project Overview: PSI-99 (SAFFIRE-II)

**Context and Identification:** Project **PSI-99**, designated as **SAFFIRE-II** (*Spacecraft Fire Experiment-II*), is a microgravity combustion investigation conducted by **NASA Glenn Research Center (GRC)** between September 30, 2016, and April 1, 2017. The Principal Investigator (PI) is **David L. Urban**, alongside Investigator **Gary Ruff**. The experiment was performed aboard an uncrewed **Orbital Sciences Cygnus** resupply vehicle after unberthing from the International Space Station (ISS).

**Scientific Objectives:**
1. Determine how rapidly a large-scale fire grows in low-gravity ($\mu\text{-g}$).
2. Investigate low-gravity flammability limits compared to those obtained in NASA’s normal-gravity ($1\text{-g}$) material flammability screening test (**NASA-STD-6001 Test #1**).

**Fundamental Hypothesis:**
Due to major differences between fire behavior in normal gravity ($1\text{-g}$) and reduced gravity ($\mu\text{-g}$), relying solely on terrestrial fire standards to design spacecraft fire safety systems introduces inherent risks and high uncertainty—especially for long-duration deep-space exploration missions with extended transit times. SAFFIRE-II addresses this knowledge gap by executing large-scale fire experiments inside an expendable spacecraft without endangering a crew.

**Experimental Apparatus:**
* **Flow Duct:** A sample card holding **9 material samples** (each measuring $5\text{ cm}$ wide by $29\text{ cm}$ long) is mounted inside the center of a large flow duct.
* **Airflow Control:** Fans located at the top of the duct and flow straighteners at the bottom draw air across the samples at controlled velocities of $20\text{ cm/s}$ (or $30\text{ cm/s}$ depending on campaign parameters), configured in either **concurrent flow** (airflow moving in the same direction as flame spread) or **opposed flow** (airflow moving opposite to flame spread).
* **Diagnostics & Instrumentation:** Two video cameras capture flame growth and morphology; thermocouples measure flow, flame, and plume temperatures; two radiometers record flame radiant heat flux; solid-state sensors monitor cabin pressure and $\text{O}_2$ and $\text{CO}_2$ mole fractions; and two anemometers track airflow velocity.

---

## 2. Summary Table of the 9 SAFFIRE-II Experiments (Cleaned Dataset)

**Data Cleaning Note:** In the original raw CSV dataset, sample IDs `2-1` through `2-9` were inadvertently auto-formatted as dates (`02-janv` to `02-sept`), and blank material cells in tests `2-6` and `2-9` represent repeat tests of the preceding row's material (SIBAL and PMMA, respectively). Furthermore, the column labeled `?-g Spread Length` physically represents the **microgravity flame spread rate ($\mu\text{-g Spread Rate}$)** in $\text{mm/s}$.

| Sample ID | Material | Thickness | Dimensions ($L \times W$) | Airflow Velocity & Direction | $\text{O}_2$ Concentration | Ignition Power & Duration | Burn Time ($\mu\text{-g}$) | Burn Length ($\mu\text{-g}$) | Flame Spread Rate ($\mu\text{-g}$) | Burn Length ($1\text{-g}$) | Flame Spread Rate ($1\text{-g}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2-1** | Silicone | $0.27\text{ mm}$ | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $\sim 21.5\%$ | $80\text{ W}$ for $9.2\text{ s}$ | Insignificant | $\sim 0\text{ cm}$ | n/a | Full ($29\text{ cm}$) | Acceleratory |
| **2-2** | Silicone | $0.61\text{ mm}$ | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $\sim 22.1\%$ | $80\text{ W}$ for $9.2\text{ s}$ | Insignificant | $\sim 0\text{ cm}$ | n/a | $7.6\text{ cm}$ | $1.2\text{ mm/s}$ |
| **2-3** | Silicone | $1.03\text{ mm}$ | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $\sim 22.1\%$ | $80\text{ W}$ for $9.2\text{ s}$ | Insignificant | $\sim 0\text{ cm}$ | n/a | $\sim 0\text{ cm}$ | n/a |
| **2-4** | Silicone | $0.37\text{ mm}$ | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Opposed) | $\sim 22.1\%$ | $80\text{ W}$ for $9.2\text{ s}$ | Insignificant | $\sim 0\text{ cm}$ | n/a | Full ($29\text{ cm}$) | $0.6\text{ mm/s}$ |
| **2-5** | SIBAL (75% Cotton / 25% Fiberglass) | $0.37\text{ mm}$ | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $\sim 22.1\%$ | $80\text{ W}$ for $9.2\text{ s}$ | $145\text{ s}$ | Full ($29\text{ cm}$) | $2.1\text{ mm/s}$ | Full ($29\text{ cm}$) | Acceleratory |
| **2-6** | SIBAL (75% Cotton / 25% Fiberglass) | $0.37\text{ mm}$ | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $\sim 22.1\%$ | $80\text{ W}$ for $9.2\text{ s}$ | $115\text{ s}$ | Full ($29\text{ cm}$) | $2.6\text{ mm/s}$ | Full ($29\text{ cm}$) | Acceleratory |
| **2-7** | PMMA + Nomex (Sequential Composite) | $0.85\text{ mm}$ (PMMA) / $0.37\text{ mm}$ (Nomex) | $5\text{ cm}$ (PMMA) + $24\text{ cm}$ (Nomex) $\times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $\sim 22.1\%$ | $80\text{ W}$ for $9.2\text{ s}$ | $140\text{ s}$ | $5\text{ cm}$ (PMMA) / $0\text{ cm}$ (Nomex) | n/a (Nomex) | $\sim 0\text{ cm}$ (Nomex) | n/a (Nomex) |
| **2-8** | PMMA (Structured) | Per configuration | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $22.1\% \to 22.0\%$ | $97\text{ W}$ for $30\text{ s}$ | $600\text{ s}$ | $\sim 10\text{ cm}$ (damage) | $0.01 \text{ to } 0.04\text{ mm/s}$ | Full ($29\text{ cm}$) | Acceleratory |
| **2-9** | PMMA (Flat) | $10\text{ mm}$ ($1\text{ cm}$) | $29\text{ cm} \times 5\text{ cm}$ | $20\text{ cm/s}$ (Concurrent) | $22.0\% \to 21.9\%$ | $97\text{ W}$ for $30\text{ s}$ | $900\text{ s}$ | $\sim 10\text{ cm}$ (damage) | $0.01 \text{ to } 0.04\text{ mm/s}$ | Full ($29\text{ cm}$) | Acceleratory |

---

## 3. Physical Mechanisms: Microgravity ($\mu\text{-g}$) vs. Normal Gravity ($1\text{-g}$)

**Absence of Buoyancy-Driven Natural Convection:**
In normal gravity ($1\text{-g}$), hot combustion gases are less dense than ambient air and rise rapidly due to buoyancy. This upward plume induces a strong natural convective draft (typically $50 \text{ to } 100\text{ cm/s}$) that continuously supplies fresh oxygen to the flame base and pushes the flame sheet tightly against the solid fuel surface during upward (concurrent) flame spread. This intense convective and radiative heat feedback produces **acceleratory flame spread** (*Acceleratory*).

In microgravity ($\mu\text{-g}$), buoyant convection is eliminated. Mass transport (oxygen supply and pyrolysis vapor dispersion) and heat transfer rely solely on:
1. **Molecular diffusion** (a slow process).
2. **Forced spacecraft ventilation** (set to a low-velocity regime of $20\text{ cm/s}$ in these tests).

**Thermodynamic and Aerodynamic Consequences in $\mu\text{-g}$:**
* **Boundary Layer Thickening:** At low forced-flow velocities ($20\text{ cm/s}$), the hydrodynamic and thermal boundary layers above the fuel surface become significantly thicker than in $1\text{-g}$. The flame stand-off distance increases, lowering the temperature gradient and reducing convective heat transfer back to the unburned solid fuel.
* **Dominance of Radiative Heat Losses:** Combustion products accumulate around the flame zone and oxygen replenishment is limited, reducing flame temperatures. Radiative heat losses from both the flame and the hot solid surface exceed the chemical heat release rate, promoting **radiative extinction** (*radiative quenching*).

---

## 4. Detailed Physical Analysis by Experiment and Material

### 4.1. Samples 2-1, 2-2, 2-3, and 2-4: Silicone Behavior
* **Experimental Data:** Silicone samples were tested at three thicknesses in concurrent flow ($0.27\text{ mm}$, $0.61\text{ mm}$, $1.03\text{ mm}$) and one thickness in opposed flow ($0.37\text{ mm}$) under a $20\text{ cm/s}$ airflow at $\sim 21.5\% \text{ to } 22.1\%\text{ O}_2$, using an ignition power of $80\text{ W}$ for $9.2\text{ s}$. In $1\text{-g}$, thin samples burned completely ($0.27\text{ mm}$ concurrent; $0.37\text{ mm}$ opposed at $0.6\text{ mm/s}$), whereas the $0.61\text{ mm}$ sample self-extinguished after $7.6\text{ cm}$ and the $1.03\text{ mm}$ sample failed to ignite. In $\mu\text{-g}$, **none of the four silicone samples sustained combustion** (insignificant burn time, $\sim 0\text{ cm}$ burn length).
* **Physical Interpretation:**
  1. *Radiative Quenching in Thin Samples:* Even for thin samples ($0.27\text{ mm}$ and $0.37\text{ mm}$) that burn completely on Earth, the absence of buoyant draft at $20\text{ cm/s}$ in $\mu\text{-g}$ starves the flame of rapid oxygen transport. Furthermore, silicone forms a surface silica ash layer that enhances radiative heat loss and insulates the underlying polymer, causing immediate extinction once the igniter turns off.
  2. *Thermal Heat-Sink Effect in Thick Samples:* For thicker samples ($0.61\text{ mm}$ and $1.03\text{ mm}$), internal heat conduction across the material thickness absorbs the $736\text{ J}$ ignition energy, preventing the surface from reaching its pyrolysis temperature.

### 4.2. Samples 2-5 and 2-6: SIBAL Composite Fabric Behavior
* **Experimental Data:** SIBAL is a composite fabric composed of $75\%$ cotton and $25\%$ fiberglass by weight ($0.37\text{ mm}$ thick). Tested twice in concurrent flow ($20\text{ cm/s}$, $22.1\%\text{ O}_2$, $80\text{ W}$ ignition for $9.2\text{ s}$), it burned across its entire $29\text{ cm}$ length in microgravity over $145\text{ s}$ (test 2-5) and $115\text{ s}$ (test 2-6), exhibiting steady spread rates of $2.1\text{ mm/s}$ and $2.6\text{ mm/s}$. In $1\text{-g}$, burning is also complete but strongly acceleratory.
* **Physical Interpretation:**
  1. *Steady-State Flame Spread Regime:* Unlike normal gravity where buoyancy accelerates flame growth exponentially, oxidizer delivery in $\mu\text{-g}$ is strictly bounded by the constant $20\text{ cm/s}$ forced ventilation. Flame length and forward heat transfer reach equilibrium, resulting in a constant, linear spread rate ($\approx 2.1 \text{ to } 2.6\text{ mm/s}$).
  2. *Structural Role of the Fiberglass Matrix:* The non-combustible fiberglass substrate preserves the flat geometry of the fabric as the cotton pyrolyzes, preventing curling or structural collapse and maintaining consistent heat transfer to the virgin fuel downstream.

### 4.3. Sample 2-7: PMMA + Nomex Assembly (Fire-Barrier Test)
* **Experimental Data:** This configuration pairs a $5\text{ cm}$ long PMMA booster ($0.85\text{ mm}$ thick) upstream of a $24\text{ cm}$ long Nomex strip ($0.37\text{ mm}$ thick) under $20\text{ cm/s}$ concurrent airflow ($22.1\%\text{ O}_2$). The PMMA burned completely ($5\text{ cm}$) over $140\text{ s}$, acting as a sustained chemical pilot flame, yet the **Nomex failed to ignite** ($0\text{ cm}$ burned in both $\mu\text{-g}$ and $1\text{-g}$).
* **Physical Interpretation:** The burning PMMA subjects the leading edge of the Nomex to a prolonged, high-intensity convective and radiative heat flux far exceeding the initial $80\text{ W}$ electrical igniter. However, Nomex (a flame-resistant meta-aramid polymer) possesses a high thermal decomposition threshold and chars without releasing sufficient flammable pyrolysis gases to sustain a gas-phase flame under these flow conditions.

### 4.4. Samples 2-8 and 2-9: Thick PMMA (Structured and Flat)
* **Experimental Data:** Samples 2-8 (structured PMMA) and 2-9 (flat PMMA, $10\text{ mm}$ / $1\text{ cm}$ thick) were exposed to elevated ignition energy ($97\text{ W}$ for $30\text{ s}$, totaling $2910\text{ J}$) in $20\text{ cm/s}$ concurrent airflow. In $1\text{-g}$, both burn completely with acceleratory flame spread. In $\mu\text{-g}$, they sustain a flame for extended durations ($600\text{ s}$ for 2-8 and $900\text{ s}$ for 2-9), but flame spread is nearly stationary ($0.01 \text{ to } 0.04\text{ mm/s}$), restricting visible surface damage to $\sim 10\text{ cm}$. A measurable drop in ambient module oxygen concentration occurs (from $22.1\%$ down to $21.9\%$).
* **Physical Interpretation:**
  1. *High Thermal Inertia of Thick Solids:* Due to its $10\text{ mm}$ thickness, flat PMMA acts as a massive heat sink. In-depth thermal conduction absorbs most of the flame's heat feedback, slowing surface heating and limiting the pyrolysis mass flux.
  2. *Anchored Flame Regime:* The methyl methacrylate vapor flux generated at the ignition region is sufficient to anchor a small, stable diffusion flame at the sample base (within the local recirculation zone), but downstream heat transfer is too weak to preheat the thick bulk material to its pyrolysis temperature. Consequently, the fire remains localized while burning persistently for 10 to 15 minutes.

---

## 5. Operational Solutions and Engineering Recommendations (Space & Earth)

Findings from the **PSI-99 (SAFFIRE-II)** investigation provide actionable engineering solutions for spacecraft fire safety architectures (ISS, Lunar Gateway, Mars transit habitats) and confined terrestrial environments (submarines, aircraft, mines):

1. **Material Qualification and Selection (Updating NASA-STD-6001 Criteria):**
   * **Validation of Nomex and Silicone:** Under nominal spacecraft cabin atmospheres ($20\text{ cm/s}$ airflow, $\sim 22\%\text{ O}_2$), silicone ($0.27\text{ mm}$ to $1.03\text{ mm}$) and Nomex (even when exposed to a sustained PMMA pilot fire) either self-extinguish or resist ignition in microgravity. Both are validated as safe materials for cabin interiors and insulation.
   * **Mitigation for Thin Cellulosic Materials:** Thin fabrics such as SIBAL burn completely in $\mu\text{-g}$ at a steady rate ($2.1\text{–}2.6\text{ mm/s}$). Their usage must be strictly controlled, flame-retarded, or isolated behind Nomex fire barriers.

2. **Active Cabin Ventilation Management (Aerodynamic Fire Suppression):**
   * In microgravity, forced airflow velocity is the primary rate-limiting control on oxygen delivery and flame cooling. Immediate **cabin ventilation shutdown** upon fire detection eliminates convective oxygen transport, driving flames (particularly slow, anchored polymer fires like thick PMMA or steady fabric fires like SIBAL) toward rapid radiative extinction.

3. **Fire Detection and Crew Response Architecture:**
   * **Early Detection of Slow, Persistent Fires:** Unlike terrestrial fires that accelerate rapidly upward, thick plastics (PMMA) in microgravity produce anchored flames with ultra-low spread rates ($0.01\text{–}0.04\text{ mm/s}$) that can burn quietly for over 15 minutes while depleting $\text{O}_2$ and generating $\text{CO}_2$ and toxic pyrolysis species. Smoke and gas sensors must be calibrated to detect low-rate, continuous emissions rather than relying solely on rapid thermal spikes.
   * **Predictable Crew Intervention Window:** Because microgravity flame spread is linear and bounded ($2.1\text{–}2.6\text{ mm/s}$ for thin fabrics, $< 0.04\text{ mm/s}$ for thick thermoplastics) rather than exponentially acceleratory, flight crews have a predictable timeframe to deploy fire extinguishers once early detection is triggered.