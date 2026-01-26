from decimal import Decimal
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class UserAccountService:
    """Service for managing user account operations and balance calculations."""
    
    def __init__(self):
        self.minimum_balance = Decimal('0.00')
        self.default_currency = 'USD'
    
    def create_user_account(self, user_id: int, initial_balance: Optional[Decimal] = None) -> 'UserAccount':
        """Create a new user account with optional initial balance."""
        from .models import UserAccount
        
        if initial_balance is None:
            initial_balance = Decimal('0.00')
        
        account_data = {
            'user_id': user_id,
            'balance': initial_balance,
            'currency': self.default_currency,
            'created_at': timezone.now(),
            'is_active': True
        }
        
        return self._create_account_record(account_data)
    
    def process_transaction(self, account_id: int, amount: Decimal, 
                          transaction_type: str) -> Dict[str, Any]:
        """Process a financial transaction for the given account."""
        from .models import UserAccount, Transaction
        
        with transaction.atomic():
            account = UserAccount.objects.select_for_update().get(id=account_id)
            
            if not self._validate_transaction(account, amount, transaction_type):
                raise ValidationError("Invalid transaction parameters")
            
            previous_balance = account.balance
            new_balance = self._calculate_new_balance(previous_balance, amount, transaction_type)
            
            account.balance = new_balance
            account.last_transaction_date = timezone.now()
            account.save()
            
            transaction_record = Transaction.objects.create(
                account=account,
                amount=amount,
                transaction_type=transaction_type,
                previous_balance=previous_balance,
                new_balance=new_balance,
                processed_at=timezone.now()
            )
            
            return self._format_transaction_response(transaction_record)
    
    def calculate_account_metrics(self, account_id: int) -> Dict[str, Any]:
        """Calculate various metrics for the user account."""
        from .models import UserAccount, Transaction
        
        account = UserAccount.objects.get(id=account_id)
        transactions = Transaction.objects.filter(account=account).order_by('-processed_at')
        
        total_deposits = self._calculate_total_by_type(transactions, 'deposit')
        total_withdrawals = self._calculate_total_by_type(transactions, 'withdrawal')
        transaction_count = transactions.count()
        
        return {
            'account_id': account_id,
            'current_balance': account.balance,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'transaction_count': transaction_count,
            'average_transaction_amount': self._calculate_average_transaction(transactions),
            'account_age_days': (timezone.now() - account.created_at).days
        }
    
    def _create_account_record(self, account_data: Dict[str, Any]) -> 'UserAccount':
        """Create the actual account record in the database."""
        from .models import UserAccount
        
        account = UserAccount.objects.create(**account_data)
        logger.info(f"Created new account {account.id} for user {account.user_id}")
        return account
    
    def _validate_transaction(self, account: 'UserAccount', amount: Decimal, 
                            transaction_type: str) -> bool:
        """Validate transaction parameters and account state."""
        if not account.is_active:
            return False
        
        if amount <= 0:
            return False
        
        if transaction_type == 'withdrawal' and account.balance < amount:
            return False
        
        return True
    
    def _calculate_new_balance(self, current_balance: Decimal, amount: Decimal, 
                             transaction_type: str) -> Decimal:
        """Calculate the new account balance after transaction."""
        if transaction_type == 'deposit':
            return current_balance + amount
        elif transaction_type == 'withdrawal':
            return current_balance - amount
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")
    
    def _calculate_total_by_type(self, transactions, transaction_type: str) -> Decimal:
        """Calculate total amount for specific transaction type."""
        filtered_transactions = transactions.filter(transaction_type=transaction_type)
        return sum(t.amount for t in filtered_transactions) or Decimal('0.00')
    
    def _calculate_average_transaction(self, transactions) -> Decimal:
        """Calculate average transaction amount."""
        if not transactions.exists():
            return Decimal('0.00')
        
        total_amount = sum(t.amount for t in transactions)
        return total_amount / transactions.count()
    
    def _format_transaction_response(self, transaction: 'Transaction') -> Dict[str, Any]:
        """Format transaction data for API response."""
        return {
            'transaction_id': transaction.id,
            'account_id': transaction.account.id,
            'amount': transaction.amount,
            'type': transaction.transaction_type,
            'previous_balance': transaction.previous_balance,
            'new_balance': transaction.new_balance,
            'processed_at': transaction.processed_at.isoformat()
        }