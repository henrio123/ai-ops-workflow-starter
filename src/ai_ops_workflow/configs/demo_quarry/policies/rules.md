# demo_quarry policy and rule snippets (SYNTHETIC)

All snippets below are invented for the demo. The operator "Demo Kruusakarjaar
OU", the prices, and the limits are fictional. These seed the pgvector store;
each has a source id used for citation in the decision output. See
docs/data-privacy.md.

## PRICE-01 Minimum load
Minimum billable load is 5 tonnes. Orders below 5 t are revised up to the
minimum, or escalated if the customer declines.

## DELIV-02 Delivery radius
Standard delivery radius is 40 km from the quarry. Beyond 40 km a surcharge
applies and the order is escalated for a manual quote.

## CREDIT-03 New customer credit
New customers ordering above 200 tonnes must be on prepayment. Otherwise the
order is escalated for a credit check before confirmation.

## PERMIT-04 Daily extraction cap
The daily extraction permit cap is 800 tonnes. Any order that would push the
day's committed volume over the cap is escalated.

## MAT-05 Stocked materials
The quarry stocks: 0-16 crushed gravel, 16-32 crushed gravel, 0-4 sand, and
fill material. Requests for a grade not on this list are revised to the nearest
available grade.
