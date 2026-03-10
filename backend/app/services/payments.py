"""
Imoogle 5.0 Payment Service
Imoogle Pay - P2P transfers, deposits, withdrawals using Paystack.
Nigerian market focus with ImoCoin support.
"""

import httpx
import hashlib
import secrets
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.config import settings, SUBSCRIPTION_PLANS
from app.database.models import (
    User, Wallet, Transaction,
    TransactionType, TransactionStatus, UserTier,
)


class PaymentService:
    """
    Imoogle Pay service with:
    1. Wallet management
    2. P2P transfers between users
    3. Paystack deposits/withdrawals
    4. Subscription management
    5. ImoCoin virtual currency
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.paystack_base = "https://api.paystack.co"
        
        # Transaction fees (in percentage)
        self.transfer_fee_percent = 0  # Free P2P
        self.withdrawal_fee_flat = 5000  # 50 Naira in kobo
        
        # Limits (in kobo - 100 kobo = 1 Naira)
        self.min_deposit = 10000  # 100 Naira
        self.max_deposit = 100000000  # 1 Million Naira
        self.min_withdrawal = 50000  # 500 Naira
        self.min_transfer = 10000  # 100 Naira
        self.daily_transfer_limit = 50000000  # 500k Naira
    
    async def close(self):
        await self.http_client.aclose()
    
    def _get_paystack_headers(self) -> Dict[str, str]:
        """Get Paystack API headers."""
        return {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
    
    def _generate_reference(self, prefix: str = "IMO") -> str:
        """Generate unique transaction reference."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = secrets.token_hex(4).upper()
        return f"{prefix}-{timestamp}-{random_str}"
    
    def _hash_pin(self, pin: str) -> str:
        """Hash wallet PIN."""
        return hashlib.sha256(pin.encode()).hexdigest()
    
    def _verify_pin(self, pin: str, pin_hash: str) -> bool:
        """Verify wallet PIN."""
        return self._hash_pin(pin) == pin_hash
    
    # ==================== WALLET MANAGEMENT ====================
    
    async def get_or_create_wallet(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Wallet:
        """Get or create wallet for user."""
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0, imocoin_balance=0)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        
        return wallet
    
    async def get_balance(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """Get user's wallet balance."""
        wallet = await self.get_or_create_wallet(db, user_id)
        
        return {
            "balance_kobo": wallet.balance,
            "balance_naira": wallet.balance / 100,
            "balance_formatted": f"₦{wallet.balance / 100:,.2f}",
            "imocoin": wallet.imocoin_balance,
            "has_pin": wallet.pin_hash is not None,
        }
    
    async def set_wallet_pin(
        self,
        db: AsyncSession,
        user_id: int,
        pin: str,
    ) -> Dict[str, Any]:
        """Set or update wallet PIN."""
        if len(pin) != 4 or not pin.isdigit():
            return {"success": False, "error": "PIN must be exactly 4 digits"}
        
        wallet = await self.get_or_create_wallet(db, user_id)
        wallet.pin_hash = self._hash_pin(pin)
        wallet.pin_attempts = 0
        wallet.locked_until = None
        await db.commit()
        
        return {"success": True, "message": "PIN set successfully"}
    
    async def verify_wallet_pin(
        self,
        db: AsyncSession,
        user_id: int,
        pin: str,
    ) -> Tuple[bool, str]:
        """Verify wallet PIN with lockout protection."""
        wallet = await self.get_or_create_wallet(db, user_id)
        
        if not wallet.pin_hash:
            return False, "Please set a PIN first using /setpin"
        
        # Check if locked
        if wallet.locked_until and datetime.now() < wallet.locked_until:
            remaining = (wallet.locked_until - datetime.now()).seconds // 60
            return False, f"Wallet locked. Try again in {remaining} minutes."
        
        # Verify PIN
        if self._verify_pin(pin, wallet.pin_hash):
            wallet.pin_attempts = 0
            wallet.locked_until = None
            await db.commit()
            return True, "PIN verified"
        
        # Wrong PIN
        wallet.pin_attempts += 1
        if wallet.pin_attempts >= 3:
            wallet.locked_until = datetime.now() + timedelta(minutes=30)
            await db.commit()
            return False, "Too many wrong attempts. Wallet locked for 30 minutes."
        
        await db.commit()
        remaining = 3 - wallet.pin_attempts
        return False, f"Wrong PIN. {remaining} attempts remaining."
    
    # ==================== DEPOSITS ====================
    
    async def initialize_deposit(
        self,
        db: AsyncSession,
        user_id: int,
        amount_naira: float,
        email: str,
    ) -> Dict[str, Any]:
        """Initialize a deposit via Paystack."""
        if not settings.PAYSTACK_SECRET_KEY:
            return {"success": False, "error": "Payment system not configured"}
        
        amount_kobo = int(amount_naira * 100)
        
        if amount_kobo < self.min_deposit:
            return {"success": False, "error": f"Minimum deposit is ₦{self.min_deposit / 100}"}
        
        if amount_kobo > self.max_deposit:
            return {"success": False, "error": f"Maximum deposit is ₦{self.max_deposit / 100:,.0f}"}
        
        wallet = await self.get_or_create_wallet(db, user_id)
        reference = self._generate_reference("DEP")
        
        # Create transaction record
        transaction = Transaction(
            wallet_id=wallet.id,
            reference=reference,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.PENDING,
            amount=amount_kobo,
            description=f"Deposit of ₦{amount_naira:,.2f}",
        )
        db.add(transaction)
        await db.commit()
        
        # Initialize with Paystack
        try:
            response = await self.http_client.post(
                f"{self.paystack_base}/transaction/initialize",
                headers=self._get_paystack_headers(),
                json={
                    "email": email,
                    "amount": amount_kobo,
                    "reference": reference,
                    "callback_url": f"{settings.TELEGRAM_WEBHOOK_URL}/payment/callback",
                    "metadata": {
                        "user_id": user_id,
                        "wallet_id": wallet.id,
                        "type": "deposit",
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "reference": reference,
                    "amount": amount_naira,
                }
            else:
                return {"success": False, "error": data.get("message", "Payment initialization failed")}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def verify_deposit(
        self,
        db: AsyncSession,
        reference: str,
    ) -> Dict[str, Any]:
        """Verify and complete a deposit."""
        # Get transaction
        result = await db.execute(
            select(Transaction).where(Transaction.reference == reference)
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            return {"success": False, "error": "Transaction not found"}
        
        if transaction.status == TransactionStatus.COMPLETED:
            return {"success": True, "message": "Already processed"}
        
        # Verify with Paystack
        try:
            response = await self.http_client.get(
                f"{self.paystack_base}/transaction/verify/{reference}",
                headers=self._get_paystack_headers(),
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") and data["data"]["status"] == "success":
                # Credit wallet
                wallet = await db.get(Wallet, transaction.wallet_id)
                wallet.balance += transaction.amount
                
                # Update transaction
                transaction.status = TransactionStatus.COMPLETED
                transaction.completed_at = datetime.now()
                transaction.provider_reference = data["data"]["reference"]
                
                await db.commit()
                
                return {
                    "success": True,
                    "amount": transaction.amount / 100,
                    "new_balance": wallet.balance / 100,
                }
            else:
                transaction.status = TransactionStatus.FAILED
                await db.commit()
                return {"success": False, "error": "Payment verification failed"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== P2P TRANSFERS ====================
    
    async def transfer(
        self,
        db: AsyncSession,
        sender_user_id: int,
        recipient_username: str,
        amount_naira: float,
        pin: str,
        note: str = None,
    ) -> Dict[str, Any]:
        """Transfer money between users."""
        amount_kobo = int(amount_naira * 100)
        
        # Validate amount
        if amount_kobo < self.min_transfer:
            return {"success": False, "error": f"Minimum transfer is ₦{self.min_transfer / 100}"}
        
        # Verify sender PIN
        pin_valid, pin_msg = await self.verify_wallet_pin(db, sender_user_id, pin)
        if not pin_valid:
            return {"success": False, "error": pin_msg}
        
        # Get sender wallet
        sender_wallet = await self.get_or_create_wallet(db, sender_user_id)
        
        # Check balance
        if sender_wallet.balance < amount_kobo:
            return {"success": False, "error": "Insufficient balance"}
        
        # Find recipient by username
        result = await db.execute(
            select(User).where(User.username == recipient_username.lstrip("@"))
        )
        recipient = result.scalar_one_or_none()
        
        if not recipient:
            return {"success": False, "error": f"User @{recipient_username} not found"}
        
        if recipient.id == sender_user_id:
            return {"success": False, "error": "You cannot transfer to yourself"}
        
        recipient_wallet = await self.get_or_create_wallet(db, recipient.id)
        
        # Create transaction
        reference = self._generate_reference("TRF")
        
        transaction = Transaction(
            wallet_id=sender_wallet.id,
            reference=reference,
            type=TransactionType.TRANSFER,
            status=TransactionStatus.COMPLETED,
            amount=amount_kobo,
            recipient_wallet_id=recipient_wallet.id,
            description=note or f"Transfer to @{recipient_username}",
            completed_at=datetime.now(),
        )
        
        # Update balances
        sender_wallet.balance -= amount_kobo
        recipient_wallet.balance += amount_kobo
        
        db.add(transaction)
        await db.commit()
        
        return {
            "success": True,
            "amount": amount_naira,
            "recipient": recipient_username,
            "sender_balance": sender_wallet.balance / 100,
            "reference": reference,
        }
    
    # ==================== WITHDRAWALS ====================
    
    async def initialize_withdrawal(
        self,
        db: AsyncSession,
        user_id: int,
        amount_naira: float,
        bank_code: str,
        account_number: str,
        pin: str,
    ) -> Dict[str, Any]:
        """Initialize withdrawal to bank account."""
        amount_kobo = int(amount_naira * 100)
        total_amount = amount_kobo + self.withdrawal_fee_flat
        
        # Validate amount
        if amount_kobo < self.min_withdrawal:
            return {"success": False, "error": f"Minimum withdrawal is ₦{self.min_withdrawal / 100}"}
        
        # Verify PIN
        pin_valid, pin_msg = await self.verify_wallet_pin(db, user_id, pin)
        if not pin_valid:
            return {"success": False, "error": pin_msg}
        
        wallet = await self.get_or_create_wallet(db, user_id)
        
        # Check balance (amount + fee)
        if wallet.balance < total_amount:
            return {"success": False, "error": f"Insufficient balance. You need ₦{total_amount / 100:,.2f} (including ₦{self.withdrawal_fee_flat / 100} fee)"}
        
        # Verify bank account with Paystack
        try:
            verify_response = await self.http_client.get(
                f"{self.paystack_base}/bank/resolve",
                headers=self._get_paystack_headers(),
                params={"account_number": account_number, "bank_code": bank_code},
            )
            verify_data = verify_response.json()
            
            if not verify_data.get("status"):
                return {"success": False, "error": "Could not verify bank account"}
            
            account_name = verify_data["data"]["account_name"]
            
            # Create transfer recipient
            recipient_response = await self.http_client.post(
                f"{self.paystack_base}/transferrecipient",
                headers=self._get_paystack_headers(),
                json={
                    "type": "nuban",
                    "name": account_name,
                    "account_number": account_number,
                    "bank_code": bank_code,
                    "currency": "NGN",
                },
            )
            recipient_data = recipient_response.json()
            
            if not recipient_data.get("status"):
                return {"success": False, "error": "Could not create transfer recipient"}
            
            recipient_code = recipient_data["data"]["recipient_code"]
            
            # Create transaction record
            reference = self._generate_reference("WDR")
            
            transaction = Transaction(
                wallet_id=wallet.id,
                reference=reference,
                type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.PENDING,
                amount=amount_kobo,
                fee=self.withdrawal_fee_flat,
                description=f"Withdrawal to {account_name}",
                metadata={
                    "bank_code": bank_code,
                    "account_number": account_number,
                    "account_name": account_name,
                    "recipient_code": recipient_code,
                },
            )
            db.add(transaction)
            
            # Debit wallet
            wallet.balance -= total_amount
            await db.commit()
            
            # Initiate transfer
            transfer_response = await self.http_client.post(
                f"{self.paystack_base}/transfer",
                headers=self._get_paystack_headers(),
                json={
                    "source": "balance",
                    "amount": amount_kobo,
                    "recipient": recipient_code,
                    "reference": reference,
                    "reason": "Imoogle Pay Withdrawal",
                },
            )
            transfer_data = transfer_response.json()
            
            if transfer_data.get("status"):
                return {
                    "success": True,
                    "amount": amount_naira,
                    "fee": self.withdrawal_fee_flat / 100,
                    "account_name": account_name,
                    "reference": reference,
                    "message": "Withdrawal initiated. You'll receive your money shortly.",
                }
            else:
                # Refund on failure
                wallet.balance += total_amount
                transaction.status = TransactionStatus.FAILED
                await db.commit()
                return {"success": False, "error": transfer_data.get("message", "Transfer failed")}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== SUBSCRIPTIONS ====================
    
    async def subscribe(
        self,
        db: AsyncSession,
        user_id: int,
        plan: str,
        pin: str,
    ) -> Dict[str, Any]:
        """Subscribe user to a plan using wallet balance."""
        if plan not in SUBSCRIPTION_PLANS:
            return {"success": False, "error": "Invalid plan"}
        
        plan_details = SUBSCRIPTION_PLANS[plan]
        amount_kobo = plan_details["price"] * 100
        
        if amount_kobo == 0:
            # Free plan
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(tier=UserTier(plan), subscription_expires=None)
            )
            await db.commit()
            return {"success": True, "plan": plan, "message": "Switched to free plan"}
        
        # Verify PIN
        pin_valid, pin_msg = await self.verify_wallet_pin(db, user_id, pin)
        if not pin_valid:
            return {"success": False, "error": pin_msg}
        
        wallet = await self.get_or_create_wallet(db, user_id)
        
        # Check balance
        if wallet.balance < amount_kobo:
            return {"success": False, "error": f"Insufficient balance. You need ₦{amount_kobo / 100:,.0f}"}
        
        # Debit wallet
        wallet.balance -= amount_kobo
        
        # Update subscription
        expires = datetime.now() + timedelta(days=30)
        
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(tier=UserTier(plan), subscription_expires=expires)
        )
        
        # Create transaction
        transaction = Transaction(
            wallet_id=wallet.id,
            reference=self._generate_reference("SUB"),
            type=TransactionType.SUBSCRIPTION,
            status=TransactionStatus.COMPLETED,
            amount=amount_kobo,
            description=f"{plan_details['name']} Plan Subscription",
            completed_at=datetime.now(),
        )
        db.add(transaction)
        await db.commit()
        
        return {
            "success": True,
            "plan": plan,
            "expires": expires.strftime("%Y-%m-%d"),
            "features": plan_details,
        }
    
    async def get_transaction_history(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> list[Dict[str, Any]]:
        """Get user's transaction history."""
        wallet = await self.get_or_create_wallet(db, user_id)
        
        result = await db.execute(
            select(Transaction)
            .where(Transaction.wallet_id == wallet.id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        transactions = result.scalars().all()
        
        return [
            {
                "reference": t.reference,
                "type": t.type.value,
                "status": t.status.value,
                "amount": t.amount / 100,
                "fee": (t.fee or 0) / 100,
                "description": t.description,
                "date": t.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for t in transactions
        ]
    
    def format_balance(
        self,
        balance_data: Dict[str, Any],
        use_pidgin: bool = False,
    ) -> str:
        """Format balance for display."""
        if use_pidgin:
            return f"""💰 **Your Imoogle Pay Balance**

Naira: **{balance_data['balance_formatted']}**
ImoCoin: **{balance_data['imocoin']} IMC**

{"You never set PIN o. Use /setpin to secure your wallet." if not balance_data['has_pin'] else "Your wallet dey secure with PIN."}"""
        else:
            return f"""💰 **Your Imoogle Pay Balance**

Naira: **{balance_data['balance_formatted']}**
ImoCoin: **{balance_data['imocoin']} IMC**

{"You haven't set a PIN yet. Use /setpin to secure your wallet." if not balance_data['has_pin'] else "Your wallet is secured with PIN."}"""


# Singleton instance
payment_service = PaymentService()
