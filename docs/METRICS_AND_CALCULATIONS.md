# MediPick Master Business Metrics & Calculations

This master document specifies the mathematical formulations, statutory limits, and Finite State Machine (FSM) rules applied across MediPick.

---

## 1. Prescription Order Finite State Machine (FSM)

```text
[PENDING] ──(Pharmacist Quote)──> [QUOTED] ──(Customer Accepts & Pays)──> [CONFIRMED]
    │                                │                                        │
    └──(Reject / Ineligible)──> [REJECTED] ──(Quote Expired: 15m)──> [CANCELLED]    └──(Dispensary Packs)──> [PREPARING]
                                                                                               │
                                                                                 [COMPLETED] <──(Dispensed/Picked Up)──┘
```

### FSM Timer Constraints & Statutory SLAs:
* **Quote Validity Window (`QUOTE_VALIDITY_MINUTES`):** **15 minutes**. If a customer does not accept within 15 minutes, the quote transitions to `CANCELLED`.
* **AI Clarity Pass Threshold (`AI_CLARITY_PASS_SCORE`):** **60 / 100**. Prescriptions scoring below 60 are automatically flagged for recapture.
* **Pharmacist Verification SLA:** Target response time **< 10 minutes** during operational dispensary hours.

---

## 2. Financial Metrics & Formulas

### A. Gross Merchandise Value (GMV)
$$\text{GMV} = \sum_{i=1}^{N} \text{OrderTotal}_i \quad \forall \, \text{status} = \text{'COMPLETED'}$$

### B. Dispensary Net Payout
MediPick applies a configurable platform service commission (default: 5%):
$$\text{PlatformFee} = \text{GMV} \times 0.05$$
$$\text{DispensaryPayout} = \text{GMV} - \text{PlatformFee}$$

### C. Government MRP Ceiling Compliance
Sri Lanka National Medicines Regulatory Authority (NMRA) enforces Maximum Retail Price (MRP) ceilings:
$$\text{QuotePrice} \le \text{NMRA\_MRP\_Ceiling}$$
*Quotes submitted above statutory MRP are rejected automatically with a 400 VALIDATION error.*

---

## 3. Inventory & Stock Health Metrics

### A. Stock Turnover Rate
$$\text{StockTurnover} = \frac{\text{Cost of Goods Sold (COGS)}}{\text{Average Inventory Value}}$$

### B. Stock Health Status Flags
* **`OUT_OF_STOCK`**: $\text{AvailableQuantity} = 0$
* **`LOW_STOCK`**: $0 < \text{AvailableQuantity} \le \text{ReorderLevel}$ (Default reorder level: 10 units)
* **`IN_STOCK`**: $\text{AvailableQuantity} > \text{ReorderLevel}$

---

## 4. Haversine Geographic Distance (Pharmacy Discovery)

Used in customer catalog to sort open pharmacies by physical distance from customer GPS coordinates:
$$d = 2r \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
* Where $r = 6,371 \text{ km}$ (Earth radius).
* Filter: Only pharmacies with $\text{isOpen} = \text{true}$ within the pharmacy's configured $\text{deliveryRadiusKm}$ are shown for delivery.
