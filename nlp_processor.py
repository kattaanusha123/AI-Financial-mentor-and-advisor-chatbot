"""
NLP Processor Module
Handles natural language understanding and response generation
"""
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import random

# Check for required NLTK data but avoid blocking automatic downloads at import time.
# If corpora are missing, fall back to safe defaults so the app doesn't stall.
has_punkt = True
has_stopwords = True
has_wordnet = True
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    has_punkt = False
    print('NLTK punkt tokenizer not found; falling back to simple split tokenization.')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    has_stopwords = False
    print('NLTK stopwords corpus not found; continuing with empty stopword set.')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    has_wordnet = False
    print('NLTK wordnet corpus not found; lemmatization will be a no-op.')

# Fallbacks
if has_wordnet:
    lemmatizer = WordNetLemmatizer()
else:
    class _NoOpLemmatizer:
        def lemmatize(self, token):
            return token
    lemmatizer = _NoOpLemmatizer()

if has_stopwords:
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        stop_words = set()
else:
    stop_words = set()

def _tokenize(text):
    """Tokenize text using NLTK if available, otherwise fallback to simple split."""
    if has_punkt:
        try:
            return word_tokenize(text)
        except Exception:
            return text.split()
    return text.split()

class NLPProcessor:
    def __init__(self):
        # Financial knowledge base with detailed explanations
        self.financial_terms = {
            'sip': """**SIP (Systematic Investment Plan)** is a smart investment strategy that allows you to invest a fixed amount regularly (usually monthly) in mutual funds.

**Key Features:**
• **Regular Investments**: You invest a fixed amount monthly, weekly, or quarterly
• **Discipline**: Helps build a disciplined investment habit
• **Rupee Cost Averaging**: You buy more units when prices are low and fewer when prices are high
• **Flexibility**: You can start with as little as ₹500 per month
• **Easy to Start**: Can be set up through banks, mutual fund companies, or online platforms

**Example**: If you invest ₹5,000 every month in a SIP, you're investing systematically regardless of market conditions, which helps average out the cost of your investments over time.

Would you like me to calculate how much you could accumulate with a SIP?""",
            
            'mutual fund': """**Mutual Funds** are investment vehicles that pool money from multiple investors to invest in a diversified portfolio of stocks, bonds, and other securities.

**How They Work:**
• Professional fund managers manage your money
• Your investment is divided into units (like shares)
• The fund's value changes based on the performance of underlying investments
• You can buy or sell units anytime (depending on the fund type)

**Types:**
• **Equity Funds**: Invest primarily in stocks (higher risk, higher returns)
• **Debt Funds**: Invest in bonds and fixed-income securities (lower risk, steady returns)
• **Hybrid Funds**: Mix of stocks and bonds
• **Index Funds**: Track specific market indices

**Benefits**: Diversification, professional management, and accessibility for small investors.

Would you like to know more about any specific type of mutual fund?""",
            
            'stocks': """**Stocks** (also called shares or equities) represent ownership in a company. When you buy a company's stock, you become a partial owner of that company.

**Key Concepts:**
• **Ownership**: Each share represents a small piece of ownership
• **Dividends**: Companies may pay shareholders a portion of profits
• **Price Appreciation**: Stock prices can increase over time
• **Volatility**: Stock prices can fluctuate based on market conditions

**How Stocks Work:**
1. Companies issue stocks to raise capital
2. You buy stocks through a broker or trading platform
3. You can hold them for dividends or sell them when prices increase
4. Stock performance depends on company performance and market conditions

**Risks**: Stock values can go down as well as up, so there's risk of losing your investment.

Would you like advice on how to start investing in stocks?""",
            
            'bonds': """**Bonds** are debt securities where you lend money to a company or government entity in exchange for regular interest payments and return of principal at maturity.

**How They Work:**
• You lend money (principal) to the issuer
• The issuer pays you interest periodically (usually fixed rate)
• At maturity, you get back your principal
• Generally considered lower risk than stocks

**Types:**
• **Government Bonds**: Issued by the government (very safe, lower returns)
• **Corporate Bonds**: Issued by companies (higher risk, higher returns)
• **Municipal Bonds**: Issued by local governments

**Benefits**: Fixed income, predictable returns, lower risk than stocks
**Risks**: Interest rate risk, credit risk (default), inflation risk

Bonds are good for conservative investors seeking steady income.""",
            
            'fd': """**Fixed Deposit (FD)** is a financial instrument where you deposit money for a fixed period at a predetermined interest rate.

**Key Features:**
• **Fixed Interest Rate**: Rate is locked in when you open the FD
• **Fixed Tenure**: You choose the duration (usually 7 days to 10 years)
• **Safety**: Very safe investment, typically insured up to certain limits
• **Guaranteed Returns**: Unlike stocks, returns are predictable

**How It Works:**
1. You deposit a lump sum amount
2. Choose a tenure (how long to keep the money)
3. Earn fixed interest for that period
4. Get your principal + interest at maturity

**Benefits**: Safe, guaranteed returns, no market risk
**Limitations**: Lower returns than stocks/mutual funds, money is locked in, premature withdrawal may have penalties

FDs are ideal for risk-averse investors who want guaranteed returns.""",
            
            'rd': """**Recurring Deposit (RD)** allows you to invest a fixed amount monthly for a fixed period, earning interest on your deposits.

**Key Features:**
• **Monthly Deposits**: Invest a fixed amount every month
• **Fixed Tenure**: Choose duration (typically 6 months to 10 years)
• **Compound Interest**: Interest compounds quarterly
• **Discipline**: Helps build a regular savings habit

**How It Works:**
1. Choose monthly deposit amount (e.g., ₹5,000)
2. Select tenure (e.g., 12 months)
3. Bank automatically deducts the amount each month
4. At maturity, you receive all deposits + accumulated interest

**Benefits**: Regular savings habit, safe investment, guaranteed returns, flexibility in deposit amount
**Limitations**: Lower returns than mutual funds, money locked until maturity

RDs are great for people who want to save regularly with guaranteed returns.""",
            
            'ppf': """**Public Provident Fund (PPF)** is a long-term savings scheme with tax benefits, backed by the Government of India.

**Key Features:**
• **Tax Benefits**: Investments qualify for deductions under Section 80C (up to ₹1.5 lakh/year)
• **Tax-Free Returns**: Interest earned is tax-free
• **Long-Term**: Minimum 15 years, can be extended
• **Safety**: Backed by the government, very safe

**How It Works:**
1. Open a PPF account at any bank or post office
2. Deposit minimum ₹500 to maximum ₹1.5 lakh per year
3. Earn interest (currently around 7-8% annually, set by government)
4. Interest compounds annually
5. Can withdraw partially after 6 years in case of emergencies

**Benefits**: Tax savings, safe investment, good long-term returns, retirement planning
**Limitations**: Long lock-in period, limited withdrawal options

PPF is excellent for retirement planning and long-term wealth building with tax advantages.""",
            
            'emi': """**EMI (Equated Monthly Installment)** is a fixed payment amount made by a borrower to a lender on a specified date each month to repay a loan.

**How EMIs Work:**
• **Fixed Amount**: You pay the same amount every month
• **Principal + Interest**: Each EMI includes both principal repayment and interest
• **Amortization**: Initially, most of the EMI goes to interest; over time, more goes to principal

**Factors Affecting EMI:**
• **Loan Amount**: Higher loan = higher EMI
• **Interest Rate**: Higher rate = higher EMI
• **Tenure**: Longer tenure = lower EMI (but more total interest paid)

**Example**: For a home loan of ₹50 lakhs at 8% interest for 20 years, your EMI would be around ₹41,822 per month.

**Benefits**: Predictable monthly payments, easier budgeting, spreads cost over time

Would you like me to calculate the EMI for a specific loan amount?""",
            
            'interest': """**Interest** is the cost of borrowing money or the return earned on invested money.

**Two Types:**

1. **Interest on Loans** (Cost):
   - The extra amount you pay when you borrow money
   - Example: If you borrow ₹1,00,000 at 10% interest, you pay ₹10,000 extra per year

2. **Interest on Investments** (Return):
   - The extra amount you earn on your savings/investments
   - Example: If you invest ₹1,00,000 at 8% interest, you earn ₹8,000 per year

**Simple Interest**: Calculated only on the principal amount
**Compound Interest**: Calculated on principal + accumulated interest (grows faster!)

**Key Concept**: When borrowing, you pay interest (cost). When saving/investing, you earn interest (return).

Would you like to calculate how much interest you could earn on an investment?""",
            
            'compound interest': """**Compound Interest** is interest calculated on both the principal amount and previously accumulated interest. It's often called "interest on interest" and is one of the most powerful concepts in finance!

**How It Works:**
Unlike simple interest (only on principal), compound interest grows exponentially because you earn interest on your interest.

**Example:**
• Invest ₹1,00,000 at 8% for 10 years
• **Simple Interest**: ₹1,80,000 (₹80,000 interest)
• **Compound Interest**: ₹2,15,892 (₹1,15,892 interest) - that's ₹35,892 more!

**The Magic of Compounding:**
• **Time is key**: The longer you invest, the more you benefit
• **Regular investments amplify it**: SIPs leverage compounding effectively
• **Albert Einstein** called it the "eighth wonder of the world"

**Rule of 72**: Divide 72 by your interest rate to know how many years it takes to double your money.
At 8%: 72 ÷ 8 = 9 years to double!

This is why starting investments early is so powerful - time + compound interest = wealth building.

Would you like me to calculate compound interest for your investment?""",
            
            'credit score': """**Credit Score** is a numerical representation (typically 300-850) of your creditworthiness - how reliable you are at repaying debts.

**Credit Score Ranges:**
• **750-850**: Excellent - best interest rates, easy loan approvals
• **700-749**: Good - favorable terms
• **650-699**: Fair - may get higher interest rates
• **Below 650**: Poor - difficulty getting loans, very high rates

**Factors Affecting Credit Score:**
• **Payment History** (35%): Do you pay on time?
• **Credit Utilization** (30%): How much credit do you use vs. available?
• **Credit History Length** (15%): How long you've had credit
• **Credit Mix** (10%): Types of credit (cards, loans, etc.)
• **New Credit** (10%): Recent credit inquiries

**How to Improve:**
• Pay bills on time
• Keep credit card balances low
• Don't close old accounts
• Limit new credit applications
• Check your credit report regularly

A good credit score saves you money through better loan rates!

Would you like tips on improving your credit score?""",
            
            'diversification': """**Diversification** is the investment strategy of spreading your money across different types of assets, sectors, or investments to reduce risk.

**The Principle:**
"Don't put all your eggs in one basket"

**Why It Matters:**
• If one investment performs poorly, others may perform well
• Reduces overall portfolio risk
• Helps achieve more stable returns

**Ways to Diversify:**
1. **Asset Types**: Stocks, bonds, real estate, gold, cash
2. **Sectors**: Technology, healthcare, finance, consumer goods
3. **Geographic**: Indian stocks, international stocks
4. **Company Size**: Large-cap, mid-cap, small-cap stocks

**Example Portfolio:**
• 40% Equity Mutual Funds (stocks)
• 30% Debt Funds (bonds)
• 20% Fixed Deposits
• 10% Gold

**Benefits**: Lower risk, smoother returns, protection against market volatility

Diversification doesn't guarantee profits, but it's a smart risk management strategy!

Would you like help creating a diversified investment portfolio?""",
            
            'inflation': """**Inflation** is the rate at which the general level of prices for goods and services rises, reducing purchasing power over time.

**In Simple Terms:**
If inflation is 5%, something that costs ₹100 today will cost ₹105 next year. Your money buys less!

**Real-World Impact:**
• Your ₹1,00,000 today might only buy what ₹95,000 could buy next year (at 5% inflation)
• This is why keeping money idle loses value over time

**How to Beat Inflation:**
• **Invest, don't just save**: Savings accounts typically earn less than inflation
• **Equity investments**: Historically beat inflation over long term
• **Diversified portfolio**: Mix of stocks, bonds, and other assets
• **Real returns matter**: 8% return with 5% inflation = 3% real return

**Inflation in India:**
Typically 4-6% per year, so your investments should aim for higher returns to grow your wealth in real terms.

**Key Insight**: Your money needs to grow faster than inflation to maintain and increase purchasing power!

Would you like help planning investments that beat inflation?""",
            
            'asset': """**Assets** are anything of value that you own and can be converted into cash or used to generate income.

**Types of Assets:**

1. **Liquid Assets**: Cash, savings accounts, money market funds (easily accessible)

2. **Investment Assets**: 
   • Stocks and mutual funds
   • Bonds and fixed deposits
   • Real estate properties

3. **Physical Assets**: 
   • Real estate (your home, rental properties)
   • Gold, jewelry
   • Vehicles, equipment

4. **Intangible Assets**: 
   • Patents, trademarks
   • Intellectual property

**Assets vs. Expenses:**
• **Asset**: Puts money in your pocket (rental property, dividend stocks)
• **Liability/Expense**: Takes money out (loans, credit card debt)

**Net Worth Calculation:**
Net Worth = Total Assets - Total Liabilities

**Good Financial Practice**: Focus on building assets that generate income or appreciate in value!

Would you like advice on building your asset portfolio?""",
            
            'liability': """**Liabilities** are debts or financial obligations you owe to others. They represent money you need to pay back.

**Common Types:**
• **Home Loan**: Money borrowed to buy a house
• **Car Loan**: Loan for vehicle purchase
• **Credit Card Debt**: Unpaid credit card balances
• **Personal Loans**: Loans for various purposes
• **Student Loans**: Education financing
• **Mortgages**: Property loans

**Good vs. Bad Liabilities:**

**Good Liabilities** (can create value):
• Home loan (builds equity in an appreciating asset)
• Business loan (can generate income)

**Bad Liabilities** (consume money):
• Credit card debt (high interest, no asset)
• Personal loans for consumption
• Car loan (depreciating asset)

**Financial Health:**
• **Debt-to-Income Ratio**: Should be below 40%
• **Avoid high-interest debt**: Credit cards can charge 18-36%!
• **Pay off bad debts first**: Credit cards, personal loans
• **Use debt wisely**: For assets that appreciate or generate income

**Key Principle**: Minimize liabilities, especially high-interest debt, while building assets!

Would you like help creating a debt repayment strategy?"""
        }
        
        self.greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        self.calculation_keywords = ['calculate', 'compute', 'emi', 'interest', 'sip', 'investment', 'savings']
        self.greeting_responses = [
            "Hello! I'm your Financial Mentor. How can I help you with your finances today?",
            "Hi there! I'm here to guide you through your financial journey. What would you like to know?",
            "Greetings! I'm your 24/7 financial advisor. What financial topic can I help you with?",
            "Hello! Ready to make informed financial decisions? Ask me anything about finance!"
        ]
        
        self.motivational_quotes = [
            "The best time to plant a tree was 20 years ago. The second best time is now. - Start investing today!",
            "Don't save what is left after spending; spend what is left after saving. - Warren Buffett",
            "Budget is not just about numbers, it's about making your money work for you.",
            "Invest in yourself. Your career is the engine of your wealth. - Mark Cuban",
            "Financial freedom is available to those who learn about it and work for it. - Robert Kiyosaki",
            "Every dollar you save is a dollar you've earned. Make saving a habit!",
            "The goal isn't more money. The goal is living life on your terms. - Chris Brogan",
            "Wealth is not about having a lot of money; it's about having a lot of options. - Chris Rock"
        ]
    
    def preprocess_text(self, text):
        """Preprocess text for NLP analysis"""
        text = text.lower()
        tokens = _tokenize(text)
        tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalnum()]
        tokens = [token for token in tokens if token not in stop_words]
        return tokens
    
    def is_greeting(self, text):
        """Check if the input is a greeting"""
        text_lower = text.lower()
        return any(greeting in text_lower for greeting in self.greetings)
    
    def is_explanation_request(self, text):
        """Check if the input is asking for an explanation"""
        text_lower = text.lower()
        explanation_phrases = ['what is', 'what are', 'explain', 'tell me about', 'tell me', 'define', 'meaning of', 'what does', 'how does']
        return any(phrase in text_lower for phrase in explanation_phrases)
    
    def is_calculation_request(self, text):
        """Check if the input is explicitly requesting a calculation"""
        text_lower = text.lower()
        # Only treat as calculation if explicitly says calculate/compute or contains numbers
        explicit_calc_words = ['calculate', 'compute', 'work out', 'figure out', 'what will be', 'how much will']
        has_numbers = bool(re.search(r'\d+', text))
        return any(word in text_lower for word in explicit_calc_words) or (has_numbers and any(keyword in text_lower for keyword in ['emi', 'sip', 'interest', 'investment']))
    
    def extract_calculation_type(self, text):
        """Extract what type of calculation is needed"""
        text_lower = text.lower()
        if 'emi' in text_lower:
            return 'emi'
        elif 'sip' in text_lower:
            return 'sip'
        elif 'compound' in text_lower and 'interest' in text_lower:
            return 'compound_interest'
        elif 'simple' in text_lower and 'interest' in text_lower:
            return 'simple_interest'
        elif 'future value' in text_lower or 'savings' in text_lower:
            return 'future_value'
        return None
    
    def extract_numbers(self, text):
        """Extract numbers from text"""
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(num) for num in numbers]

    def parse_amount(self, text):
        """Parse a human-friendly amount from text like '5 lakh', '5 lakhs', '5k', '50,000', '₹5,00,000'"""
        t = text.lower().replace(',', '').replace('₹', '').strip()
        # look for patterns like '5 lakh', '5 lakhs', '5k', '50000'
        m = re.search(r'(\d+\.?\d*)\s*(lakh|lakhs|lac|k|thousand|crore|cr)?', t)
        if not m:
            # fallback to numeric extraction
            nums = self.extract_numbers(t)
            return nums[0] if nums else None

        val = float(m.group(1))
        unit = m.group(2)
        if not unit:
            return val
        unit = unit.lower()
        if unit in ('k', 'thousand'):
            return val * 1_000
        if unit in ('lakh', 'lakhs', 'lac'):
            return val * 100_000
        if unit in ('crore', 'cr'):
            return val * 10_000_00
        return val
    
    def find_financial_term(self, text):
        """Check if text contains any financial term"""
        text_lower = text.lower()
        for term, explanation in self.financial_terms.items():
            if term in text_lower:
                return term, explanation
        return None, None
    
    def infer_profile_from_history(self, user_history):
        """Infer simple profile attributes from past conversation history.
        Looks for age, risk tolerance (low/medium/high), and investment horizon (years).
        Returns dict with keys: age (int or None), risk ('low'|'medium'|'high' or None), horizon_years (int or None)
        """
        profile = {'age': None, 'risk': None, 'horizon_years': None}
        if not user_history:
            return profile

        history_text = ' '.join([ (h.get('query') or '') + ' ' + (h.get('response') or '') if isinstance(h, dict) else str(h) for h in user_history ])
        # Age patterns: "I'm 30", "age 30", "i am 30 years"
        m = re.search(r"\b(?:i\s+am|i'm|age)\s+(\d{2})\b", history_text.lower())
        if m:
            try:
                age = int(m.group(1))
                if 15 <= age <= 100:
                    profile['age'] = age
            except Exception:
                pass

        # Risk tolerance
        if re.search(r"\b(high|aggressive|very high)\b", history_text.lower()):
            profile['risk'] = 'high'
        elif re.search(r"\b(low|conservative|very low)\b", history_text.lower()):
            profile['risk'] = 'low'
        elif re.search(r"\b(medium|moderate|balanced)\b", history_text.lower()):
            profile['risk'] = 'medium'

        # Horizon: look for "X years", "long term", "short term"
        mh = re.search(r"(\d{1,2})\s*(?:years|yrs)\b", history_text.lower())
        if mh:
            try:
                yrs = int(mh.group(1))
                profile['horizon_years'] = yrs
            except Exception:
                pass
        else:
            if re.search(r"long term|long-term|longterm", history_text.lower()):
                profile['horizon_years'] = 7
            elif re.search(r"medium term|medium-term|mid term|mid-term", history_text.lower()):
                profile['horizon_years'] = 4
            elif re.search(r"short term|short-term|shortterm", history_text.lower()):
                profile['horizon_years'] = 2

        return profile


    # compute_personalized_allocation removed — portfolio suggestion feature reverted per user request

    def process_query(self, text, user_history=None):
        """Process user query and generate response"""
        response = {
            'type': 'general',
            'message': '',
            'calculation_type': None,
            'requires_calculation': False,
            'suggested_term': None
        }
        
        # Check for greeting - will be handled with language preference in app.py
        # Keep English greeting here, translation happens in app.py
        if self.is_greeting(text):
            response['message'] = random.choice(self.greeting_responses)
            response['type'] = 'greeting'
            return response
        
        text_lower = text.lower()
        
        # PRIORITY 1: Check for explanation requests FIRST (what is, explain, tell me about)
        if self.is_explanation_request(text):
            # Try to find the financial term being asked about
            term, explanation = self.find_financial_term(text)
            if term:
                response['message'] = explanation
                response['suggested_term'] = term
                response['type'] = 'explanation'
                return response
            else:
                # No specific term found, but it's an explanation request
                response['message'] = "I'd be happy to explain! Please mention the specific financial term or concept you'd like to learn about (e.g., SIP, mutual funds, stocks, bonds, EMI, FD, PPF, credit score)."
                response['type'] = 'question'
                return response
        
        # PRIORITY 2: Check for financial term explanation (even without "what is")
        term, explanation = self.find_financial_term(text)
        if term and len(text.split()) <= 5:  # Short queries like "sip", "what is sip", "explain sip"
            response['message'] = explanation
            response['suggested_term'] = term
            response['type'] = 'explanation'
            return response
        
        # PRIORITY 3: Check for explicit calculation request (with "calculate" or numbers)
        if self.is_calculation_request(text):
            calc_type = self.extract_calculation_type(text)
            if calc_type:
                response['type'] = 'calculation'
                response['calculation_type'] = calc_type
                response['requires_calculation'] = True
                # Provide helpful calculation message
                calc_examples = {
                    'emi': 'For EMI calculation, I need: loan amount (principal), interest rate (%), and loan tenure (months).\nExample: Calculate EMI for ₹10,00,000 at 8% for 20 years (240 months)',
                    'sip': 'For SIP calculation, I need: monthly investment amount, expected return rate (%), and investment period (years).\nExample: Calculate SIP of ₹5,000 per month at 12% return for 10 years',
                    'compound_interest': 'For compound interest, I need: principal amount, interest rate (%), and time period (years).\nExample: Calculate compound interest for ₹1,00,000 at 8% for 5 years',
                    'simple_interest': 'For simple interest, I need: principal amount, interest rate (%), and time period (years).\nExample: Calculate simple interest for ₹50,000 at 6% for 3 years'
                }
                response['message'] = f"I can help you calculate {calc_type.replace('_', ' ')}. {calc_examples.get(calc_type, 'Please provide the required parameters (e.g., principal, rate, time).')}"
            else:
                response['message'] = "I can help with financial calculations! Specify what you'd like to calculate: EMI, SIP, compound interest, simple interest, or future value.\n\nJust mention the calculation type along with the numbers, like: 'Calculate SIP for ₹5,000 at 12% for 10 years'"
            return response

        # PRIORITY 3.5: Investment guidance when user mentions an amount to invest
        amount = self.parse_amount(text)
        if amount and ('invest' in text_lower or 'how to invest' in text_lower or re.search(r"how\s+invest|how\s+to\s+invest|i\s+have\s+\d", text_lower)):
            response['type'] = 'advice'
            # Ask for profile details (age, horizon, risk) before making suggestions
            amt_str = f"₹{amount:,.0f}"
            response['message'] = (
                f"You have {amt_str} to invest. Please tell me your age, investment horizon (in years), and risk tolerance (low/medium/high) so I can advise appropriately.\n"
                "For example: 'I am 30 years old, horizon 10 years, risk medium'"
            )
            response['follow_up'] = True
            response['follow_up_question'] = "Please tell me your age, investment horizon (years), and risk tolerance (low/medium/high)."
            return response
        
        if 'how to' in text_lower and ('invest' in text_lower or 'save' in text_lower):
            response['message'] = """Here are some tips to start investing and saving:
1. **Set clear financial goals** - Define what you're saving for (emergency fund, retirement, house, etc.)
2. **Start with an emergency fund** - Save 3-6 months of expenses
3. **Understand your risk tolerance** - Younger investors can take more risks
4. **Start with SIPs** - Systematic Investment Plans are great for beginners
5. **Diversify your investments** - Don't put all eggs in one basket
6. **Learn continuously** - Financial education is an ongoing process
7. **Consult a financial advisor** for personalized advice

Would you like more details on any of these points?"""
            response['type'] = 'advice'
            return response
        
        if 'budget' in text_lower or 'expense' in text_lower:
            response['message'] = """Here's how to create a budget:
1. **Track your income** - Know how much you earn monthly
2. **List all expenses** - Categorize them (needs vs wants)
3. **Use the 50/30/20 rule**:
   - 50% for needs (rent, groceries, utilities)
   - 30% for wants (entertainment, dining out)
   - 20% for savings and investments
4. **Review and adjust** regularly
5. **Use budgeting apps** or spreadsheets to track

Would you like to create a personalized budget plan?"""
            response['type'] = 'advice'
            return response
        
        # Intelligent query understanding - handle general financial questions
        intelligent_response = self.generate_intelligent_response(text, text_lower)
        if intelligent_response:
            return intelligent_response
        
        # Last resort: Try to understand the query and provide helpful guidance
        response['message'] = self.understand_and_respond(text, text_lower)
        response['type'] = 'general'
        return response
    
    def generate_intelligent_response(self, text, text_lower):
        """Generate intelligent responses for common financial topics"""
        response = {
            'type': 'advice',
            'message': '',
            'calculation_type': None,
            'requires_calculation': False,
            'suggested_term': None
        }
        
        # Retirement planning
        if any(word in text_lower for word in ['retirement', 'pension', 'retire', 'old age', 'after 60']):
            response['message'] = """**Retirement Planning** is crucial for financial security in your golden years.

**Key Steps:**
1. **Start Early**: The earlier you start, the more you'll have. Thanks to compound interest!
2. **Calculate Your Needs**: Estimate 70-80% of your current income for retirement
3. **Save Consistently**: Aim to save 15-20% of your income for retirement
4. **Diversify Investments**: Mix of equity (for growth) and debt (for stability)
5. **Use Retirement Accounts**: PPF, EPF, NPS offer tax benefits
6. **Plan for Healthcare**: Medical costs increase with age - factor this in

**Common Retirement Options:**
• **PPF**: Tax benefits, guaranteed returns, 15-year lock-in
• **NPS**: National Pension System, market-linked returns
• **EPF**: Employee Provident Fund (for salaried employees)
• **Mutual Funds**: Equity funds for long-term growth
• **Annuities**: Regular income after retirement

**Rule of Thumb**: Save 25 times your annual expenses by retirement age.

Would you like help calculating how much you need to save for retirement?"""
            return response
        
        # Emergency fund
        if any(word in text_lower for word in ['emergency', 'rainy day', 'unexpected', 'urgent money', 'crisis fund']):
            response['message'] = """**Emergency Fund** is money set aside to cover unexpected expenses or financial setbacks.

**Why It's Important:**
• Covers unexpected medical expenses
• Handles job loss or income reduction
• Covers urgent repairs (home, car, appliances)
• Prevents taking high-interest loans
• Gives peace of mind

**How Much You Need:**
• **Minimum**: 3 months of expenses
• **Recommended**: 6 months of expenses
• **Conservative**: 12 months of expenses (if self-employed or unstable income)

**Where to Keep It:**
• **Savings Account**: Easily accessible, low interest
• **Liquid Mutual Funds**: Better returns, easy withdrawal
• **FD with auto-renewal**: Decent returns, accessible
• **Avoid**: Long-term investments, stocks (may be down when you need it)

**Example**: If your monthly expenses are ₹50,000:
• Minimum emergency fund: ₹1,50,000 (3 months)
• Recommended: ₹3,00,000 (6 months)

**Tip**: Build it gradually - start with ₹10,000-20,000, then add monthly until you reach your target!

Would you like help calculating your emergency fund requirement?"""
            return response
        
        # Tax saving
        if any(word in text_lower for word in ['tax', 'save tax', 'tax saving', 'income tax', '80c', 'tax deduction']):
            response['message'] = """**Tax Saving Strategies** help you legally reduce your tax liability and increase your savings.

**Popular Tax-Saving Options (Section 80C):**
• **ELSS Mutual Funds**: Equity Linked Savings Schemes - lock-in 3 years, potential high returns
• **PPF**: Public Provident Fund - 15 years, safe, tax-free interest
• **Life Insurance**: Term or traditional policies (min 5 years)
• **NSC**: National Savings Certificate - 5 years
• **FD (5-year)**: Tax-saving fixed deposit
• **Home Loan Principal**: Principal repayment qualifies
• **Tuition Fees**: Children's education fees
• **Limit**: ₹1.5 lakh per year

**Section 80D - Health Insurance:**
• Premium for self/family: ₹25,000 (₹50,000 for senior citizens)
• Parents' premium: Additional ₹25,000 (₹50,000 if senior)

**Section 24 - Home Loan Interest:**
• Up to ₹2 lakh deduction on home loan interest

**Section 80G - Donations:**
• Donations to approved charities/trusts

**Key Tips:**
1. **Invest early in the year**: Don't wait until March
2. **Choose growth assets**: ELSS for long-term wealth building
3. **Don't invest just for tax**: Consider returns too
4. **Plan systematically**: Spread investments throughout the year

**Remember**: Tax saving is bonus - focus on building wealth!

Would you like help planning your tax-saving investments?"""
            return response
        
        # Credit/Debt management
        if any(word in text_lower for word in ['credit card', 'debt', 'loan', 'borrow', 'owe', 'repay debt']):
            response['message'] = """**Debt Management** is crucial for financial health. Here's how to handle debts effectively:

**Types of Debt:**
• **Good Debt**: Home loan (appreciating asset), education loan (income potential)
• **Bad Debt**: Credit card debt, personal loans for consumption (high interest, no asset)

**Strategies to Manage Debt:**
1. **Prioritize High-Interest Debt**: Pay off credit cards first (18-36% interest!)
2. **Debt Snowball Method**: Pay minimum on all, extra on smallest debt first
3. **Debt Avalanche Method**: Pay minimum on all, extra on highest interest first
4. **Consolidate if Possible**: Combine multiple debts at lower rate
5. **Stop Using Credit Cards**: Until paid off completely

**Credit Card Best Practices:**
• Pay full balance monthly (avoid interest)
• If carrying balance, negotiate lower rate
• Don't use more than 30% of credit limit
• Never take cash advances (very high interest)

**Loan Management:**
• **Prepay if possible**: Reduces total interest paid
• **Refinance**: If interest rates drop, consider refinancing
• **Don't take loans for depreciating assets**: Cars, electronics

**Debt-to-Income Ratio:**
Keep it below 40%. Calculate: (Total monthly debt payments / Monthly income) × 100

**Warning Signs:**
• Paying minimums only
• Using one card to pay another
• Skipping payments
• Debt growing faster than income

**Action Plan**: List all debts, interest rates, minimum payments. Attack highest interest first!

Would you like help creating a debt repayment strategy?"""
            return response
        
        # Investment strategy
        if any(word in text_lower for word in ['investment strategy', 'where to invest', 'best investment', 'portfolio', 'asset allocation']):
            response['message'] = """**Investment Strategy** should be personalized based on your goals, risk tolerance, and time horizon.

**Asset Allocation by Age:**
• **20-30 years**: 70-80% equity, 20-30% debt (aggressive growth)
• **30-40 years**: 60-70% equity, 30-40% debt (balanced growth)
• **40-50 years**: 50-60% equity, 40-50% debt (moderate growth)
• **50+ years**: 30-40% equity, 60-70% debt (capital preservation)

**Investment Options for Different Goals:**

**Short-Term (1-3 years):**
• Fixed Deposits
• Liquid Mutual Funds
• Short-term debt funds
• Avoid: Stocks, equity funds (too volatile)

**Medium-Term (3-7 years):**
• Hybrid Mutual Funds
• Debt Funds
• Balanced Portfolio
• Some equity exposure (via mutual funds)

**Long-Term (7+ years):**
• Equity Mutual Funds (large-cap, mid-cap)
• Index Funds
• PPF, NPS
• Direct stocks (if experienced)

**Core Principles:**
1. **Diversify**: Don't put all money in one asset
2. **Start Early**: Time is your biggest advantage
3. **Invest Regularly**: SIP approach works well
4. **Review Annually**: Rebalance if needed
5. **Stay Disciplined**: Don't panic sell during market downturns

**Example Portfolio (Age 30, Moderate Risk):**
• 40% Large-cap equity funds
• 20% Mid-cap equity funds
• 20% Debt funds/FD
• 10% Gold
• 10% International equity

**Remember**: Past performance doesn't guarantee future returns. Always invest based on your risk capacity!

Would you like help creating a personalized investment portfolio?"""
            return response
        
        # Insurance
        if any(word in text_lower for word in ['insurance', 'life insurance', 'health insurance', 'term insurance', 'cover']):
            response['message'] = """**Insurance** protects you and your family from financial risks. Here's what you need:

**Types of Insurance:**

**1. Life Insurance:**
• **Term Insurance** (Recommended): Pure protection, low premium, high coverage
  - Coverage: 10-20 times annual income
  - Premium: Very affordable (e.g., ₹5,000/year for ₹1 crore cover)
  - Best for: Young earners with dependents
• **Whole Life/Endowment**: Combines insurance + savings (higher premium, lower coverage)
• **ULIP**: Market-linked, complex, usually expensive

**2. Health Insurance:**
• **Coverage**: ₹5-10 lakh minimum (₹1 crore+ for comprehensive)
• **Family Floater**: Covers entire family under one policy
• **Top-up/Super Top-up**: Additional coverage at low cost
• **Critical Illness**: Separate rider for major diseases

**3. Disability Insurance:**
• Protects income if you can't work
• Often overlooked but very important

**Insurance Needs by Life Stage:**
• **Single, No Dependents**: Basic health insurance
• **Married, No Kids**: Term + health insurance
• **With Kids**: Term (high coverage) + health (family) + disability
• **Near Retirement**: Health insurance becomes priority, term may reduce

**How Much Life Insurance?**
Rule of thumb: 10-15 times annual income + outstanding loans + children's education needs

**Common Mistakes:**
• Under-insuring (to save premium)
• Mixing insurance with investment (expensive)
• Not reviewing coverage regularly
• Relying only on employer insurance

**Tips:**
• Buy term insurance young (cheaper premiums)
• Health insurance: Buy early, cover increases over time
• Compare policies, read fine print
• Don't let policies lapse

**Remember**: Insurance is protection, not investment. Buy pure protection (term) and invest separately for better returns!

Would you like help calculating your insurance needs?"""
            return response
        
        # Real estate/Property
        if any(word in text_lower for word in ['property', 'real estate', 'home', 'house', 'buy house', 'rent vs buy']):
            response['message'] = """**Real Estate Decisions** are major financial choices. Here's what to consider:

**Rent vs Buy:**
• **Rent if**: Job location unstable, prices very high, not ready for commitment
• **Buy if**: Stable location, long-term plans, prices reasonable, ready for responsibilities

**Buying Property:**

**Financial Readiness:**
• **Down Payment**: Usually 20-30% of property value
• **Home Loan Eligibility**: 40-60% of income can go to EMI
• **Additional Costs**: Registration, stamp duty (5-8% of property value)
• **Maintenance**: Ongoing expenses (society charges, repairs, property tax)

**Affordability Rule:**
• EMI should not exceed 40% of monthly income
• Total debt (including home loan) should not exceed 50% of income
• Emergency fund: 6 months expenses (after buying)

**What to Check:**
• Legal documents (title, encumbrances)
• Builder reputation (if under construction)
• Location and future development
• Resale value potential
• Infrastructure (schools, hospitals, connectivity)

**Property as Investment:**
• Real estate returns: 6-8% historically (lower than equity)
• High entry cost, less liquid
• Rental yield: 2-4% typically
• Good for diversification, not for primary wealth building

**Tax Benefits:**
• **Section 24**: Up to ₹2 lakh deduction on home loan interest
• **Section 80C**: Principal repayment qualifies (up to ₹1.5 lakh)
• **Capital Gains**: Exemption available if reinvested in another property

**Red Flags:**
• Buying beyond affordability (EMI stress)
• Not considering all costs
• No emergency fund before buying
• Buying for short-term gains (not ideal)

**Tip**: Buy a home for living, not primarily as investment. For investment, consider REITs (Real Estate Investment Trusts) - more liquid and diversified.

Would you like help calculating home loan affordability?"""
            return response
        
        # Savings and money management
        if any(word in text_lower for word in ['save money', 'saving', 'money management', 'manage money', 'personal finance']):
            response['message'] = """**Personal Finance Management** is about making your money work for you. Here's a practical guide:

**The Foundation - Budget:**
• **Track Income & Expenses**: Know where your money goes
• **50/30/20 Rule**: 50% needs, 30% wants, 20% savings/investments
• **Zero-Based Budget**: Assign every rupee a purpose
• **Review Monthly**: Adjust as needed

**Savings Strategy:**
1. **Pay Yourself First**: Save before spending
2. **Automate Savings**: Set up auto-debit to investment accounts
3. **Emergency Fund First**: Build 6 months expenses before investing
4. **Then Invest**: Start SIPs, FDs based on goals

**Common Savings Tips:**
• **Reduce Unnecessary Expenses**: Cancel unused subscriptions
• **Cook at Home**: Saves significantly vs eating out
• **Buy Quality**: Spend more upfront, save on replacements
• **Compare Before Buying**: Use price comparison sites
• **Avoid Impulse Buying**: Wait 24-48 hours before big purchases
• **Use Credit Card Rewards**: But pay in full to avoid interest

**Goal-Based Planning:**
1. **Short-term Goals** (1-3 years): Vacation, car down payment
   - Use: FD, liquid funds, short-term debt funds
2. **Medium-term Goals** (3-7 years): Home down payment, education
   - Use: Hybrid funds, balanced portfolio, FDs
3. **Long-term Goals** (7+ years): Retirement, children's future
   - Use: Equity mutual funds, PPF, NPS, stocks

**Financial Health Checklist:**
✓ Emergency fund (6 months expenses)
✓ No high-interest debt (credit cards paid off)
✓ Adequate insurance (life + health)
✓ Systematic investments (SIPs)
✓ Retirement savings started
✓ Budget in place and followed
✓ Regular financial review

**The Power of Small Savings:**
Saving ₹5,000/month at 10% return:
• 10 years: ₹10.2 lakh
• 20 years: ₹38.2 lakh
• 30 years: ₹1.1 crore

**Key Principle**: Live below your means, invest the difference, let time and compound interest work!

Would you like help creating a savings plan for your goals?"""
            return response
        
        return None
    
    def understand_and_respond(self, text, text_lower):
        """Analyze query and provide contextual response even if topic not specifically matched"""
        # Extract keywords
        tokens = self.preprocess_text(text)
        
        # Financial keywords detected
        financial_keywords = ['money', 'finance', 'investment', 'save', 'loan', 'interest', 'bank', 
                           'fund', 'stock', 'market', 'wealth', 'income', 'expense', 'tax', 
                           'profit', 'return', 'gain', 'loss', 'capital', 'asset', 'liability']
        
        has_financial_context = any(keyword in text_lower for keyword in financial_keywords)
        
        if has_financial_context:
            # It's a financial question but we couldn't categorize it
            return f"""I understand you're asking about finances. While I don't have a specific answer to "{text}", let me help guide you:

**I can assist with:**
• **Explaining financial terms**: SIP, mutual funds, stocks, bonds, EMI, PPF, FD, etc.
• **Calculations**: EMI, SIP returns, compound interest, simple interest
• **Planning**: Retirement, emergency fund, tax saving, debt management
• **Advice**: Investment strategies, budgeting, insurance, real estate decisions

**Try asking:**
• "What is [term]?" - I'll explain any financial concept
• "How to [action]?" - Get step-by-step guidance
• "Calculate [type] for [amount] at [rate]%" - I'll do the math
• Or be more specific about what you'd like to know!

**Example questions:**
- "What is SIP?"
- "How to save tax?"
- "Calculate EMI for ₹50 lakhs at 8% for 20 years"
- "How to plan for retirement?"
- "Should I buy or rent a house?"

What specific financial topic would you like help with?"""
        else:
            # Not clearly financial - provide friendly guidance
            return f"""I'm your Financial Mentor and Advisor! I specialize in helping with all things related to money and finance.

**I can help you with:**
• Understanding financial terms and concepts (SIP, mutual funds, stocks, EMI, etc.)
• Financial calculations (EMI, SIP returns, interest calculations)
• Investment and savings strategies
• Retirement and financial planning
• Tax saving strategies
• Debt management
• Insurance planning
• Budgeting and money management

**Try asking me:**
• "What is SIP?" - Learn about financial concepts
• "How to save tax?" - Get practical advice
• "Calculate EMI for ₹30 lakhs at 7% for 15 years" - Get calculations
• "How to start investing?" - Get guidance
• Or any other financial question!

Feel free to ask me anything about personal finance, investments, savings, loans, or money management. I'm here to help! 💰"""
    
    def get_motivational_quote(self):
        """Get a random motivational quote"""
        return random.choice(self.motivational_quotes)

