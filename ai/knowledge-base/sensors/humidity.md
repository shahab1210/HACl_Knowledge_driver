# Humidity Sensor in Industrial IoT Fault Diagnosis

## 1. What the Sensor Measures
An industrial IoT humidity sensor measures the moisture content or water vapor concentration present in the ambient atmosphere, electrical enclosures, or motor terminal junction boxes. Measurement technologies typically comprise capacitive polymer relative humidity (RH) sensors, resistive hygrometers, or thermal conductivity sensors. The sensor outputs relative humidity as a percentage (% RH, representing the ratio of partial vapor pressure to saturation vapor pressure at the current temperature) alongside ambient temperature telemetry.

## 2. What a Normal Reading Generally Represents
A normal relative humidity reading indicates that the surrounding air or enclosure interior remains within the designed dry environmental operating envelope (typically 30% to 70% RH in standard industrial plant environments). A stable, normal humidity reading confirms that environmental seals, cable glands, enclosure heaters, and ventilation breathers are intact, preventing moisture condensation on sensitive electrical insulation, stator windings, and control electronics.

> **Important Operational Note:**
> Actual limits depend on the equipment specification, sensor location, operating conditions, and manufacturer recommendations.

For example, inside a sealed motor terminal junction box or control cabinet equipped with an anti-condensation space heater, relative humidity should ideally stay below 60% to avoid moisture condensation during cold plant shutdowns.

## 3. What Abnormal Readings Can Indicate
Deviations and extreme humidity readings reveal environmental contamination, enclosure breach, or process fluid leaks:
- **Excessively High Humidity (> 80-90% RH):** High risk of condensation dew-point crossing, leading to moisture deposition on motor windings, tracking along terminal blocks, and rust formation on bearing raceways.
- **Localized Sudden Spikes:** Direct indicator of external fluid spraying, leaking pump mechanical seals, blown flange gaskets, or steam trap failures discharging vapor into the equipment enclosure.
- **Low Humidity (< 20% RH):** Elevated risk of electrostatic discharge (ESD) in electronic control enclosures and drying/cracking of elastomeric shaft seals.
- **Sensor Saturation / Flatline (100% or 0%):** Water droplet accumulation directly on capacitive polymer sensing elements, short-circuiting sensor electrodes, or sensor disconnection.

## 4. Which Faults the Sensor Can Help Identify
While humidity is largely an environmental or secondary diagnostic variable, it provides key corroborating evidence in critical scenarios:
- **[FAULT-010: Sensor Anomaly](../faults/sensor-anomaly.md):** 0% or 100% flatline readings caused by condensation bridges or broken telemetry leads.
- **[FAULT-007: Pump Dry Running](../faults/pump-dry-running.md):** Rapid humidity rise around seal glands when scorched seal faces vaporize residual barrier fluid or process liquid.
- **[FAULT-008: Low Pressure](../faults/low-pressure.md):** Elevated ambient humidity in pump skids corroborating active pipeline rupture or flange spray.
- **[FAULT-003: Motor Overheating](../faults/motor-overheating.md):** Prolonged high humidity accelerates dielectric breakdown of stator insulation, precipitating winding thermal failure.
- **[FAULT-002: Bearing Wear](../faults/bearing-wear.md):** High humidity drives water contamination into grease reservoirs, emulsifying lubricants and initiating corrosive bearing raceway pitting.

## 5. Limitations of Using That Sensor Alone
Humidity monitoring is strictly a contextual and secondary diagnostic tool with marked limitations:
- **Indirect Indicator of Mechanical Condition:** Humidity sensors cannot detect rotating machinery unbalance, shaft misalignment, bearing spalls, or electrical overloading.
- **Slow Environmental Diffusion:** Ambient atmospheric humidity changes slowly unless a high-pressure pipe directly ruptures against the sensor enclosure.
- **Contamination Susceptibility:** Airborne oil mist, dust, chemical vapors, and solvent fumes can contaminate or foul polymer hygrometer membranes, causing significant calibration drift.
- **Must be Synthesized with Primary Telemetry:** Humidity data is diagnostically valuable only when correlated with machine-specific telemetry including temperature, current, vibration, and hydraulic pressure.
