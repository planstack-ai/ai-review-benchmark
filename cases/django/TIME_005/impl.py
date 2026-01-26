from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from myapp.models import Account, Transaction, MonthlyReport


class MonthEndProcessingService:
    """Service for handling month-end financial processing and reporting."""
    
    def __init__(self):
        self.processing_date = timezone.now().date()
        self.errors = []
    
    def process_month_end(self, target_date: Optional[date] = None) -> Dict[str, any]:
        """Execute complete month-end processing workflow."""
        if target_date:
            self.processing_date = target_date
        
        results = {
            'processed_accounts': 0,
            'total_balance': Decimal('0.00'),
            'reports_generated': 0,
            'errors': []
        }
        
        try:
            with transaction.atomic():
                accounts = self._get_active_accounts()
                results['processed_accounts'] = len(accounts)
                
                for account in accounts:
                    balance = self._calculate_month_end_balance(account)
                    results['total_balance'] += balance
                    self._create_month_end_entry(account, balance)
                
                next_month_date = self._get_next_month_date()
                report = self._generate_monthly_report(next_month_date)
                results['reports_generated'] = 1
                
                self._schedule_next_processing(next_month_date)
                
        except Exception as e:
            results['errors'].append(str(e))
            self.errors.append(f"Month-end processing failed: {e}")
        
        return results
    
    def _get_active_accounts(self) -> List[Account]:
        """Retrieve all active accounts for processing."""
        return Account.objects.filter(
            is_active=True,
            account_type__in=['CHECKING', 'SAVINGS', 'INVESTMENT']
        ).select_related('account_type')
    
    def _calculate_month_end_balance(self, account: Account) -> Decimal:
        """Calculate the final balance for an account at month end."""
        transactions = Transaction.objects.filter(
            account=account,
            transaction_date__month=self.processing_date.month,
            transaction_date__year=self.processing_date.year,
            is_processed=False
        )
        
        balance = account.current_balance
        for transaction in transactions:
            if transaction.transaction_type == 'CREDIT':
                balance += transaction.amount
            else:
                balance -= transaction.amount
            transaction.is_processed = True
            transaction.save()
        
        return balance
    
    def _create_month_end_entry(self, account: Account, balance: Decimal) -> None:
        """Create month-end balance entry for the account."""
        Transaction.objects.create(
            account=account,
            transaction_type='MONTH_END',
            amount=balance,
            transaction_date=self.processing_date,
            description=f"Month-end balance for {self.processing_date.strftime('%B %Y')}",
            is_processed=True
        )
        
        account.current_balance = balance
        account.last_processed_date = self.processing_date
        account.save()
    
    def _get_next_month_date(self) -> date:
        """Calculate the date for next month's processing."""
        current_month = self.processing_date.month
        current_year = self.processing_date.year
        current_day = self.processing_date.day
        
        if current_month == 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_month = current_month + 1
            next_year = current_year
        
        return self.processing_date.replace(month=next_month, year=next_year)
    
    def _generate_monthly_report(self, report_date: date) -> MonthlyReport:
        """Generate comprehensive monthly financial report."""
        total_accounts = Account.objects.filter(is_active=True).count()
        total_balance = sum(
            account.current_balance for account in Account.objects.filter(is_active=True)
        )
        
        report = MonthlyReport.objects.create(
            report_date=report_date,
            total_accounts=total_accounts,
            total_balance=total_balance,
            processing_date=self.processing_date,
            status='COMPLETED'
        )
        
        return report
    
    def _schedule_next_processing(self, next_date: date) -> None:
        """Schedule the next month-end processing job."""
        from myapp.tasks import schedule_month_end_processing
        schedule_month_end_processing.apply_async(
            args=[next_date.isoformat()],
            eta=timezone.make_aware(
                timezone.datetime.combine(next_date, timezone.datetime.min.time())
            )
        )