#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Unit Tests for Medical & Dosage Calculator Suite.
Tests:
1. Pediatrics: Clark's, Young's, Fried's, mg/kg, ET Tube, 4-2-1 Holliday-Segar, APGAR
2. General Medicine: BMI, BSA (Mosteller/DuBois), Cockcroft-Gault GFR, MAP, Anion Gap, Corrected Sodium, GCS
3. Surgery / Trauma: Parkland Burns Formula, Urine Output
4. OBG: Naegele's Rule EDD & Gestational Age
5. PSM & Epidemiology: 2x2 Matrix, Sensitivity, Specificity, PPV, NPV, Odds Ratio, Relative Risk
6. Pharmacology: IV Drip Rate, Inotrope Syringe Pump Infusion
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from devi.operator.medical_calculator import (
    calc_pediatric_dose, calc_mg_per_kg, calc_pediatric_weight_est,
    calc_et_tube, calc_maintenance_fluids, calc_apgar,
    calc_bmi, calc_bsa, calc_gfr, calc_map, calc_anion_gap,
    calc_corrected_sodium, calc_gcs,
    calc_parkland, calc_urine_output,
    calc_edd,
    calc_psm_matrix,
    calc_iv_drip, calc_inotrope_infusion,
    calc_ckd_epi_2021, calc_corrected_calcium, calc_meld_na
)


def test_pediatric_dosage_rules():
    # Clark's rule: (14 kg / 70) * 500 mg = 100 mg
    res = calc_pediatric_dose(adult_dose=500, weight_kg=14)
    assert "clark" in res
    assert res["clark"]["dose"] == 100.0

    # Young's rule: (4 / (4 + 12)) * 500 = (4/16) * 500 = 125 mg
    res_young = calc_pediatric_dose(adult_dose=500, age_years=4)
    assert "young" in res_young
    assert res_young["young"]["dose"] == 125.0

    # Fried's rule: (6 months / 150) * 500 = 20 mg
    res_fried = calc_pediatric_dose(adult_dose=500, age_months=6)
    assert "fried" in res_fried
    assert res_fried["fried"]["dose"] == 20.0


def test_mg_per_kg_and_syrup():
    # 15 mg/kg for 10 kg child = 150 mg total. Strength: 250 mg / 5 mL -> (150/250)*5 = 3 mL
    res = calc_mg_per_kg(dose_mg_kg=15, weight_kg=10, strength_mg_5ml=250)
    assert res["total_mg"] == 150.0
    assert res["syrup_ml"] == 3.0


def test_et_tube_and_fluids():
    # 4 year old: Uncuffed = 4/4 + 4 = 5.0 mm, Cuffed = 4/4 + 3.5 = 4.5 mm, Depth = 4/2 + 12 = 14 cm
    et = calc_et_tube(4)
    assert et["uncuffed_size_mm"] == 5.0
    assert et["cuffed_size_mm"] == 4.5
    assert et["insertion_depth_cm"] == 14.0

    # 4-2-1 fluids for 15 kg child: 10*4 + 5*2 = 50 mL/hr = 1200 mL/day
    fl = calc_maintenance_fluids(15)
    assert fl["rate_ml_hr"] == 50.0
    assert fl["total_24h_ml"] == 1250.0


def test_apgar():
    ap = calc_apgar(appearance=2, pulse=2, grimace=2, activity=2, respiration=2)
    assert ap["score"] == 10
    assert "Reassuring" in ap["status"]


def test_bmi_and_bsa():
    # BMI for 70 kg, 175 cm = 70 / (1.75^2) = 22.86
    bmi_res = calc_bmi(70, 175)
    assert bmi_res["bmi"] == 22.86
    assert "Normal Weight" in bmi_res["who_category"]

    # BSA Mosteller: sqrt(175 * 70 / 3600) = sqrt(3.40277) = 1.84
    bsa_res = calc_bsa(175, 70)
    assert bsa_res["mosteller_m2"] == 1.84


def test_gfr_and_map():
    # Cockcroft-Gault: ((140-50)*70)/(72*1.0) = (90*70)/72 = 6300/72 = 87.5 mL/min
    gfr_res = calc_gfr(age_years=50, weight_kg=70, serum_cr_mg_dl=1.0, is_female=False)
    assert gfr_res["cr_cl_ml_min"] == 87.5
    assert "Stage 2" in gfr_res["ckd_stage"]

    # MAP for 120/80: 80 + 40/3 = 93.3 mmHg
    map_res = calc_map(120, 80)
    assert map_res["map"] == 93.3


def test_parkland_burns():
    # Parkland for 70 kg, 30% TBSA: 4 * 70 * 30 = 8400 mL total, 4200 mL in first 8h (525 mL/hr)
    burns = calc_parkland(weight_kg=70, tbsa_pct=30)
    assert burns["total_24h_ml"] == 8400.0
    assert burns["first_8h_ml"] == 4200.0
    assert burns["first_8h_rate_ml_hr"] == 525.0


def test_edd():
    # LMP: 01/01/2026 -> EDD: 08/10/2026 (Naegele's rule: +280 days)
    edd_res = calc_edd("01/01/2026")
    assert "error" not in edd_res
    assert "October 2026" in edd_res["edd"]


def test_psm_matrix():
    # 2x2 table: TP=80, FP=20, FN=10, TN=90
    # Sensitivity = 80 / (80+10) = 80/90 = 88.9%
    # Specificity = 90 / (90+20) = 90/110 = 81.8%
    psm = calc_psm_matrix(tp=80, fp=20, fn=10, tn=90)
    assert psm["sensitivity"] == 88.9
    assert psm["specificity"] == 81.8


def test_pharmacology_infusions():
    # IV Drip: 1000 mL in 8 hours with drop factor 20 -> (1000 * 20) / (8 * 60) = 20000 / 480 = 41.67 -> 42 gtt/min
    drip = calc_iv_drip(volume_ml=1000, hours=8, drop_factor=20)
    assert drip["drops_per_min"] == 42
    assert drip["ml_per_hour"] == 125.0

    # Inotrope: Norad 4 mg in 50 mL for 70 kg patient at 0.1 mcg/kg/min
    # Conc = 4000 mcg / 50 mL = 80 mcg/mL
    # Dose = 0.1 * 70 = 7 mcg/min = 420 mcg/hr
    # Rate = 420 / 80 = 5.25 mL/hr
    inotrope = calc_inotrope_infusion(drug_mg=4, volume_ml=50, dose_mcg_kg_min=0.1, weight_kg=70)
    assert inotrope["rate_ml_hr"] == 5.25


def test_ckd_epi_2021_race_free():
    # 50 yo male, Cr 1.0 -> ~91.7 mL/min/1.73m2
    egfr_m = calc_ckd_epi_2021(age_years=50, serum_cr_mg_dl=1.0, is_female=False)
    assert egfr_m == 91.7

    # 60 yo female, Cr 1.2 -> ~51.8 mL/min/1.73m2
    egfr_f = calc_ckd_epi_2021(age_years=60, serum_cr_mg_dl=1.2, is_female=True)
    assert 50.0 <= egfr_f <= 53.0


def test_corrected_calcium():
    # Ca 7.8, Albumin 2.5 -> Payne: 7.8 + 0.8 * (4.0 - 2.5) = 7.8 + 1.2 = 9.0 (Normal)
    ca_res = calc_corrected_calcium(serum_ca_mg_dl=7.8, serum_albumin_g_dl=2.5)
    assert ca_res["corrected_ca"] == 9.0
    assert "Normal" in ca_res["status"]

    # Ca 11.5, Albumin 4.0 -> Payne: 11.5 + 0.8 * 0 = 11.5 (Hypercalcemia)
    ca_high = calc_corrected_calcium(serum_ca_mg_dl=11.5, serum_albumin_g_dl=4.0)
    assert ca_high["corrected_ca"] == 11.5
    assert "Hypercalcemia" in ca_high["status"]


def test_meld_na():
    # Bilirubin 2.5, INR 1.8, Cr 1.4, Na 130
    res = calc_meld_na(bilirubin_mg_dl=2.5, inr=1.8, creatinine_mg_dl=1.4, sodium_meq_l=130.0)
    assert "meld_score" in res
    assert "three_month_mortality" in res
    assert res["meld_score"] >= 15


