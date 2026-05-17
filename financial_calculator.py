"""
Financial Calculator Module
Handles calculations for savings, investments, interest, and EMI
"""
import math

class FinancialCalculator:
    @staticmethod
    def calculate_emi(principal, rate, tenure_months):
        """
        Calculate Equated Monthly Installment (EMI)
        principal: Loan amount
        rate: Annual interest rate (percentage)
        tenure_months: Loan tenure in months
        """
        if rate == 0:
            return principal / tenure_months
        
        monthly_rate = rate / (12 * 100)
        emi = principal * monthly_rate * (pow(1 + monthly_rate, tenure_months)) / (pow(1 + monthly_rate, tenure_months) - 1)
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
        
        return {
            'emi': round(emi, 2),
            'total_payment': round(total_payment, 2),
            'total_interest': round(total_interest, 2),
            'principal': principal,
            'rate': rate,
            'tenure_months': tenure_months
        }
    
    @staticmethod
    def calculate_compound_interest(principal, rate, time_years, compounding_frequency=12):
        """
        Calculate compound interest
        principal: Initial amount
        rate: Annual interest rate (percentage)
        time_years: Time period in years
        compounding_frequency: Number of times interest is compounded per year (default: 12 for monthly)
        """
        rate_decimal = rate / 100
        amount = principal * pow(1 + rate_decimal / compounding_frequency, compounding_frequency * time_years)
        interest_earned = amount - principal
        
        return {
            'principal': principal,
            'rate': rate,
            'time_years': time_years,
            'compounding_frequency': compounding_frequency,
            'maturity_amount': round(amount, 2),
            'interest_earned': round(interest_earned, 2)
        }
    
    @staticmethod
    def calculate_simple_interest(principal, rate, time_years):
        """
        Calculate simple interest
        principal: Initial amount
        rate: Annual interest rate (percentage)
        time_years: Time period in years
        """
        interest = (principal * rate * time_years) / 100
        total_amount = principal + interest
        
        return {
            'principal': principal,
            'rate': rate,
            'time_years': time_years,
            'interest': round(interest, 2),
            'total_amount': round(total_amount, 2)
        }
    
    @staticmethod
    def calculate_sip(monthly_investment, rate, time_years):
        """
        Calculate Systematic Investment Plan (SIP) returns
        monthly_investment: Monthly investment amount
        rate: Expected annual return rate (percentage)
        time_years: Investment period in years
        """
        months = time_years * 12
        monthly_rate = rate / (12 * 100)
        
        if monthly_rate == 0:
            maturity_amount = monthly_investment * months
        else:
            maturity_amount = monthly_investment * (((pow(1 + monthly_rate, months) - 1) / monthly_rate) * (1 + monthly_rate))
        
        total_invested = monthly_investment * months
        gains = maturity_amount - total_invested
        
        return {
            'monthly_investment': monthly_investment,
            'rate': rate,
            'time_years': time_years,
            'total_invested': round(total_invested, 2),
            'maturity_amount': round(maturity_amount, 2),
            'gains': round(gains, 2),
            'return_percentage': round((gains / total_invested) * 100, 2) if total_invested > 0 else 0
        }
    
    @staticmethod
    def calculate_future_value(principal, rate, time_years, monthly_contribution=0):
        """
        Calculate future value with optional monthly contributions
        principal: Initial amount
        rate: Annual interest rate (percentage)
        time_years: Time period in years
        monthly_contribution: Optional monthly contribution amount
        """
        # Calculate future value of principal
        principal_fv = principal * pow(1 + rate / 100, time_years)
        
        # Calculate future value of monthly contributions
        if monthly_contribution > 0:
            months = time_years * 12
            monthly_rate = rate / (12 * 100)
            if monthly_rate == 0:
                contributions_fv = monthly_contribution * months
            else:
                contributions_fv = monthly_contribution * (((pow(1 + monthly_rate, months) - 1) / monthly_rate))
        else:
            contributions_fv = 0
        
        total_fv = principal_fv + contributions_fv
        
        return {
            'principal': principal,
            'monthly_contribution': monthly_contribution,
            'rate': rate,
            'time_years': time_years,
            'principal_future_value': round(principal_fv, 2),
            'contributions_future_value': round(contributions_fv, 2),
            'total_future_value': round(total_fv, 2)
        }

