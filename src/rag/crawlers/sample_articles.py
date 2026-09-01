"""
Sample real financial articles
In production, these would be crawled from real sources.
For demo, we use representative content.
"""

SAMPLE_ARTICLES = [
    # ===== VIETNAM (5) =====
    {
        "title": "VNM Report Q3 2024: Revenue Growth 8%",
        "source": "CafeF.vn",
        "url": "https://cafef.vn/vnm-q3-2024",
        "country": "Vietnam",
        "content": """
Vinamilk (VNM) Q3 2024 Financial Report

Revenue: VND 16,200 billion (+8% YoY)
Net Profit: VND 2,750 billion (+12% YoY)
EPS: VND 4,200 (vs VND 3,750 in Q3 2023)
Gross Margin: 47.5% (vs 45.2% YoY)

Key Highlights:
- Domestic milk sales grew 10%, driven by premium products
- Export revenue increased 15% to VND 3,200 billion
- New product launches in condensed milk and yogurt segments
- Distribution expansion in rural areas

Outlook:
Management expects 2024 full year revenue growth of 6-8%.
Dividend payout ratio maintained at 50% of net profit.
""",
    },
    {
        "title": "FPT Report: AI Services Drive Growth",
        "source": "Vietstock.vn",
        "url": "https://vietstock.vn/fpt-ai-services",
        "country": "Vietnam",
        "content": """
FPT Corporation (FPT) Q3 2024 Update

Revenue: VND 14,500 billion (+19% YoY)
Net Profit: VND 1,980 billion (+22% YoY)
AI Services Revenue: VND 1,200 billion (+85% YoY)

Key Segments:
- IT Services: VND 8,200 billion (+15% YoY)
- Telecommunications: VND 3,800 billion (+8% YoY)
- Education: VND 1,500 billion (+12% YoY)
- AI & Cloud: VND 1,000 billion (+90% YoY)

Strategic Initiatives:
- Partnership with NVIDIA for AI infrastructure
- Expansion in Japan and South Korea markets
- New data center in Ho Chi Minh City
- Investment in generative AI research

2024 Guidance:
Revenue growth: 18-20%
AI services to contribute 15% of total revenue
""",
    },
    {
        "title": "VCB Q3 2024: Credit Growth Strong",
        "source": "VnEconomy.vn",
        "url": "https://vneconomy.vn/vcb-q3-2024",
        "country": "Vietnam",
        "content": """
Vietcombank (VCB) Q3 2024 Results

Total Assets: VND 1,850 trillion (+12% YoY)
Net Profit: VND 9,800 billion (+15% YoY)
ROE: 22.5% (vs 21.0% YoY)
NIM: 3.85% (vs 3.92% YoY)

Key Metrics:
- Credit Growth: 11.2% YTD
- Deposit Growth: 8.5% YTD
- NPL Ratio: 0.95% (very low)
- CAR: 13.2% (well above 8% requirement)
- CASA Ratio: 45.3%

Strategic Focus:
- Digital banking transformation
- SME lending expansion
- Green credit initiatives
- Fee income growth from bancassurance

Dividend:
- Cash dividend VND 1,200/share
- Stock dividend ratio 100:18
""",
    },
    {
        "title": "VIC: Vinhomes Sales Strong",
        "source": "CafeF.vn",
        "url": "https://cafef.vn/vic-vinhomes",
        "country": "Vietnam",
        "content": """
Vingroup (VIC) Q3 2024 Update

Revenue: VND 38,500 billion (+15% YoY)
Net Profit: VND 1,250 billion (vs VND 850 billion YoY)

Vinhomes (VHM) Performance:
- New contracts: VND 28,500 billion
- Delivered: 8,200 units
- Average selling price: VND 45 million/sqm

VinFast Updates:
- Delivered 15,800 EVs in Q3
- New factory in Hai Phong operational
- Expansion to Indonesia and Philippines

Strategic Direction:
- Focus on Vinhomes and VinFast as growth drivers
- Reduce non-core assets
- Capital raising plan: USD 1.5 billion

Outlook 2024:
- Real estate recovery expected to continue
- EV business break-even target: 2025
""",
    },
    {
        "title": "HPG: Steel Demand Recovery",
        "source": "Vietstock.vn",
        "url": "https://vietstock.vn/hpg-steel",
        "country": "Vietnam",
        "content": """
Hoa Phat Group (HPG) Q3 2024 Report

Revenue: VND 32,500 billion (+18% YoY)
Net Profit: VND 2,800 billion (+85% YoY)
Gross Margin: 18.5% (vs 12.3% YoY)

Production:
- Crude steel: 2.5 million tons (+20% YoY)
- Construction steel: 2.2 million tons (+15% YoY)
- Hot-rolled coil: 850,000 tons (new product)

Key Drivers:
- Strong construction demand from public investment
- Real estate market recovery
- Export volume up 25%

New Projects:
- Dung Quat 2 steel complex: 5.6 million tons capacity
- Dung Quat battery project: 1 million EV batteries/year
- Container manufacturing: 500,000 TEU/year

2024 Guidance:
Revenue: VND 130 trillion (+12% YoY)
Earnings: VND 12 trillion
""",
    },
    # ===== INTERNATIONAL (5) =====
    {
        "title": "Apple Q4 2024: iPhone Sales Strong",
        "source": "Reuters.com",
        "url": "https://reuters.com/apple-q4-2024",
        "country": "USA",
        "content": """
Apple Inc. (AAPL) Q4 FY2024 Results

Revenue: $94.9 billion (+6% YoY)
Net Income: $14.7 billion
EPS: $0.97 (vs $0.94 YoY)

Segment Performance:
- iPhone: $46.2 billion (+5% YoY)
- Mac: $7.7 billion (+2% YoY)
- iPad: $7.0 billion (+25% YoY)
- Wearables: $9.0 billion (-3% YoY)
- Services: $25.0 billion (+12% YoY)

Geographic:
- Americas: $42.6 billion
- Europe: $24.8 billion
- Greater China: $15.0 billion (-8% YoY)
- Japan: $6.7 billion
- Rest of Asia: $5.8 billion

AI Strategy:
- Apple Intelligence rollout in iOS 18
- Partnership with OpenAI for ChatGPT integration
- New M4 chip with neural engine upgrades

2025 Outlook:
Services growth expected 14-16%
iPhone 17 cycle expected to be strong
""",
    },
    {
        "title": "Nvidia Q3 2024: AI Chip Demand Soars",
        "source": "YahooFinance.com",
        "url": "https://finance.yahoo.com/nvidia-q3-2024",
        "country": "USA",
        "content": """
Nvidia Corporation (NVDA) Q3 FY2025 Results

Revenue: $35.1 billion (+94% YoY)
Data Center Revenue: $30.8 billion (+112% YoY)
Net Income: $19.3 billion
EPS: $0.78 (vs $0.40 YoY)

Segment Breakdown:
- Data Center: $30.8B (+112%)
- Gaming: $3.3B (+15%)
- Professional Visualization: $0.5B (+7%)
- Automotive: $0.4B (+72%)

Key Products:
- H100 GPU: Strong demand from cloud providers
- H200: New generation ramping up
- Blackwell B200: Production started
- Grace CPU: Growing adoption

Customers:
- Microsoft Azure: 23% of data center
- Meta: 19%
- Google Cloud: 16%
- Amazon AWS: 12%

2025 Outlook:
Blackwell architecture expected to drive next growth cycle
Supply constraints may persist into 2025
""",
    },
    {
        "title": "Tesla Q3 2024: Margin Pressure",
        "source": "Bloomberg.com",
        "url": "https://bloomberg.com/tesla-q3-2024",
        "country": "USA",
        "content": """
Tesla Inc. (TSLA) Q3 2024 Results

Total Revenue: $25.2 billion (+8% YoY)
Automotive Revenue: $20.0 billion
Net Income: $2.2 billion
EPS: $0.62 (vs $0.53 YoY)
Gross Margin: 17.1% (vs 18.7% YoY)

Deliveries:
- Total: 462,890 vehicles (+6% YoY)
- Model 3/Y: 443,668
- Model S/X: 19,222
- Cybertruck: 16,260

Energy Business:
- Storage deployments: 6.9 GWh (+73% YoY)
- Revenue: $2.4 billion
- Gross margin improving

Challenges:
- Price cuts in China affecting margins
- FSD (Full Self-Driving) delays
- Cybertruck production ramp-up

2025 Outlook:
- Affordable model launch in 2025
- Robotaxi unveil expected
- Optimus robot production target
""",
    },
    {
        "title": "Microsoft Cloud Growth Strong",
        "source": "CNBC.com",
        "url": "https://cnbc.com/microsoft-cloud-q1-2025",
        "country": "USA",
        "content": """
Microsoft Corporation (MSFT) Q1 FY2025 Results

Revenue: $65.6 billion (+16% YoY)
Operating Income: $30.6 billion (+24% YoY)
Net Income: $24.7 billion
EPS: $3.23 (vs $2.94 YoY)

Segment Performance:
- Productivity & Business Services: $28.2B (+12% YoY)
  - Office 365: +16% growth
  - LinkedIn: +10% growth
- Intelligent Cloud: $24.1B (+20% YoY)
  - Azure: +33% growth (constant currency)
  - Server products: +3% growth
- More Personal Computing: $13.2B (+2% YoY)
  - Windows: +3% growth
  - Gaming: -1% growth

AI Highlights:
- Azure AI services revenue up 60%
- Copilot adoption growing in enterprise
- 400+ Fortune 500 companies using Copilot Studio

Capital Expenditure:
$20 billion in Q1 (mostly for AI infrastructure)
""",
    },
    {
        "title": "Toyota Q3 2024: Hybrid Sales Strong",
        "source": "Nikkei.com",
        "url": "https://nikkei.com/toyota-q3-2024",
        "country": "Japan",
        "content": """
Toyota Motor Corporation (TM) Q3 FY2024 Results

Revenue: ¥11.4 trillion (+8% YoY)
Operating Income: ¥1.16 trillion (+12% YoY)
Net Income: ¥0.85 trillion (+9% YoY)

Sales:
- Global vehicle sales: 2.7 million units (+5% YoY)
- Hybrid vehicles: 1.0 million units (+30% YoY)
- BEV (Battery EV): 50,000 units (+50% YoY)

Regional Performance:
- Japan: 600,000 units (+2% YoY)
- North America: 850,000 units (+8% YoY)
- Europe: 350,000 units (+5% YoY)
- Asia: 500,000 units (+10% YoY)

Strategy:
- Multi-pathway approach: HEV, PHEV, BEV, FCEV
- New BEV platform launching 2025
- Solid-state battery development
- Hydrogen fuel cell investments

Challenges:
- Chinese market competition
- Quality concerns in some markets
- Currency fluctuations (weak yen impact)

2025 Guidance:
Operating income: ¥4.3 trillion
""",
    },
]
