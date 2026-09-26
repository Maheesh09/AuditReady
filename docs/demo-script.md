# Demo script (our North Star)

Target: **3 minutes live, on the deployed app.** If a feature is not in this script, it is not built before feature freeze (Day 17).

| Step | Time | What the judge sees | Feature it proves |
|---|---|---|---|
| 1 | 0:00 | Log in as Lotus Apparel. Dashboard shows "0 documents". | Auth, empty state |
| 2 | 0:15 | Drag in 8 documents at once (fire certificate photo, scanned audit report, payroll spreadsheet, two utility bills, others). Progress bars run. | Upload, async processing |
| 3 | 0:45 | Documents turn green, amber or red. Review Queue: fire certificate expiry read at 71% confidence, highlighted on the original image. Confirm in one click. | Confidence tiers, human review, source highlight |
| 4 | 1:15 | Payroll card: "Original deleted after processing. SHA-256: 3f9a…". Worker names masked. | Keep the fact, not the file |
| 5 | 1:35 | "Demo Buyer SAQ" → **Generate answers**. Answers in about 30 s. | Answer generation |
| 6 | 2:05 | Click "Is the fire safety certificate valid?": citation opens the exact page, value highlighted. Click a question with no evidence: "No evidence found" plus which document to upload. | Citations, honest abstention |
| 7 | 2:30 | Gap Dashboard: "Boiler inspection certificate expires in 23 days", "Wage records missing for March". | Early warnings |
| 8 | 2:45 | Access log shows every view. Log in as the second factory: sees none of Lotus's data. Export SAQ to Excel. | Access log, isolation, export |

## Planted problems in the demo data

- Fire certificate photo is blurry and slightly rotated (low-confidence date).
- Boiler certificate expires 23 days after demo day.
- March missing from payroll records.
- ISO certificate with expiry before issue date (rule violation R01).
- No grievance policy uploaded ("No evidence found" for PO-01).
