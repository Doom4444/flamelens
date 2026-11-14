---
id: PSI-26
title: "BASS (Burning and Suppression of Solids)"
type: Microgravity Investigation
platform: International Space Station (ISS), Microgravity Science Glovebox (MSG)
sponsor: NASA (Glenn Research Center)
period: 10-01-2009 to 06-30-2013
pi: Paul Ferkul (NASA GRC)
co_investigators: [Fumiaki Takahashi (Case Western Reserve University), James T'ien (Case Western Reserve University)]
project_scientist: Sandra L. Olson (NASA GRC)
topic: Solid-fuel flammability, flame spread, wake flames, flame suppression by inert gas, microgravity
related_psi: [PSI-25 (BASS-II), PSI-62 (modeling with BASS benchmarks)]
related_file: PSI-26_experimental_table.md
keywords: [BASS, solid fuel, flame spread, concurrent flow, opposed flow, wake flame, microgravity, buoyancy, NASA-STD-6001 Test 1, cone calorimeter, nitrogen suppression, extinguishment, flame radiation, thermally thick fuel, cotton-fiberglass fabric, Nomex, Ultem, PMMA, sphere, cylinder, candle, spacecraft fire safety, ISS, Microgravity Science Glovebox]
provenance_legend: "[PSI] = stated in the PSI-26 record (or in the PSI record named next to it). [TABLE] = taken from the BASS test log supplied for PSI-26. [PHYS] = standard physics added to explain what the record says; it is not a result of PSI-26. [N/A] = not given in any source."
---

# PSI-26: Physics analysis

## PSI-26 | 0. Identification
PSI-26 is BASS (Burning and Suppression of Solids), a microgravity investigation on the ISS in the Microgravity Science Glovebox, from 10-01-2009 to 06-30-2013. Principal investigator Paul Ferkul (NASA GRC). Co-investigators Fumiaki Takahashi and James T'ien (Case Western Reserve University). Project scientist Sandra L. Olson (NASA GRC). Companion file: `PSI-26_experimental_table.md` (test log, 122 rows). Later investigation: PSI-25 (BASS-II).
Keywords: BASS, PSI-26, solid fuel flammability, flame spread, concurrent flow, opposed flow, wake flame, microgravity, buoyancy, NASA-STD-6001 Test 1, cone calorimeter, nitrogen suppression, extinguishment, flame radiation, cotton-fiberglass fabric, Nomex, Ultem, PMMA, sphere, cylinder, candle, spacecraft fire safety.
Mots-clés: combustion de solides en microgravité, propagation de flamme, écoulement concurrent, écoulement opposé, flamme de sillage, suppression par azote, extinction, sécurité incendie des engins spatiaux.

## PSI-26 | 1. Summary
- BASS studied how solid fuels burn in microgravity on the ISS, inside the Microgravity Science Glovebox. [PSI]
- Two goals: (1) link the normal-gravity NASA-STD-6001 Test #1 screening method and ground-based microgravity tests to real material flammability in microgravity; (2) assess how well an inert gaseous extinguishing agent (similar to that used on ISS) puts out flames over different materials, geometries, preheating, and flow. [PSI]
- Core hypothesis: with adequate ventilation, a material burns as well as, or better than, the same material in normal gravity at identical pressure, oxygen concentration, and temperature. [PSI]
- [N/A] PSI-26 reports no measured results (no spread rates, flame sizes, or extinction limits). The test log supplied for PSI-26 lists which tests were run and when, with no outcomes. [TABLE]

## PSI-26 | 2. Physical question
Do materials selected on the basis of a 1g test (NASA-STD-6001 Test 1, which ranks materials by 1g behavior without considering low-gravity effects) behave the same way in microgravity? The record says this needs flames burning for longer times than ground-based microgravity facilities give, with practical, realistic (thicker) fuels in typical geometries, including wake flames. [PSI]

## PSI-26 | 3. Experimental set-up
- Fuel samples: custom fabric of 75% cotton and 25% fiberglass (by mass); Nomex fabric; Ultem. Other shapes used: spheres and cylinders. [PSI]
- Ignition: Kanthal wire (29-gage) igniter at one end of the fabric. [PSI]
- Flow: variable-speed fan, airflow up to 40 cm/s, directed along the fuel surface in the concurrent or the opposed direction. [PSI]
- Flow duct: small duct with a 76 mm x 76 mm cross section for the fabric samples. [PSI]
- Observations: flames seen in top and edge profiles. Data collected on flame size, shape, color, spread rate, and potential flame quenching. [PSI]
- Wake flames are included: flames with the characteristics of a fire burning behind another object, for example in a tight area that is not easily accessible. [PSI]

## PSI-26 | 4. Physical explanation
This section explains the physics behind what the record says. Statements tagged [PHYS] are standard combustion physics, not PSI-26 results.

### 4.1 Why microgravity changes the flame
- [PHYS] On Earth, hot combustion gases are lighter than the surrounding air and rise. This buoyancy creates its own flow around any flame. In microgravity this flow disappears. The flow around the flame is then the imposed flow (here the fan, up to 40 cm/s) plus the flow produced by the flame itself (gas expansion and fuel vapor leaving the surface).
- [PSI, from PSI-25] In outer space, fuels burn as oval balls rather than with an upward-pointed cone flame as on Earth.
- [PSI] The 1g upward-burning test (Test 1) is considered the worst-case geometry for flammability on Earth, "however, it may not be conservative for flammability in space". This is stated in the PSI-25 record (the BASS-II description), and it is the same hypothesis as in PSI-26.

### 4.2 Why "adequate ventilation" matters in the hypothesis
- [PSI] The hypothesis is conditional: with adequate ventilation, the material burns as well or better in microgravity.
- [PHYS] A flame needs oxygen to be delivered to it. In 1g the buoyant flow supplies air on its own. In microgravity only the forced flow supplies it. So when the forced flow is adequate, oxygen supply no longer limits the flame, and the burning depends on the heat the flame sends back to the fuel. When the flow is not adequate, the flame can weaken or go out. The record mentions "potential flame quenching" as one of the things observed. [PSI]
- [N/A] The record does not give the flow speeds at which burning improved, weakened, or quenched.

### 4.3 Why thick fuels need long microgravity time
- [PSI] Testing the hypothesis with any but the thinnest materials requires extended microgravity time, longer than drop towers or parabolic aircraft provide.
- [PHYS] A thermally thick solid has to heat up through its thickness before the burning reaches steady state. The time for heat to diffuse through a thickness d scales as d^2 / alpha_s, with alpha_s the thermal diffusivity of the solid. Thicker fuel means a much longer time scale (it grows with the square of the thickness). This is why short-duration facilities only suit thin fuels.
- [N/A] The record gives no drop-tower or aircraft durations, and no sample thicknesses.

### 4.4 Concurrent vs opposed flow
Definitions from the record: concurrent flow = the air flows in the same direction as the flame spread; opposed flow = the air flows in the direction opposite to the flame spread. [PSI]

| Aspect | Opposed flow | Concurrent flow |
|---|---|---|
| Flow direction vs spread | Against the spread [PSI] | With the spread [PSI] |
| Where fresh oxygen arrives | [PHYS] Reaches the flame front first, from the unburned side | [PHYS] The flame is carried downstream, over the fuel ahead of it |
| Heat to the unburned fuel | [PHYS] Mainly from the flame edge by heat transfer against the flow | [PHYS] The flame lies over unburned fuel, so the fuel ahead is exposed to the flame and can be preheated |
| Measured in BASS | Flame appearance, size, spread rate, quenching [PSI] | Same quantities [PSI] |
| Results | [N/A] | [N/A] |

- [TABLE] In the test log only 3 rows carry the word "opposed" (tests 5b, 72, 73). The other rows do not state the flow direction.

### 4.5 Why flame radiation is singled out
- [PSI] A critical element of the understanding is the radiative heat emission from the flame. These results feed first-order models and predictions of heat release in spacecraft fires. They also extend heat release data from tests such as the NASA cone calorimeter test (NASA-STD-6001 Test 2) to a performance-based material selection process.
- [PHYS] Radiation is one of the heat paths between flame and fuel and between flame and surroundings. In a slow microgravity flow it can matter more than in a buoyant flow, because the flame is bigger and slower-moving. The record does not give measured radiative values. [N/A]

### 4.6 Suppression by inert gas (nitrogen)
- [PSI] Objective 2: assess an inert gaseous extinguishing agent (similar to that used on ISS) over different materials, geometries, preheating, and flow. Using nitrogen as a flame suppressant in microgravity gives a direct link to current and planned extinguishment techniques.
- [PHYS] An inert gas such as nitrogen dilutes the oxygen near the flame. Less oxygen lowers the reaction rate and the flame temperature, and below some oxygen level the flame cannot be sustained.
- [N/A] The record gives no agent concentrations and no extinction results.

### 4.7 Wake flames
- [PSI] Wake flames have characteristics of a fire burning behind another object, for example in a tight area that is not easily accessible.
- [PHYS] Behind an obstacle the flow is disturbed and slower, so the flame sits in a different oxygen and heat environment than a flame in the free stream.
- [TABLE] 16 rows are labeled "wake": candles (Japan wax, paraffin) and spheres of 1 cm and 2 cm. Three sphere rows are labeled "wake ign". The log does not say what "ign" stands for.

## PSI-26 | 5. Results
- [N/A] No spread rates, flame sizes, quenching conditions, or extinction limits appear in the PSI-26 record.
- [N/A] No outcome columns appear in the supplied test log.
- [PSI] The stated outputs are: guidance for ground-based microgravity combustion research; validation of detailed combustion models in the simpler flow environment of microgravity; and the radiative-emission data used in first-order fire models (see 4.5).
- [PSI] Once validated, the models can be used to build more complex models needed for flames in normal gravity, with wide applicability to terrestrial combustion problems, and to guide spacecraft design for crew safety.

## PSI-26 | 6. Test log (what was run)
Full rows are in `PSI-26_experimental_table.md`, one self-contained line per test (each line starts with "PSI-26 BASS test log"). The log has the columns Date, GMT, As Run Test #, Test #, Sample #, and Fuel Sample Material. [TABLE]

- 121 test rows plus 1 row "SOOT Cleaning" (08/03/2012, no test number). [TABLE]
- Dates: 03/30/2012 to 06/01/2013 (19 test days in 2012, 11 in 2013). This is inside the PSI-26 investigation period. [TABLE + PSI]
- 116 distinct As Run numbers, 117 distinct Test #, 40 distinct Sample #. [TABLE]
- Material labels, grouped by the analyst: SIBAL 12 rows (2 cm: 10, of which one is labeled "opposed flow"; 1 cm: 2); Nomex 6 (blend 2 cm: 4; natural III: 2); Ultem sheet 2; PMMA-labeled 48 (spheres, slabs, "1 cm", "2 cm"); other sphere rows with no material name 30 (1 cm sphere 6, 2 cm sphere 18, plus the 6 wake sphere rows); candles and wax slabs 23 (paraffin, Japan wax). [TABLE]
- [N/A] The record does not define "SIBAL", and does not say what the sizes "1 cm" and "2 cm" measure (for example a diameter or a thickness).
- Agreement with the record: fabric (cotton/fiberglass), Nomex, Ultem, spheres, and wake flames appear in both. [PSI + TABLE]
- Not in the record: PMMA, candles, and wax slabs are not named in the PSI-26 text. Cylinders are named in the PSI-26 text but no row uses the word "cylinder". [PSI + TABLE]
- The log does not state which rows belong to BASS and which to BASS-II.

### 6.1 Inconsistencies in the log (copied unchanged in the table file)
1. Two date typos: `6/29/`12` and `5/15/2103`.
2. GMT looks like the day of the year (114 of 121 rows match the date). Seven rows do not match: 04/26/2013 with GMT 113 (the date is day 116); 06/01/2013 with GMT 137 and 150 (the date is day 152).
3. As Run Test # 24 and 85 are each used on two rows on the same day (tests 12-R and 12-R2; 117 and 117a). As Run 89, 90, and 91 are used on 04/16/2013 and again on 04/23/2013 for different tests.
4. Test # 53, 75, 114, and 118 each appear once in 2012 and once in 2013.
5. The same Sample # carries different labels (for example Sample 22: "2 cm sphere" and "PMMA sphere 2 cm"), with spelling variants ("parrafin", "oppsed"). The rows labeled only "2 cm sphere" are therefore not confirmed as PMMA.

## PSI-26 | 7. Comparisons

### 7.1 BASS (PSI-26) vs BASS-II (PSI-25)
| Item | BASS (PSI-26) | BASS-II (PSI-25) |
|---|---|---|
| Period | 10-01-2009 to 06-30-2013 | 01-01-2010 to 12-31-2022 |
| Platform | ISS, Microgravity Science Glovebox | ISS, Microgravity Science Glovebox |
| Flow speed | Up to 40 cm/s | Up to 40 cm/s |
| Flow direction | Opposed and concurrent | Opposed and concurrent |
| Samples | Cotton/fiberglass fabric (75/25 by mass), Nomex, Ultem; spheres, cylinders | Rods, spherical sections, slabs, films, fabric sheets; slabs, cylinders, spherical sections |
| Oxygen | Nitrogen as flame suppressant (objective 2); the Approach does not say oxygen was varied | Oxygen varied below 21% by adding nitrogen (nitrogen vitiation); tested at constant O2 mole fractions |
| Objectives | Bridge Test #1, ground microgravity tests, and real flammability; assess inert-gas extinguishing | Ignition, growth, spread, and extinction limits; bridge Test #1; preliminary data for SoFIE PIs; thicker fuels |
| Hypothesis | Same: burns as well or better in microgravity with adequate ventilation | Same, and adds that Test 1 may not be conservative for space; looks for the fundamental limit of a material |
| Igniter | Kanthal wire, 29-gage | [N/A] |
| Duct | 76 mm x 76 mm cross section | [N/A] "small wind tunnel" |
| Principal investigator | Paul Ferkul | [N/A] Ferkul is listed as Co-I; no PI is listed |

### 7.2 BASS (PSI-26) vs PSI-62 (modeling)
| Item | PSI-26 (BASS) | PSI-62 |
|---|---|---|
| Type | Microgravity flight investigation | Ground investigation (modeling) |
| Period | 10-01-2009 to 06-30-2013 | 05-01-2019 to 04-30-2021 |
| What it does | Burns samples on the ISS and records flame size, shape, color, spread rate, quenching | Develops and validates an unsteady flamelet generated manifold (UFGM) model of concurrent flame spread, with BASS and BASS-II as benchmarks |
| Samples | Fabrics, Nomex, Ultem, spheres, cylinders | Flat sheets, spheres, PMMA rods (as simulated on BASS geometries), wax cylinders |
| Link | BASS imagery and BASS-II imagery are post-processed in PSI-62 with two-color tomography (DSLR cameras) to reconstruct 3D soot and temperature fields | Compared with model predictions of flame geometry, temperature, soot volume fraction, and spread rate |
| Open items | [N/A] results | The "Goldilocks" flammability zone (Olson and Ferkul) is a target of the model. [N/A] the record does not define it |

### 7.3 Microgravity (0g) vs normal gravity (1g)
| Item | 1g | 0g |
|---|---|---|
| Material screening | NASA-STD-6001 Test 1, upward burning, considered the worst-case geometry on Earth [PSI] | Not conservative by assumption in the Test 1 design: the record's hypothesis is that materials burn as well or better, with adequate ventilation [PSI] |
| Flame shape | Upward-pointed cone [PSI-25] | Oval ball [PSI-25] |
| Flow around flame | [PHYS] Buoyant flow plus any imposed flow | [PHYS] Imposed flow plus flame-generated flow |
| Test duration | [PHYS] Not limiting for ground tests of thick fuels | Needs long microgravity time for thick fuels [PSI] |
| Measured comparison | [N/A] | [N/A] |

### 7.4 Ground microgravity facilities vs ISS (from the record)
- The record says drop towers and parabolic aircraft do not give enough time to test any but the thinnest materials. The ISS gives longer flame times. [PSI]
- Ground-based microgravity combustion research receives guidance from BASS results. [PSI]

## PSI-26 | 8. Questions a team may ask
Q: What is BASS?
A: Burning and Suppression of Solids, an ISS investigation in the Microgravity Science Glovebox (10-01-2009 to 06-30-2013, PI Paul Ferkul). [PSI]

Q: What are the two main objectives?
A: (1) Bridge the gap between NASA-STD-6001 Test #1, ground-based microgravity tests, and actual material flammability in microgravity. (2) Assess an inert gaseous extinguishing agent over different materials, geometries, preheating, and flow. [PSI]

Q: What is the hypothesis?
A: With adequate ventilation, materials in microgravity burn as well or better than in normal gravity at identical pressure, oxygen concentration, and temperature. [PSI]

Q: Why is the ISS needed?
A: Testing the hypothesis with any but the thinnest materials takes more microgravity time than drop towers or parabolic aircraft give. Physically, a thick solid needs time to heat through its thickness (time scale d^2 / alpha_s). [PSI + PHYS]

Q: What materials were burned?
A: Per the record: 75% cotton / 25% fiberglass fabric, Nomex fabric, Ultem, plus spheres and cylinders. The test log also lists PMMA, candles (paraffin, Japan wax), and wax slabs. [PSI + TABLE]

Q: How was the flow controlled?
A: A variable-speed fan, up to 40 cm/s, along the fuel surface in the concurrent or opposed direction, in a duct of 76 mm x 76 mm cross section. [PSI]

Q: What is the difference between concurrent and opposed flow?
A: Concurrent: the air flows in the same direction as the flame spread. Opposed: the air flows against the spread. [PSI] In concurrent flow the flame lies over unburned fuel, in opposed flow oxygen reaches the flame front first. [PHYS]

Q: What is a wake flame?
A: A flame with the characteristics of a fire burning behind another object, for example in a tight area that is not easily accessible. [PSI]

Q: What was measured?
A: Flame size, shape, color, spread rate, and potential flame quenching, from top and edge views. [PSI]

Q: What were the results (spread rate, quenching limits)?
A: [N/A] The PSI-26 record and the supplied test log give no numerical results.

Q: How does inert gas extinguish a flame?
A: Nitrogen dilutes the oxygen, which lowers the reaction rate and the flame temperature. [PHYS] The record states the link to current and planned extinguishment techniques. [PSI]

Q: Why does flame radiation matter?
A: The record calls radiative heat emission from the flame a critical element. It feeds first-order models of heat release in spacecraft fires and extends cone calorimeter (Test 2) data to a performance-based material selection process. [PSI]

Q: How does BASS differ from BASS-II?
A: See table 7.1: the hypothesis is the same. BASS-II lists a wider set of geometries, varies oxygen below 21% with nitrogen, and runs until 12-31-2022. [PSI]

Q: How does PSI-62 use BASS?
A: It uses BASS and BASS-II as benchmarks for a UFGM concurrent flame spread model, and reconstructs 3D soot and temperature fields from BASS imagery with two-color tomography. [PSI]

Q: How many tests were run and when?
A: The log has 121 test rows, from 03/30/2012 to 06/01/2013. [TABLE]

Q: Is the test log reliable?
A: It has date typos, seven GMT values that do not match the date, repeated As Run numbers, and repeated Test numbers (section 6.1). Check the source before quoting exact numbers. [TABLE]

## PSI-26 | 9. Limits of this document
- [N/A] No results, measured values, or extinction limits are available in the PSI-26 record or the supplied table.
- [N/A] The meaning of "SIBAL", "ign", and the sample sizes (1 cm, 2 cm) is not given.
- [N/A] The PSI-26 record does not say whether oxygen concentration or preheating levels were varied, or which tests used the extinguishing agent.
- [PHYS] Statements tagged [PHYS] explain mechanisms in general terms. They are not findings of BASS.

## PSI-26 | 10. Impacts [PSI]
- NASA spacecraft material selection uses NASA-STD-6001 Test 1, which sorts materials by 1g behavior. BASS builds the link to behavior in low gravity.
- BASS results are used in first-order models of heat release in spacecraft fires and extend cone calorimeter (Test 2) data.
- Nitrogen as a suppressant in microgravity links directly to current and planned extinguishment techniques.
- BASS results guide ground-based microgravity combustion research. Validated models are applicable to terrestrial combustion problems and guide spacecraft design for crew safety.

## PSI-26 | 11. Related PSI records
- **PSI-25 (BASS-II):** continuation with the same hypothesis, wider geometries, and oxygen variation (table 7.1).
- **PSI-62:** ground modeling of concurrent flame spread using BASS and BASS-II experiments as benchmarks (table 7.2).

## PSI-26 | 12. Terminology and synonyms
General terms, not results. They are listed so that a search with another wording still finds this file.
- PSI-26 = BASS = Burning and Suppression of Solids. PSI-25 = BASS-II (also written BASS II).
- Microgravity = low gravity = reduced gravity = 0g = weightlessness (on the ISS).
- Flame spread = flame propagation over a solid. Spread rate = flame spread velocity.
- Concurrent flow = co-current flow: the air flows in the direction of the flame spread. Opposed flow = counter-current flow: the air flows against the flame spread.
- Wake flame = a flame behind an object (flow wake).
- Extinction = flame-out = quenching. Blowoff = blow-off: the flame is removed by a fast flow.
- Oxygen concentration = O2 mole fraction = O2 % by volume.
- Nitrogen suppression = inert-gas suppression = inert-gas dilution. (PSI-25 calls the reduction of oxygen with nitrogen "nitrogen vitiation".)
- Radiative heat emission = flame radiation.
- Thermally thick fuel = a solid that must heat through its thickness. Thermally thin fuel = a solid heated through its thickness almost at once.
- PMMA = polymethyl methacrylate (acrylic). MSG = Microgravity Science Glovebox. ISS = International Space Station.
- NASA-STD-6001 Test 1 = the normal-gravity upward-burning flammability test. Test 2 = the NASA cone calorimeter test.
- Termes en français: microgravité, propagation de flamme, vitesse de propagation, écoulement concurrent (même sens que la propagation), écoulement opposé (sens contraire), flamme de sillage, extinction, soufflage (blowoff), concentration en oxygène, dilution à l'azote, rayonnement de la flamme, combustible thermiquement épais ou mince.
