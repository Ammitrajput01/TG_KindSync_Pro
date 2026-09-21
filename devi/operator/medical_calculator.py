"""
DEVI Medical & Clinical Formula Engine
=======================================
Comprehensive, subject-wise medical calculation suite for MBBS, NEET-PG, USMLE,
and Clinical Wards. Includes Pediatrics, General Medicine, Nephrology, Surgery,
Emergency, OBG, PSM/Epidemiology, and Pharmacology Infusion calculators.
"""

import math
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, Union

# ==============================================================================
# 1. PEDIATRICS (Ward, PICU & NICU Essentials)
# ==============================================================================

def calc_pediatric_dose(adult_dose: float, age_years: Optional[float] = None, weight_kg: Optional[float] = None, age_months: Optional[float] = None) -> Dict[str, Any]:
    """Calculates pediatric drug dosage using Clark's, Young's, or Fried's Rules."""
    results = {}
    if weight_kg and weight_kg > 0:
        # Clark's Rule: (Weight in kg / 70) * Adult Dose
        clark_dose = (weight_kg / 70.0) * adult_dose
        results["clark"] = {
            "name": "Clark's Rule (Weight-based)",
            "formula": "(Weight_kg / 70) × Adult Dose",
            "dose": round(clark_dose, 2),
            "unit": "mg/dose"
        }
    if age_years and age_years > 0:
        # Young's Rule: (Age / (Age + 12)) * Adult Dose
        young_dose = (age_years / (age_years + 12.0)) * adult_dose
        results["young"] = {
            "name": "Young's Rule (Age > 1 yr)",
            "formula": "(Age / (Age + 12)) × Adult Dose",
            "dose": round(young_dose, 2),
            "unit": "mg/dose"
        }
    if age_months and age_months > 0:
        # Fried's Rule for Infants (< 1 yr): (Age_months / 150) * Adult Dose
        fried_dose = (age_months / 150.0) * adult_dose
        results["fried"] = {
            "name": "Fried's Rule (Infants < 1 yr)",
            "formula": "(Age_months / 150) × Adult Dose",
            "dose": round(fried_dose, 2),
            "unit": "mg/dose"
        }
    return results


def calc_mg_per_kg(dose_mg_kg: float, weight_kg: float, strength_mg_5ml: Optional[float] = None) -> Dict[str, Any]:
    """Calculates exact total mg dose and syrup volume in mL."""
    total_mg = dose_mg_kg * weight_kg
    res = {
        "total_mg": round(total_mg, 2),
        "dose_mg_kg": dose_mg_kg,
        "weight_kg": weight_kg
    }
    if strength_mg_5ml and strength_mg_5ml > 0:
        # Syrup volume: (total_mg / strength_mg) * 5 mL
        ml_dose = (total_mg / strength_mg_5ml) * 5.0
        res["syrup_ml"] = round(ml_dose, 2)
        res["strength_mg_5ml"] = strength_mg_5ml
    return res


def calc_pediatric_weight_est(age_years: Optional[float] = None, age_months: Optional[float] = None) -> Dict[str, Any]:
    """Estimates normal pediatric body weight based on age (APLS / Weech's formulas)."""
    if age_months is not None and age_months <= 12:
        # Infancy: (Age in months + 9) / 2
        est_wt = (age_months + 9.0) / 2.0
        formula_used = "(Age_months + 9) / 2"
    elif age_years is not None:
        if 1 <= age_years <= 6:
            # 1-6 years: (Age * 2) + 8
            est_wt = (age_years * 2.0) + 8.0
            formula_used = "(Age × 2) + 8"
        elif 7 <= age_years <= 12:
            # 7-12 years: (Age * 7 - 5) / 2
            est_wt = (age_years * 7.0 - 5.0) / 2.0
            formula_used = "(Age × 7 - 5) / 2"
        else:
            est_wt = age_years * 3.0
            formula_used = "Age × 3"
    else:
        est_wt = 10.0
        formula_used = "Standard Baseline"
    return {"estimated_weight_kg": round(est_wt, 1), "formula": formula_used}


def calc_et_tube(age_years: float) -> Dict[str, Any]:
    """Calculates pediatric Endotracheal (ET) Tube internal diameter and depth."""
    uncuffed = (age_years / 4.0) + 4.0
    cuffed = (age_years / 4.0) + 3.5
    depth = (age_years / 2.0) + 12.0
    return {
        "uncuffed_size_mm": round(uncuffed, 1),
        "cuffed_size_mm": round(cuffed, 1),
        "insertion_depth_cm": round(depth, 1),
        "rule_of_thumb_depth": f"{round(uncuffed * 3, 1)} cm (Size × 3)"
    }


def calc_maintenance_fluids(weight_kg: float) -> Dict[str, Any]:
    """Holliday-Segar 4-2-1 Maintenance IV Fluid calculation."""
    if weight_kg <= 10:
        ml_hr = weight_kg * 4.0
        ml_day = weight_kg * 100.0
    elif weight_kg <= 20:
        ml_hr = 40.0 + (weight_kg - 10.0) * 2.0
        ml_day = 1000.0 + (weight_kg - 10.0) * 50.0
    else:
        ml_hr = 60.0 + (weight_kg - 20.0) * 1.0
        ml_day = 1500.0 + (weight_kg - 20.0) * 20.0

    return {
        "weight_kg": weight_kg,
        "rate_ml_hr": round(ml_hr, 1),
        "total_24h_ml": round(ml_day, 1),
        "formula": "Holliday-Segar 4-2-1 Rule (100/50/20 mL/kg/day)"
    }


def calc_apgar(appearance: int, pulse: int, grimace: int, activity: int, respiration: int) -> Dict[str, Any]:
    """Calculates neonatal APGAR score (0-10) and resuscitation category."""
    total = appearance + pulse + grimace + activity + respiration
    if total >= 7:
        status = "Reassuring / Normal 🟢 (Routine Postnatal Care)"
    elif 4 <= total <= 6:
        status = "Moderately Abnormal 🟡 (Airway clearance, Stimulation, Supplemental O₂)"
    else:
        status = "Critically Low / Severe Distress 🔴 (Immediate Active Resuscitation, Bag-Mask / Intubation)"
    return {
        "score": total,
        "breakdown": f"A:{appearance} P:{pulse} G:{grimace} A:{activity} R:{respiration}",
        "status": status
    }


# ==============================================================================
# 2. GENERAL MEDICINE & NEPHROLOGY / CRITICAL CARE
# ==============================================================================

def calc_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """Calculates BMI, WHO/Asian classification, and Devine Ideal Body Weight."""
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    
    # WHO Classification
    if bmi < 18.5:
        who_cat = "Underweight 🔵"
    elif bmi < 24.9:
        who_cat = "Normal Weight 🟢 (Ideal)"
    elif bmi < 29.9:
        who_cat = "Overweight 🟡 (Pre-obese)"
    elif bmi < 34.9:
        who_cat = "Obesity Class I 🟠"
    elif bmi < 39.9:
        who_cat = "Obesity Class II 🔴"
    else:
        who_cat = "Obesity Class III (Severe / Morbid) 🟣"

    # Asian Indian Cutoff (Consensus Guidelines)
    if bmi < 18.5:
        asian_cat = "Underweight"
    elif bmi <= 22.9:
        asian_cat = "Normal (Asian Cutoff: 18.5-22.9)"
    elif bmi <= 24.9:
        asian_cat = "Overweight (Asian Cutoff: 23.0-24.9)"
    else:
        asian_cat = "Obese (Asian Cutoff: ≥ 25.0)"

    # Devine Ideal Body Weight (for height in inches > 60)
    height_inches = height_cm / 2.54
    inches_over_5ft = max(0.0, height_inches - 60.0)
    ibw_male = 50.0 + (2.3 * inches_over_5ft)
    ibw_female = 45.5 + (2.3 * inches_over_5ft)

    return {
        "bmi": round(bmi, 2),
        "who_category": who_cat,
        "asian_category": asian_cat,
        "ideal_body_weight_male": round(ibw_male, 1),
        "ideal_body_weight_female": round(ibw_female, 1)
    }


def calc_bsa(height_cm: float, weight_kg: float) -> Dict[str, Any]:
    """Calculates Body Surface Area (BSA) via Mosteller & DuBois formulas."""
    mosteller = math.sqrt((height_cm * weight_kg) / 3600.0)
    dubois = 0.007184 * (height_cm ** 0.725) * (weight_kg ** 0.425)
    return {
        "mosteller_m2": round(mosteller, 2),
        "dubois_m2": round(dubois, 2)
    }


def calc_gfr(age_years: float, weight_kg: float, serum_cr_mg_dl: float, is_female: bool = False) -> Dict[str, Any]:
    """Cockcroft-Gault Creatinine Clearance & KDIGO CKD Staging."""
    cr_cl = ((140.0 - age_years) * weight_kg) / (72.0 * serum_cr_mg_dl)
    if is_female:
        cr_cl *= 0.85

    if cr_cl >= 90:
        ckd_stage = "Stage 1 (Normal / High GFR ≥ 90 mL/min) 🟢"
    elif cr_cl >= 60:
        ckd_stage = "Stage 2 (Mildly Decreased: 60-89 mL/min) 🟢"
    elif cr_cl >= 45:
        ckd_stage = "Stage 3a (Mild-to-Moderate: 45-59 mL/min) 🟡"
    elif cr_cl >= 30:
        ckd_stage = "Stage 3b (Moderate-to-Severe: 30-44 mL/min) 🟠"
    elif cr_cl >= 15:
        ckd_stage = "Stage 4 (Severely Decreased: 15-29 mL/min) 🔴"
    else:
        ckd_stage = "Stage 5 (Kidney Failure / ESRD: < 15 mL/min) 🟣 (Dialysis Indicated)"

    return {
        "cr_cl_ml_min": round(cr_cl, 1),
        "ckd_stage": ckd_stage,
        "is_female": is_female
    }


def calc_map(sbp: float, dbp: float) -> Dict[str, Any]:
    """Calculates Mean Arterial Pressure (MAP) and organ perfusion state."""
    map_val = dbp + (sbp - dbp) / 3.0
    status = "Adequate Organ Perfusion (≥ 65 mmHg) 🟢" if map_val >= 65.0 else "Risk of Hypoperfusion / Shock (< 65 mmHg) 🔴"
    return {
        "map": round(map_val, 1),
        "sbp": sbp,
        "dbp": dbp,
        "status": status
    }


def calc_anion_gap(na: float, cl: float, hco3: float, albumin_g_dl: Optional[float] = None) -> Dict[str, Any]:
    """Calculates Serum Anion Gap with optional Figge albumin correction."""
    ag = na - (cl + hco3)
    res = {"anion_gap": round(ag, 1), "na": na, "cl": cl, "hco3": hco3}
    if ag > 12:
        res["interpretation"] = "High Anion Gap Metabolic Acidosis (HAGMA) 🔴\n*(MUDPILES / GOLD MARK causes)*"
    elif ag < 4:
        res["interpretation"] = "Low Anion Gap 🔵\n*(Hypoalbuminemia, Multiple Myeloma)*"
    else:
        res["interpretation"] = "Normal Anion Gap (8 - 12 mEq/L) 🟢"

    if albumin_g_dl is not None:
        corrected_ag = ag + 2.5 * (4.0 - albumin_g_dl)
        res["corrected_anion_gap"] = round(corrected_ag, 1)
        res["albumin"] = albumin_g_dl
    return res


def calc_corrected_sodium(measured_na: float, glucose_mg_dl: float) -> Dict[str, Any]:
    """Calculates Corrected Sodium in Hyperglycemia (Katz / Hillier formula)."""
    # Katz: Measured Na + 0.016 * (Glucose - 100)
    corrected_na = measured_na + 1.6 * ((glucose_mg_dl - 100.0) / 100.0)
    return {
        "measured_na": measured_na,
        "glucose_mg_dl": glucose_mg_dl,
        "corrected_na": round(corrected_na, 1)
    }


def calc_gcs(eye: int, verbal: int, motor: int) -> Dict[str, Any]:
    """Glasgow Coma Scale score & Head Injury severity."""
    total = eye + verbal + motor
    if total <= 8:
        severity = "Severe Brain Injury / Coma 🔴 ('GCS ≤ 8, Intubate!')"
    elif total <= 12:
        severity = "Moderate Brain Injury 🟡"
    else:
        severity = "Mild / Normal 🟢 (Minor Head Injury)"
    return {
        "total_score": total,
        "eye": eye,
        "verbal": verbal,
        "motor": motor,
        "severity": severity
    }


# ==============================================================================
# 3. SURGERY, TRAUMA & EMERGENCY
# ==============================================================================

def calc_parkland(weight_kg: float, tbsa_pct: float) -> Dict[str, Any]:
    """Parkland Formula for Burns Resuscitation Fluid (Ringer's Lactate)."""
    # Total 24h = 4 mL * Weight (kg) * % TBSA
    total_24h_ml = 4.0 * weight_kg * tbsa_pct
    first_8h_ml = total_24h_ml / 2.0
    remaining_16h_ml = total_24h_ml / 2.0
    first_8h_rate_ml_hr = first_8h_ml / 8.0
    remaining_16h_rate_ml_hr = remaining_16h_ml / 16.0

    return {
        "weight_kg": weight_kg,
        "tbsa_pct": tbsa_pct,
        "total_24h_ml": round(total_24h_ml, 1),
        "first_8h_ml": round(first_8h_ml, 1),
        "first_8h_rate_ml_hr": round(first_8h_rate_ml_hr, 1),
        "remaining_16h_ml": round(remaining_16h_ml, 1),
        "remaining_16h_rate_ml_hr": round(remaining_16h_rate_ml_hr, 1),
        "fluid_type": "Ringer's Lactate (RL)"
    }


def calc_urine_output(volume_ml: float, weight_kg: float, hours: float) -> Dict[str, Any]:
    """Calculates Urine Output Rate in mL/kg/hr."""
    rate = volume_ml / (weight_kg * hours)
    if rate < 0.3:
        status = "Severe Oliguria / Anuria 🔴 (Immediate Renal Evaluation)"
    elif rate < 0.5:
        status = "Oliguria 🟡 (Target Adult UOP ≥ 0.5 mL/kg/hr)"
    else:
        status = "Adequate Urine Output 🟢 (≥ 0.5 mL/kg/hr)"
    return {
        "uop_ml_kg_hr": round(rate, 2),
        "status": status,
        "volume_ml": volume_ml,
        "weight_kg": weight_kg,
        "hours": hours
    }


# ==============================================================================
# 4. OBSTETRICS & GYNECOLOGY (OBG)
# ==============================================================================

def calc_edd(lmp_date_str: str) -> Dict[str, Any]:
    """Naegele's Rule: LMP + 9 Months + 7 Days + Gestational Age in Weeks."""
    # Support formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
    dt = None
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            dt = datetime.strptime(lmp_date_str.strip(), fmt)
            break
        except Exception:
            pass

    if not dt:
        return {"error": "Invalid date format. Use DD/MM/YYYY (e.g. 15/01/2026)"}

    # Naegele's Rule: + 1 Year - 3 Months + 7 Days
    edd_dt = dt + timedelta(days=280)  # 40 weeks = 280 days
    today = datetime.now()
    days_pregnant = max(0, (today - dt).days)
    weeks = days_pregnant // 7
    days = days_pregnant % 7

    if weeks < 13:
        trimester = "First Trimester (1 - 12 Weeks) 🌱"
    elif weeks < 28:
        trimester = "Second Trimester (13 - 27 Weeks) 🌸"
    else:
        trimester = "Third Trimester (28 - 40+ Weeks) 🤰"

    return {
        "lmp": dt.strftime("%d %B %Y"),
        "edd": edd_dt.strftime("%d %B %Y (%A)"),
        "gestational_age": f"{weeks} Weeks, {days} Days",
        "total_days": days_pregnant,
        "trimester": trimester
    }


# ==============================================================================
# 5. PSM & BIOSTATISTICS (Epidemiology)
# ==============================================================================

def calc_psm_matrix(tp: float, fp: float, fn: float, tn: float) -> Dict[str, Any]:
    """Calculates Diagnostic 2x2 Contingency Table (Sensitivity, Specificity, PPV, NPV)."""
    total = tp + fp + fn + tn
    sensitivity = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
    specificity = (tn / (tn + fp)) * 100.0 if (tn + fp) > 0 else 0.0
    ppv = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
    npv = (tn / (tn + fn)) * 100.0 if (tn + fn) > 0 else 0.0
    accuracy = ((tp + tn) / total) * 100.0 if total > 0 else 0.0
    
    # Relative Risk & Odds Ratio
    rr = (tp / (tp + fp)) / (fn / (fn + tn)) if (tp + fp) > 0 and (fn + tn) > 0 and (fn / (fn + tn)) > 0 else 0.0
    odds_ratio = (tp * tn) / (fp * fn) if (fp * fn) > 0 else 0.0

    return {
        "sensitivity": round(sensitivity, 1),
        "specificity": round(specificity, 1),
        "ppv": round(ppv, 1),
        "npv": round(npv, 1),
        "accuracy": round(accuracy, 1),
        "relative_risk": round(rr, 2),
        "odds_ratio": round(odds_ratio, 2),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn
    }


# ==============================================================================
# 6. PHARMACOLOGY & WARD INFUSIONS
# ==============================================================================

def calc_iv_drip(volume_ml: float, hours: float, drop_factor: int = 20) -> Dict[str, Any]:
    """Calculates IV Drip Rate in Drops per minute (gtt/min) and mL/hour."""
    total_minutes = hours * 60.0
    drops_per_min = (volume_ml * drop_factor) / total_minutes
    ml_per_hour = volume_ml / hours
    return {
        "volume_ml": volume_ml,
        "hours": hours,
        "drop_factor": drop_factor,
        "drops_per_min": round(drops_per_min),
        "ml_per_hour": round(ml_per_hour, 1)
    }


def calc_inotrope_infusion(drug_mg: float, volume_ml: float, dose_mcg_kg_min: float, weight_kg: float) -> Dict[str, Any]:
    """Calculates Syringe Pump Infusion Rate in mL/hr for Inotropes (Noradrenaline, Dopamine, Dobutamine)."""
    # Concentration in mcg/mL = (drug_mg * 1000) / volume_ml
    conc_mcg_ml = (drug_mg * 1000.0) / volume_ml
    # Dose required in mcg/min = dose_mcg_kg_min * weight_kg
    dose_mcg_min = dose_mcg_kg_min * weight_kg
    # Infusion rate in mL/hr = (dose_mcg_min * 60) / conc_mcg_ml
    rate_ml_hr = (dose_mcg_min * 60.0) / conc_mcg_ml

    return {
        "drug_mg": drug_mg,
        "volume_ml": volume_ml,
        "concentration_mcg_ml": round(conc_mcg_ml, 1),
        "dose_mcg_kg_min": dose_mcg_kg_min,
        "weight_kg": weight_kg,
        "rate_ml_hr": round(rate_ml_hr, 2)
    }


def calc_curb65(confusion: int, urea_gt_7: int, rr_ge_30: int, bp_low: int, age_ge_65: int) -> Dict[str, Any]:
    """CURB-65 Pneumonia Severity Score & 30-day mortality risk."""
    score = int(confusion > 0) + int(urea_gt_7 > 0) + int(rr_ge_30 > 0) + int(bp_low > 0) + int(age_ge_65 > 0)
    if score <= 1:
        risk_group = "Low Risk 🟢"
        mortality = "< 3%"
        rec = "Outpatient treatment usually suitable."
    elif score == 2:
        risk_group = "Intermediate Risk 🟡"
        mortality = "approx. 9%"
        rec = "Consider inpatient admission or closely monitored outpatient care."
    else:
        risk_group = "High Risk 🔴"
        mortality = "15% - 40%"
        rec = "Urgent hospital admission. Consider ICU if score ≥ 4."

    return {
        "score": score,
        "risk_group": risk_group,
        "mortality_risk": mortality,
        "recommendation": rec,
        "breakdown": f"C={int(confusion > 0)}, U={int(urea_gt_7 > 0)}, R={int(rr_ge_30 > 0)}, B={int(bp_low > 0)}, 65={int(age_ge_65 > 0)}"
    }


def calc_wells_pe(dvt_signs: int, pe_likely: int, hr_gt_100: int, immob_surg: int, prior_dvt_pe: int, hemoptysis: int, malignancy: int) -> Dict[str, Any]:
    """Wells Score for Pulmonary Embolism probability and diagnostic path."""
    score = 0.0
    if dvt_signs: score += 3.0
    if pe_likely: score += 3.0
    if hr_gt_100: score += 1.5
    if immob_surg: score += 1.5
    if prior_dvt_pe: score += 1.5
    if hemoptysis: score += 1.0
    if malignancy: score += 1.0

    two_tier = "PE Likely 🔴" if score > 4.0 else "PE Unlikely 🟢"
    if score < 2.0:
        three_tier = "Low Risk (~1.3% PE rate)"
    elif score <= 6.0:
        three_tier = "Moderate Risk (~16.2% PE rate)"
    else:
        three_tier = "High Risk (~37.5% PE rate)"

    management = "Order high-sensitivity D-dimer. If negative, PE ruled out." if score <= 4.0 else "Proceed directly to CT Pulmonary Angiography (CTPA) & begin anticoagulation if no contraindications."

    return {
        "score": round(score, 1),
        "two_tier_risk": two_tier,
        "probability_three_tier": three_tier,
        "management": management
    }

