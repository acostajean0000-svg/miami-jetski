# Refstay — Monthly Reconciliation Workflow (Pilot Mode)

Cadence: **once per month, between the 1st and 5th**. Time required: ~30–45 minutes once you have 5–10 hosts.

This is your playbook for the manual phase. When you hit ~25 active hosts, we replace this with an automated backend. Until then, this routine is your entire ops layer.

---

## Day 1 — Pull the FareHarbor data

### Step 1.1 — Export the FHDN Bookings report

1. Log in to FareHarbor admin: https://fareharbor.com/dashboard/companies/miamistylerentals/ (or whatever your admin URL is)
2. Go to **Reports** → **Bookings** (or **FHDN Bookings** if shown separately for distribution partner)
3. Set date range: **previous month, 1st to last day** (e.g., on June 3rd you're pulling May 1 – May 31)
4. Filter by Online Booking Reference: contains `miamistylerentals-`
   - This grabs only bookings tied to a Refstay host. Bookings with `ref=miamistylerentals` alone (no suffix) are organic/partner-site bookings — those don't trigger host commissions.
5. Click **Export to CSV**
6. Save the file as `fh-bookings-YYYY-MM.csv` (e.g., `fh-bookings-2026-05.csv`) somewhere persistent (Google Drive folder "Refstay/Monthly Reports" recommended)

### Step 1.2 — Sanity check the export

Open the CSV. Confirm:

- Column **Online Booking Reference** is populated for every row and follows the format `miamistylerentals-<slug>`
- Column **Booking Total** (or **Amount**) shows the gross price
- Column **Status** is **confirmed** (or equivalent). Skip refunded/cancelled rows in your sum.
- No duplicate booking IDs

If a row has just `miamistylerentals` (no suffix), it's a non-Refstay booking — exclude it. If a row has a suffix you don't recognize, check your host list — it may be a test or a mistake.

---

## Day 2 — Calculate per-host commissions

### Step 2.1 — Open the CSV in Google Sheets

1. Upload `fh-bookings-YYYY-MM.csv` to Google Sheets
2. Add three new columns at the right:
   - **Host slug**: formula `=MID(B2, LEN("miamistylerentals-")+1, 100)` (assuming column B is the Online Booking Reference)
   - **Status filter**: keep only rows where status = `confirmed` (delete or hide the rest)
   - **Commission**: formula `=ROUND(F2*0.05, 2)` (where F is the booking total column)

### Step 2.2 — Pivot by host

1. Select the data → Insert → Pivot table → New sheet
2. Rows: `Host slug`
3. Values:
   - `Booking ID` → COUNT (this gives # bookings per host)
   - `Booking Total` → SUM
   - `Commission` → SUM
4. You now have one row per host showing: bookings, gross sales, your 5% to pay them

Save the sheet as `refstay-payouts-YYYY-MM.xlsx`.

### Step 2.3 — Cross-check with your host registry

Open your host registry (the Google Sheet from `host_outreach_kit.md` section 4). For each slug in the pivot, confirm:

- The slug matches a host who's actually signed up
- You have their payout method (PayPal email or Zelle phone)
- They're not in a "do not pay" state (e.g., suspended for fraud — unlikely at 5 hosts, but build the muscle now)

Flag any slug you can't match. Two common causes:
- A guest typed the URL wrong (e.g., `refstay.com/r/jonh-x4k2` instead of `john-x4k2`) — usually safe to attribute to the closest match if obvious
- Someone tested with a fake slug — exclude from payouts

---

## Day 3 — Send host reports

### Step 3.1 — Email template per host

For each host with at least 1 booking, send this email (replace the bracketed bits):

> Subject: Refstay May 2026 report — you earned $[X]
>
> Hey [First name],
>
> Your May 2026 booking report:
>
> - Bookings through your link: **[N]**
> - Total guest spend: **$[Y]**
> - Your 5% commission: **$[X]**
>
> Payment of **$[X]** sent today via [PayPal/Zelle] to [their email/phone].
>
> The booking detail is in the attached CSV — every guest who clicked your link and completed a booking.
>
> Thanks for being one of the early Refstay hosts. Reply if anything looks off.
>
> — Jean
> refstay.com

Attach a per-host CSV (just the rows for that slug — easy filter in the pivot).

For hosts with **zero bookings**, send a different note:

> Subject: Refstay May 2026 — no bookings this month
>
> Hey [First name],
>
> No bookings came through your link in May. A few thoughts:
>
> - Is your link still placed in your welcome book / WhatsApp / Instagram bio?
> - If yes, try adding a one-line nudge in your check-in message: "Want to book a jet ski or yacht? Tap here: refstay.com/r/[slug]"
> - I can send you a QR-code sticker PNG if you want guests to scan it from a printed welcome book — just reply.
>
> Most hosts see their first booking within 2–4 weeks of placing the link. Hang in there.
>
> — Jean

This is critical — silence kills the relationship. Even zero-booking hosts get a personal note every month.

### Step 3.2 — Track sends

In your host registry, add columns: `2026-05 paid amount`, `2026-05 paid date`, `2026-05 notes`. Fill them in as you send.

---

## Day 4 — Pay everyone

### Step 4.1 — Batch the payouts

Use PayPal or Zelle in a single session, not piecemeal. Less context-switching = fewer mistakes.

- **PayPal**: PayPal Business → Send → "Send to many people" (allows CSV upload of 1,000 recipients in one batch). Free for friends/family in US, ~2% fee for goods/services.
- **Zelle**: one at a time. Free. US bank required on both sides.

Use the **same payment ID** as the email reference so the host can match the deposit to your report.

### Step 4.2 — Confirm in your tracker

For each host, mark `paid date = today's date` in your registry. Also note the PayPal/Zelle transaction reference.

### Step 4.3 — Reconcile with your books

Add a row to your monthly P&L:

| Month | Gross bookings (via Refstay hosts) | Your 15% (from FareHarbor) | Host payouts (5%) | Net to you (10%) |
|-------|-------------------------------------|-----------------------------|--------------------|------------------|
| 2026-05 | $1,200 | $180 | $60 | $120 |

This is the number you actually need to watch. If "Net to you" is consistently above your cost to run Refstay (Vercel + Formspree + Plausible = roughly $0–$30/month for now), you're profitable.

---

## Day 5 — Update host registry, reset for next month

1. In your registry: mark this month as complete
2. Schedule the next reconciliation reminder for the 1st of next month
3. Spot-check: any hosts inactive for 2+ months? Send a gentle re-engagement message before assuming they're dead
4. Spot-check: any hosts trending up? Note them — these are your case studies and future testimonials

---

## When something goes wrong

### Booking total doesn't match expected (e.g., partial refund)
The CSV reflects gross at booking time. If FareHarbor refunded a portion later, the CSV may overstate. Use FareHarbor's "Settled Amount" column if available, otherwise verify big-ticket items by clicking through to the booking page.

### Slug appears that you can't match to a host
Save it. Don't pay anyone for it. Add to a "mystery slugs" tab. If it keeps appearing, someone is sharing a link you haven't formally onboarded — investigate.

### A host disputes their number
Send them the per-host CSV with booking IDs. They can verify the bookings against guest names if they kept records. Settle in their favor for amounts under $20 — the trust is worth more than the dispute.

### FareHarbor reporting changes the column names
Recheck the CSV headers. The formulas above assume column B = Online Booking Reference. Adjust the `MID()` formula if FareHarbor adds/removes columns.

---

## Tooling shortcuts (optional)

Once you have 10+ hosts and run this 3+ times, build these helpers:

1. **A Google Sheets template** with the pivot + formulas pre-built. You drop the CSV in tab 1, the report appears in tab 2.
2. **A Python script** that takes the CSV and emails per-host reports using SendGrid or AWS SES. 50 lines of code.
3. **A PayPal Mass Pay CSV** generator — automatic export from the pivot table in PayPal's expected format.

Don't build these on day one. Run the manual process 3 times first so you know what shape the helpers need to take.

---

## When to graduate to a real backend

Trigger to switch from this manual workflow to a Supabase/Airtable backend:

- 25+ active hosts (manual reconciliation takes more than 90 min/month) **or**
- Hosts are asking for real-time dashboard data more than 2x/month **or**
- A host catches a mistake in your monthly numbers (means the manual error rate is too high to scale)

When any of those hits, the next build is:
1. Real auth (Supabase Auth)
2. A FareHarbor data import script that runs daily and writes to a `bookings` table keyed by slug
3. A live dashboard that queries Supabase and shows real numbers
4. Stripe Connect for automated payouts

Estimated build: 1–2 weekends if you do it focused.
