# -*- coding: utf-8 -*-
"""
Devi Operator Clinical & Medical Formulas Command Handlers
Dispatches /calc, /burns, /gcs, /egfr, /gfr, /bmi, /bsa, /pedia, /abg, /meld in O(1) time.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

import re
from typing import List, Optional, Any
from devi.operator.medical_calculator import calc_bmi, calc_bsa

async def handle_clinical_commands(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    """Central O(1) handler for clinical calculations and Bedside CDSS."""
    thread_id = message.get("message_thread_id") if message else None
    cmd = parts[0].lower().split("@")[0]
    
    sub_cmd = cmd.lstrip("/").lower()
    if sub_cmd in ("calc", "dose", "formula", "score"):
        sub_cmd = parts[1].lower() if len(parts) > 1 else "menu"
        calc_args = parts[2:]
    else:
        calc_args = parts[1:]

    def _clean_num(val_str: Any) -> float:
        cleaned = re.sub(r'[^\d\.]', '', str(val_str).replace(',', '.'))
        return float(cleaned) if cleaned else 0.0

    # A. MASTER CLINICAL MENU
    if sub_cmd in ("menu", "help", "?", "calchelp", "dosehelp", "scorehelp", "clinicalhelp"):
        menu_card = (
            "🧮 **KIND DOCTOR CLINICAL MEDICAL FORMULA & DOSAGE SUITE** 🩺\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Subject-Wise Clinical Ward, ICU & Exam Calculators:\n\n"
            "👶 **1. PEDIATRICS (Ward & PICU):**\n"
            "• `/pedia dose <adult_dose> <wt_kg>` ➔ Clark's & Young's Rule\n"
            "• `/pedia mgkg <dose_mg_kg> <wt_kg> [syrup_mg_5ml]` ➔ Exact Syrup mL\n"
            "• `/pedia ett <age_years>` ➔ ET Tube Size & Insertion Depth\n"
            "• `/pedia fluids <wt_kg>` ➔ Holliday-Segar 4-2-1 Maintenance IV Fluid\n"
            "• `/pedia apgar <A> <P> <G> <A> <R>` ➔ APGAR Score & Resuscitation\n\n"
            "🩺 **2. GENERAL MEDICINE & CRITICAL CARE:**\n"
            "• `/bmi <weight_kg> <height_cm>` ➔ BMI & Devine Ideal Body Weight\n"
            "• `/bsa <height_cm> <weight_kg>` ➔ Mosteller & DuBois Body Surface Area\n"
            "• `/gfr <age> <weight_kg> <serum_cr> <m/f>` ➔ CrCl (Cockcroft-Gault) & CKD-EPI 2021\n"
            "• `/ca <serum_ca> <serum_albumin>` ➔ Payne's Corrected Calcium\n"
            "• `/meld <bili> <inr> <cr> [na] [dialysis:0/1]` ➔ MELD-Na Liver Mortality Score\n"
            "• `/map <sbp> <dbp>` ➔ Mean Arterial Pressure & Shock Perfusion\n"
            "• `/abg <Na> <Cl> <HCO3> [Albumin]` ➔ Serum Anion Gap & Albumin Correction\n"
            "• `/sodium <measured_na> <glucose>` ➔ Corrected Sodium in Hyperglycemia\n"
            "• `/gcs <E:1-4> <V:1-5> <M:1-6>` ➔ Glasgow Coma Scale\n"
            "• `/curb65 <C> <U> <R> <B> <65>` ➔ Pneumonia Severity & Admission\n"
            "• `/wells <DVT> <Alt> <HR> <Immob> <Prior> <Hemo> <Ca>` ➔ Wells PE Score\n\n"
            "🔪 **3. SURGERY & EMERGENCY:**\n"
            "• `/burns <weight_kg> <tbsa_percent>` ➔ Parkland 24h Ringer Lactate Fluid\n"
            "• `/uop <volume_ml> <weight_kg> <hours>` ➔ Urine Output Rate (mL/kg/hr)\n\n"
            "🤰 **4. OBSTETRICS & GYNECOLOGY (OBG):**\n"
            "• `/edd <LMP_Date_DD/MM/YYYY>` ➔ Naegele's Rule, POG Weeks & Trimester\n\n"
            "📊 **5. PSM & BIOSTATISTICS:**\n"
            "• `/psm matrix <TP> <FP> <FN> <TN>` ➔ Sensitivity, Specificity, PPV, NPV\n\n"
            "💊 **6. PHARMACOLOGY & INFUSIONS:**\n"
            "• `/drip <volume_ml> <hours> [drop_factor]` ➔ IV Drip Rate in Drops/min\n"
            "• `/infusion <drug_mg> <vol_ml> <dose_mcg_kg_min> <wt_kg>` ➔ Inotrope Syringe Pump (mL/hr)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 *Tip: Direct commands work anywhere, e.g. `/bmi 70 175` ya `/gfr 55 70 1.2 m`*"
        )
        await bot._send_message(session, chat_id, menu_card, message_thread_id=thread_id)
        return

    # B. BMI & BODY COMPOSITION
    if sub_cmd == "bmi":
        if len(calc_args) < 2:
            await bot._send_message(session, chat_id, "Usage: `/bmi <weight_kg> <height_cm>`\nExample: `/bmi 70kg 175cm`", message_thread_id=thread_id)
            return
        try:
            wt, ht = _clean_num(calc_args[0]), _clean_num(calc_args[1])
            if wt <= 0 or ht <= 0:
                raise ValueError("Positive numbers required")
            res = calc_bmi(wt, ht)
            card = (
                f"⚖️ **Clinical Calculator: Body Mass Index (BMI)** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Weight**: `{wt:.1f} kg` | **Height**: `{ht:.0f} cm`\n"
                f"• **Calculated BMI**: `{res['bmi']} kg/m²`\n"
                f"• **WHO Classification**: **{res['who_category']}**\n"
                f"• **Asian Cutoff**: `{res['asian_category']}`\n"
                f"• **Ideal Body Weight (Devine)**:\n"
                f"   - Male: `{res['ideal_body_weight_male']} kg` | Female: `{res['ideal_body_weight_female']} kg`\n\n"
                f"💡 *Clinical Pearl: Asian cutoff considers BMI ≥ 23.0 as overweight and ≥ 25.0 as obese.*"
            )
            await bot._send_message(session, chat_id, card, message_thread_id=thread_id)
        except Exception:
            await bot._send_message(session, chat_id, "⚠️ Invalid input numbers. Example: `/bmi 70kg 175cm`", message_thread_id=thread_id)
        return

    # C. BSA (BODY SURFACE AREA)
    if sub_cmd == "bsa":
        if len(calc_args) < 2:
            await bot._send_message(session, chat_id, "Usage: `/bsa <height_cm> <weight_kg>`\nExample: `/bsa 175cm 70kg`", message_thread_id=thread_id)
            return
        try:
            ht, wt = _clean_num(calc_args[0]), _clean_num(calc_args[1])
            if ht <= 0 or wt <= 0:
                raise ValueError("Positive numbers required")
            res = calc_bsa(ht, wt)
            card = (
                f"📐 **Clinical Calculator: Body Surface Area (BSA)** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Height**: `{ht:.0f} cm` | **Weight**: `{wt:.1f} kg`\n"
                f"• **BSA (Mosteller Formula)**: `{res['bsa_mosteller']} m²`\n"
                f"• **BSA (DuBois Formula)**: `{res['bsa_dubois']} m²`\n\n"
                f"💡 *Clinical Pearl: Mosteller is standard for chemotherapy and renal drug dosing clearance.*"
            )
            await bot._send_message(session, chat_id, card, message_thread_id=thread_id)
        except Exception:
            await bot._send_message(session, chat_id, "⚠️ Invalid input numbers. Example: `/bsa 175cm 70kg`", message_thread_id=thread_id)
        return

    # D. BURNS (PARKLAND RESUSCITATION)
    if sub_cmd == "burns":
        if len(calc_args) < 2:
            await bot._send_message(session, chat_id, "Usage: `/burns <weight_kg> <tbsa_percent>`\nExample: `/burns 70 30`", message_thread_id=thread_id)
            return
        try:
            wt, tbsa = _clean_num(calc_args[0]), _clean_num(calc_args[1])
            total_rl = 4.0 * wt * tbsa
            first_8h = total_rl / 2.0
            next_16h = total_rl / 2.0
            rate_8h = first_8h / 8.0
            rate_16h = next_16h / 16.0
            card = (
                f"🔥 **Clinical Decision: Parkland Burn Resuscitation** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Patient Weight**: `{wt:.1f} kg` | **% TBSA Burn**: `{tbsa:.1f}%`\n"
                f"• **Total 24h Ringer's Lactate**: `{total_rl:,.0f} mL` (4 mL × kg × %TBSA)\n\n"
                f"⏱️ **Resuscitation Fluid Schedule:**\n"
                f"  1️⃣ **First 8 Hours** (from time of burn injury):\n"
                f"     • Volume: `{first_8h:,.0f} mL`\n"
                f"     • Infusion Velocity: `{rate_8h:.0f} mL/hr`\n"
                f"  2️⃣ **Next 16 Hours**:\n"
                f"     • Volume: `{next_16h:,.0f} mL`\n"
                f"     • Infusion Velocity: `{rate_16h:.0f} mL/hr`\n\n"
                f"🎯 **Urine Output Goal**: Titrate fluids to maintain `0.5–1.0 mL/kg/hr`."
            )
            await bot._send_message(session, chat_id, card, message_thread_id=thread_id)
        except Exception:
            await bot._send_message(session, chat_id, "⚠️ Invalid burn parameters. Example: `/burns 70 30`", message_thread_id=thread_id)
        return

    # E. GCS (GLASGOW COMA SCALE)
    if sub_cmd == "gcs":
        if len(calc_args) < 3:
            await bot._send_message(session, chat_id, "Usage: `/gcs <E:1-4> <V:1-5> <M:1-6>`\nExample: `/gcs 4 5 6`", message_thread_id=thread_id)
            return
        try:
            e, v, m = int(_clean_num(calc_args[0])), int(_clean_num(calc_args[1])), int(_clean_num(calc_args[2]))
            total_gcs = e + v + m
            if total_gcs <= 8:
                severity = "🚨 Severe Brain Injury (GCS ≤ 8: Intubate!)"
            elif total_gcs <= 12:
                severity = "⚠️ Moderate Brain Injury"
            else:
                severity = "✅ Mild / Normal Neuro Status"
            card = (
                f"🧠 **Neuro Triage: Glasgow Coma Scale (GCS)** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Eye (E)**: `{e}/4` | **Verbal (V)**: `{v}/5` | **Motor (M)**: `{m}/6`\n"
                f"• **Total GCS Score**: **`{total_gcs}/15`**\n"
                f"• **Grading**: {severity}\n\n"
                f"💡 *Pearl: GCS ≤ 8 is standard clinical indication for endotracheal intubation.*"
            )
            await bot._send_message(session, chat_id, card, message_thread_id=thread_id)
        except Exception:
            await bot._send_message(session, chat_id, "⚠️ Invalid GCS numbers. Example: `/gcs 4 5 6`", message_thread_id=thread_id)
        return

    # Fallback to general clinical calculator routing in bot if specific formula
    return None

def register_clinical_handlers(router):
    commands = [
        "/calc", "/dose", "/formula", "/score", "/bmi", "/bsa", "/gfr", 
        "/pedia", "/burns", "/uop", "/edd", "/psm", "/drip", "/infusion", 
        "/map", "/abg", "/sodium", "/gcs", "/curb65", "/wells", "/ca", 
        "/calcium", "/meld", "/calchelp", "/dosehelp", "/scorehelp", "/clinicalhelp"
    ]
    router.register(commands, handle_clinical_commands, "Clinical Formulas & Bedside Calculators", "clinical")
