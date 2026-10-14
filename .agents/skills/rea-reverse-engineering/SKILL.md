---
name: rea-reverse-engineering
description: "Master reverse engineering skill powered by morluto/rea (Reverse Engineer Anything v6.5). Provides comprehensive workflows to decompile APKs, Electron ASAR apps, native binaries, and inspect network PCAP captures using Ghidra, Hopper, IDA, JADX, and AST reconstructions."
risk: low
source: "morluto/rea (MIT)"
date_added: "2026-10-15"
---

# 🔬 REA (Reverse Engineer Anything) — Autonomous Decompilation Skill

## Overview
Powered by `morluto/rea`, this skill allows AI agents to inspect, trace, and reverse-engineer local software targets without requiring the original source code. Rather than speculative code generation, it extracts deterministic **Evidence Graphs, AST layouts, and byte patterns**.

---

## 🛠️ Core Command Playbook

### 1. JavaScript & Electron Application Decompilation
Unpack local Electron desktop apps or minified JavaScript bundles into readable AST graphs:
```bash
npx -y rea-agents@latest analyze-javascript-application <path-to-extracted-app> --json
```

### 2. Android APK Decompilation & Manifest Analysis
Extract and inspect Android application classes, activities, and manifest declarations:
```bash
# Inspect package metadata & activities
npx -y rea-agents@latest inspect-android-package <path-to-apk>

# Decompile specific class members
npx -y rea-agents@latest inspect-android-class <path-to-apk> <class-name>

# Decode resources, layouts, and strings via apktool
npx -y rea-agents@latest decode-android-resources <path-to-apk>
```

### 3. Network Traffic Packet Inspection (PCAP/HAR)
Analyze recorded network captures for hidden APIs, TLS SNI, and endpoints:
```bash
npx -y rea-agents@latest inspect-pcap-capture <path-to-capture.pcap>
```

### 4. Binary Disassembly & Layout Triage
Inspect native Windows PE or Linux ELF binaries:
```bash
# Inspect headers, sections, and symbol table
npx -y rea-agents@latest inspect-binary-layout <path-to-binary>

# Read raw instructions
npx -y rea-agents@latest instructions <path-to-binary> --address <hex-addr>
```
